"""LLM Providers package for DecisionOS AI Insights."""

from typing import Optional
from app.ai_insights.constants import (
    DEFAULT_MODEL_NAME,
    PROVIDER_MOCK,
    PROVIDER_OLLAMA,
    PROVIDER_OPENAI,
)
from app.ai_insights.providers.base_llm_provider import BaseLLMProvider
from app.ai_insights.providers.mock_provider import MockLLMProvider
from app.ai_insights.providers.ollama_provider import OllamaProvider
from app.ai_insights.providers.openai_provider import OpenAIProvider
from app.core.config import settings


def get_llm_provider(
    provider_name: Optional[str] = None,
    model_name: Optional[str] = None,
) -> BaseLLMProvider:
    """
    Factory function returning configured BaseLLMProvider instance.
    Defaults to settings.AI_PROVIDER when provider_name is not explicitly passed.
    """
    p_name = (provider_name or settings.AI_PROVIDER).lower()

    if p_name == PROVIDER_OLLAMA:
        m_name = model_name or settings.OLLAMA_MODEL
        return OllamaProvider(
            base_url=settings.OLLAMA_BASE_URL,
            model_name=m_name,
            timeout=settings.OLLAMA_TIMEOUT,
        )

    if p_name == PROVIDER_MOCK:
        m_name = model_name or DEFAULT_MODEL_NAME
        return MockLLMProvider(model_name=m_name)

    # Default to OpenAI with automatic fallback
    m_name = model_name or DEFAULT_MODEL_NAME
    return OpenAIProvider(model_name=m_name)


__all__ = [
    "BaseLLMProvider",
    "MockLLMProvider",
    "OllamaProvider",
    "OpenAIProvider",
    "get_llm_provider",
]

