"""DecisionOS AI Insights & Executive Narrative Layer package."""

from app.ai_insights.constants import (
    DEFAULT_MODEL_NAME,
    DEFAULT_MODEL_PROVIDER,
    INSIGHT_VERSION,
    PROMPT_VERSION,
    PROVIDER_MOCK,
    PROVIDER_OLLAMA,
    PROVIDER_OPENAI,
    REPORT_VERSION,
)
from app.ai_insights.providers import (
    BaseLLMProvider,
    MockLLMProvider,
    OllamaProvider,
    OpenAIProvider,
    get_llm_provider,
)
from app.ai_insights.services.ai_insight_manager import AIInsightManager
from app.ai_insights.services.ai_insight_service import AIInsightService

__all__ = [
    "BaseLLMProvider",
    "MockLLMProvider",
    "OllamaProvider",
    "OpenAIProvider",
    "get_llm_provider",
    "AIInsightManager",
    "AIInsightService",
    "INSIGHT_VERSION",
    "PROMPT_VERSION",
    "REPORT_VERSION",
    "DEFAULT_MODEL_PROVIDER",
    "DEFAULT_MODEL_NAME",
    "PROVIDER_OPENAI",
    "PROVIDER_MOCK",
    "PROVIDER_OLLAMA",
]

