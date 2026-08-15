"""Comprehensive unit and integration tests for Phase 9.1 Ollama Provider Layer."""

import json
from unittest.mock import AsyncMock, patch
import httpx
import pytest

from app.ai_insights.constants import PROVIDER_MOCK, PROVIDER_OLLAMA, PROVIDER_OPENAI
from app.ai_insights.providers import (
    MockLLMProvider,
    OllamaProvider,
    OpenAIProvider,
    get_llm_provider,
)
from app.ai_insights.providers.exceptions import (
    OllamaConnectionError,
    OllamaInvalidResponseError,
    OllamaModelNotFoundError,
    OllamaTimeoutError,
)


@pytest.fixture
def ollama_provider():
    """Returns an OllamaProvider instance targeting test base URL."""
    return OllamaProvider(
        base_url="http://localhost:11434",
        model_name="qwen2.5:1.5b",
        timeout=10,
    )


# ---------------------------------------------------------------------------
# 1. Unit & Initialization Tests
# ---------------------------------------------------------------------------

def test_ollama_provider_properties(ollama_provider):
    """Verifies provider name and model name identity properties."""
    assert ollama_provider.provider_name == PROVIDER_OLLAMA
    assert ollama_provider.model_name == "qwen2.5:1.5b"


# ---------------------------------------------------------------------------
# 2. Text Generation Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_generate_text_success(ollama_provider):
    """Verifies successful completion extraction from Ollama response."""
    mock_response_payload = {
        "model": "qwen2.5:1.5b",
        "response": "Revenue increased by 15% due to higher customer retention in Q1.",
        "done": True,
    }

    with patch.object(ollama_provider, "_post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response_payload
        result = await ollama_provider.generate_text(
            prompt="Analyze Q1 revenue trend.",
            system_prompt="You are a senior financial analyst.",
            temperature=0.3,
            max_tokens=500,
        )

        assert isinstance(result, str)
        assert "Revenue increased by 15%" in result
        mock_post.assert_called_once()
        call_args = mock_post.call_args[0]
        assert call_args[0] == "/api/generate"
        assert call_args[1]["model"] == "qwen2.5:1.5b"
        assert call_args[1]["prompt"] == "Analyze Q1 revenue trend."
        assert call_args[1]["system"] == "You are a senior financial analyst."
        assert call_args[1]["options"]["temperature"] == 0.3
        assert call_args[1]["options"]["num_predict"] == 500


@pytest.mark.anyio
async def test_generate_text_timeout_error(ollama_provider):
    """Verifies that httpx.TimeoutException maps to OllamaTimeoutError."""
    with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Request timed out")):
        with pytest.raises(OllamaTimeoutError) as exc_info:
            await ollama_provider.generate_text("Prompt that times out")
        assert "timed out" in str(exc_info.value).lower()


@pytest.mark.anyio
async def test_generate_text_connection_error(ollama_provider):
    """Verifies that httpx.ConnectError maps to OllamaConnectionError."""
    with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("Connection refused")):
        with pytest.raises(OllamaConnectionError) as exc_info:
            await ollama_provider.generate_text("Prompt with no daemon running")
        assert "cannot connect to ollama" in str(exc_info.value).lower()


@pytest.mark.anyio
async def test_generate_text_model_not_found_404(ollama_provider):
    """Verifies that HTTP 404 for missing model maps to OllamaModelNotFoundError."""
    mock_req = httpx.Request("POST", "http://localhost:11434/api/generate")
    mock_resp = httpx.Response(404, text="model 'qwen2.5:1.5b' not found, try pulling it first", request=mock_req)
    http_err = httpx.HTTPStatusError("Not Found", request=mock_req, response=mock_resp)

    with patch("httpx.AsyncClient.post", side_effect=http_err):
        with pytest.raises(OllamaModelNotFoundError) as exc_info:
            await ollama_provider.generate_text("Prompt on missing model")
        assert "not installed" in str(exc_info.value).lower()


