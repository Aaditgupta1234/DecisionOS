"""Unit tests for LLM Provider abstraction and implementations."""

import pytest

from app.ai_insights.providers import MockLLMProvider, OpenAIProvider, get_llm_provider


@pytest.mark.anyio
async def test_mock_llm_provider_execution():
    """Verifies that MockLLMProvider returns valid text, JSON schemas, and passes health checks."""
    provider = MockLLMProvider()
    assert provider.provider_name == "mock"
    assert await provider.health_check() is True

    # Text generation
    text = await provider.generate_text("Summarize revenue")
    assert isinstance(text, str)
    assert len(text) > 20

    # JSON generation for narrative
    narrative_json = await provider.generate_json("generate executive_narrative")
    assert "headline" in narrative_json
    assert "executive_summary" in narrative_json

    # JSON generation for risks
    risk_json = await provider.generate_json("generate risk_analysis")
    assert "overall_risk_level" in risk_json
    assert len(risk_json["top_risks"]) >= 1


@pytest.mark.anyio
async def test_openai_provider_fallback():
    """Verifies that OpenAIProvider degrades gracefully to MockProvider when unconfigured."""
    provider = OpenAIProvider(api_key="sk-placeholder-test")
    assert provider.provider_name == "openai"
    assert await provider.health_check() is True

    # Calls should succeed via fallback
    json_res = await provider.generate_json("generate executive_narrative")
    assert "headline" in json_res


from app.ai_insights.providers import (
    BaseLLMProvider,
    MockLLMProvider,
    OllamaProvider,
    OpenAIProvider,
    get_llm_provider,
)


def test_get_llm_provider_factory():
    """Verifies provider factory selection for all supported providers."""
    p_mock = get_llm_provider("mock")
    assert isinstance(p_mock, MockLLMProvider)

    p_openai = get_llm_provider("openai")
    assert isinstance(p_openai, OpenAIProvider)

    p_ollama = get_llm_provider("ollama")
    assert isinstance(p_ollama, OllamaProvider)

    p_default = get_llm_provider()
    assert isinstance(p_default, BaseLLMProvider)

