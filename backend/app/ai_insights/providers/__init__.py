"""LLM Providers package for DecisionOS AI Insights."""

from typing import Optional
from app.ai_insights.constants import DEFAULT_MODEL_NAME, PROVIDER_MOCK, PROVIDER_OPENAI
from app.ai_insights.providers.base_llm_provider import BaseLLMProvider
from app.ai_insights.providers.mock_provider import MockLLMProvider
from app.ai_insights.providers.openai_provider import OpenAIProvider


def get_llm_provider(
    provider_name: Optional[str] = None,
    model_name: Optional[str] = None,
) -> BaseLLMProvider:
    """
    Factory function returning configured BaseLLMProvider instance.
    """
    p_name = (provider_name or PROVIDER_OPENAI).lower()
    m_name = model_name or DEFAULT_MODEL_NAME

    if p_name == PROVIDER_MOCK:
        return MockLLMProvider(model_name=m_name)

    # Default to OpenAI with automatic fallback
    return OpenAIProvider(model_name=m_name)


__all__ = [
    "BaseLLMProvider",
    "MockLLMProvider",
    "OpenAIProvider",
    "get_llm_provider",
]