@pytest.mark.anyio
async def test_generate_text_invalid_response(ollama_provider):
    """Verifies that non-string response payloads raise OllamaInvalidResponseError."""
    with patch.object(ollama_provider, "_post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = {"response": 12345}  # invalid non-str
        with pytest.raises(OllamaInvalidResponseError):
            await ollama_provider.generate_text("Prompt expecting string")


# ---------------------------------------------------------------------------
# 3. Structured JSON Generation Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_generate_json_success(ollama_provider):
    """Verifies valid JSON response parsing."""
    mock_json_content = {"headline": "Strong Performance", "confidence_score": 0.92}
    with patch.object(ollama_provider, "_post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = {"response": json.dumps(mock_json_content)}
        result = await ollama_provider.generate_json("Generate JSON analysis")

        assert isinstance(result, dict)
        assert result["headline"] == "Strong Performance"
        assert result["confidence_score"] == 0.92


@pytest.mark.anyio
async def test_generate_json_with_markdown_fences(ollama_provider):
    """Verifies markdown code fence stripping before JSON parsing."""
    raw_markdown_output = "```json\n{\n  \"action\": \"expand_marketing\",\n  \"priority\": \"high\"\n}\n```"
    with patch.object(ollama_provider, "_post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = {"response": raw_markdown_output}
        result = await ollama_provider.generate_json("Generate fenced JSON")

        assert isinstance(result, dict)
        assert result["action"] == "expand_marketing"
        assert result["priority"] == "high"


@pytest.mark.anyio
async def test_generate_json_malformed_raises_error(ollama_provider):
    """Verifies that unparseable JSON output raises OllamaInvalidResponseError."""
    with patch.object(ollama_provider, "_post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = {"response": "This is free-form text, not JSON at all!"}
        with pytest.raises(OllamaInvalidResponseError) as exc_info:
            await ollama_provider.generate_json("Generate bad JSON")
        assert "non-json output" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# 4. Health Check & Model Discovery Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_health_check_healthy(ollama_provider):
    """Verifies health_check returns True when daemon responds and model is present."""
    mock_tags = {
        "models": [
            {"name": "qwen2.5:1.5b", "size": 986000000},
            {"name": "llama3.2:1b", "size": 1200000000},
        ]
    }
    with patch.object(ollama_provider, "_get_tags", new_callable=AsyncMock) as mock_tags_call:
        mock_tags_call.return_value = mock_tags
        healthy = await ollama_provider.health_check()
        assert healthy is True


@pytest.mark.anyio
async def test_health_check_model_missing(ollama_provider):
    """Verifies health_check returns False when daemon is up but configured model is missing."""
    mock_tags = {
        "models": [
            {"name": "mistral:7b", "size": 4100000000},
        ]
    }
    with patch.object(ollama_provider, "_get_tags", new_callable=AsyncMock) as mock_tags_call:
        mock_tags_call.return_value = mock_tags
        healthy = await ollama_provider.health_check()
        assert healthy is False


@pytest.mark.anyio
async def test_health_check_unreachable(ollama_provider):
    """Verifies health_check returns False gracefully when daemon is unreachable."""
    with patch.object(ollama_provider, "_get_tags", side_effect=OllamaConnectionError("Unreachable")):
        healthy = await ollama_provider.health_check()
        assert healthy is False


@pytest.mark.anyio
async def test_list_models_success(ollama_provider):
    """Verifies list_models queries tags and returns sorted model name list."""
    mock_tags = {
        "models": [
            {"name": "qwen2.5:1.5b"},
            {"name": "llama3.2:1b"},
            {"name": "deepseek-r1:1.5b"},
        ]
    }
    with patch.object(ollama_provider, "_get_tags", new_callable=AsyncMock) as mock_tags_call:
        mock_tags_call.return_value = mock_tags
        models = await ollama_provider.list_models()
        assert models == ["deepseek-r1:1.5b", "llama3.2:1b", "qwen2.5:1.5b"]


@pytest.mark.anyio
async def test_list_models_unreachable_returns_empty(ollama_provider):
    """Verifies list_models returns empty list without raising when daemon is down."""
    with patch.object(ollama_provider, "_get_tags", side_effect=OllamaConnectionError("Down")):
        models = await ollama_provider.list_models()
        assert models == []


# ---------------------------------------------------------------------------
# 5. Provider Factory Resolution Tests
# ---------------------------------------------------------------------------

def test_provider_factory_resolution():
    """Verifies that get_llm_provider instantiates the correct concrete class."""
    p_ollama = get_llm_provider(PROVIDER_OLLAMA)
    assert isinstance(p_ollama, OllamaProvider)
    assert p_ollama.provider_name == PROVIDER_OLLAMA

    p_mock = get_llm_provider(PROVIDER_MOCK)
    assert isinstance(p_mock, MockLLMProvider)
    assert p_mock.provider_name == PROVIDER_MOCK

    p_openai = get_llm_provider(PROVIDER_OPENAI)
    assert isinstance(p_openai, OpenAIProvider)
    assert p_openai.provider_name == PROVIDER_OPENAI


# ---------------------------------------------------------------------------
# 6. Base Provider list_models() Contract on Mock & OpenAI
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_mock_provider_list_models():
    """Verifies MockLLMProvider implements list_models() contract."""
    mock_p = MockLLMProvider(model_name="test-mock-model")
    models = await mock_p.list_models()
    assert models == ["test-mock-model"]


@pytest.mark.anyio
async def test_openai_provider_list_models():
    """Verifies OpenAIProvider implements list_models() contract."""
    openai_p = OpenAIProvider()
    models = await openai_p.list_models()
    assert "gpt-4o-mini" in models
    assert "gpt-4o" in models


# ---------------------------------------------------------------------------
# 7. FastAPI AI Endpoints Tests
# ---------------------------------------------------------------------------

def test_ai_health_endpoint(client):
    """Verifies GET /api/v1/ai/health returns expected schema structure."""
    response = client.get("/api/v1/ai/health?provider=mock")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["provider"] == "mock"
    assert data["data"]["status"] == "healthy"
    assert "latency_ms" in data["data"]
    assert isinstance(data["data"]["available_models"], list)


def test_ai_providers_endpoint(client):
    """Verifies GET /api/v1/ai/providers returns provider catalog."""
    response = client.get("/api/v1/ai/providers")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    providers = data["data"]["providers"]
    names = [p["name"] for p in providers]
    assert "ollama" in names
    assert "mock" in names
    assert "openai" in names


def test_ai_test_endpoint_authenticated(client, analyst_headers):
    """Verifies POST /api/v1/ai/test executes test inference for authenticated users."""
    payload = {
        "prompt": "Summarize customer churn findings",
        "provider": "mock",
        "temperature": 0.2,
        "max_tokens": 500,
    }
    response = client.post("/api/v1/ai/test", json=payload, headers=analyst_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["generated_text"]) > 10
    assert data["data"]["provider"] == "mock"
    assert "latency_ms" in data["data"]


def test_ai_test_endpoint_unauthorized(client):
    """Verifies POST /api/v1/ai/test requires authentication."""
    payload = {"prompt": "Summarize customer churn"}
    response = client.post("/api/v1/ai/test", json=payload)
    assert response.status_code == 401

