"""AI Provider Layer management and diagnostic endpoints."""

import time
from typing import Any, Optional
from fastapi import APIRouter, Depends, Query, status

from app.ai_insights.constants import (
    DEFAULT_MODEL_NAME,
    PROVIDER_MOCK,
    PROVIDER_OLLAMA,
    PROVIDER_OPENAI,
)
from app.ai_insights.providers import get_llm_provider
from app.api.dependencies.auth import get_current_active_user
from app.core.config import settings
from app.models.user import User
from app.schemas.ai import (
    AIHealthResponse,
    AIProviderInfo,
    AIProvidersResponse,
    AITestRequest,
    AITestResponse,
)
from app.schemas.base import SuccessResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=SuccessResponse[AIHealthResponse],
    summary="AI Provider Health Check",
    tags=["AI Provider Layer"],
)
async def get_ai_health(
    provider: Optional[str] = Query(None, description="Optional provider override (e.g. 'ollama', 'mock', 'openai')"),
    model: Optional[str] = Query(None, description="Optional model override"),
) -> Any:
    """
    Queries the configured or specified AI provider to determine:
    1. Daemon/API reachability
    2. Model availability / installation status
    3. Round-trip latency in milliseconds
    4. Discovered model tags
    """
    llm = get_llm_provider(provider_name=provider, model_name=model)
    start_ts = time.monotonic()
    is_healthy = await llm.health_check()
    latency = round((time.monotonic() - start_ts) * 1000, 2)
    models = await llm.list_models() if is_healthy else []

    data = AIHealthResponse(
        provider=llm.provider_name,
        model=llm.model_name,
        status="healthy" if is_healthy else "unhealthy",
        latency_ms=latency,
        available_models=models,
    )
    return SuccessResponse(
        message=f"AI provider '{llm.provider_name}' status: {data.status}.",
        data=data,
    )


@router.get(
    "/providers",
    response_model=SuccessResponse[AIProvidersResponse],
    summary="List Supported AI Providers",
    tags=["AI Provider Layer"],
)
async def list_ai_providers() -> Any:
    """
    Returns catalog of supported AI providers, the currently configured active provider,
    and supported model specifications.
    """
    active = settings.AI_PROVIDER.lower()
    providers = [
        AIProviderInfo(
            name=PROVIDER_OLLAMA,
            description="Local offline LLM inference via Ollama (e.g. Qwen 2.5 1.5B)",
            is_active=(active == PROVIDER_OLLAMA),
            default_model=settings.OLLAMA_MODEL,
            supported_models=["qwen2.5:1.5b", "llama3.2:1b", "llama3.2:3b", "mistral:7b"],
        ),
        AIProviderInfo(
            name=PROVIDER_MOCK,
            description="Deterministic Mock LLM Provider for offline execution, CI/CD, and fallback",
            is_active=(active == PROVIDER_MOCK),
            default_model="mock-decision-v1",
            supported_models=["mock-decision-v1"],
        ),
        AIProviderInfo(
            name=PROVIDER_OPENAI,
            description="Cloud-hosted OpenAI API with structured JSON output and automatic fallback",
            is_active=(active == PROVIDER_OPENAI),
            default_model="gpt-4o-mini",
            supported_models=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        ),
    ]

    active_model = settings.OLLAMA_MODEL if active == PROVIDER_OLLAMA else DEFAULT_MODEL_NAME

    data = AIProvidersResponse(
        active_provider=active,
        active_model=active_model,
        providers=providers,
    )
    return SuccessResponse(
        message="AI providers retrieved successfully.",
        data=data,
    )


@router.post(
    "/test",
    response_model=SuccessResponse[AITestResponse],
    status_code=status.HTTP_200_OK,
    summary="Execute Test AI Generation",
    tags=["AI Provider Layer"],
)
async def test_ai_generation(
    payload: AITestRequest,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Executes a direct test prompt through the AI Provider Layer.
    Requires authenticated user.
    """
    llm = get_llm_provider(provider_name=payload.provider, model_name=payload.model)
    start_ts = time.monotonic()

    text = await llm.generate_text(
        prompt=payload.prompt,
        system_prompt=payload.system_prompt,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
    )
    latency = round((time.monotonic() - start_ts) * 1000, 2)

    data = AITestResponse(
        generated_text=text,
        provider=llm.provider_name,
        model=llm.model_name,
        latency_ms=latency,
    )
    return SuccessResponse(
        message="AI test generation completed successfully.",
        data=data,
    )

