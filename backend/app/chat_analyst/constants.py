"""Constants and enumerations for Phase 9.4: AI Chat Analyst Integration."""

from enum import Enum
from typing import List

# Prompt and Schema Versioning
CHAT_PROMPT_VERSION = "1.0"
CHAT_SCHEMA_VERSION = "1.0"

# Memory and Token Limits
MAX_HISTORY_MESSAGES = 10
MAX_CONTEXT_TOKENS = 3000
DEFAULT_CHAT_MODEL = "qwen2.5:1.5b"
DEFAULT_CHAT_PROVIDER = "ollama"

# Context Compression Limits (Top-K per category)
MAX_COMPRESSED_FINDINGS = 5
MAX_COMPRESSED_ROOT_CAUSES = 3
MAX_COMPRESSED_RECOMMENDATIONS = 5
MAX_COMPRESSED_FORECASTS = 3
MAX_COMPRESSED_SCENARIOS = 3


class QuestionType(str, Enum):
    """Categorized analytical user question intent."""
    FORECAST_QUESTION = "FORECAST_QUESTION"
    ROOT_CAUSE_QUESTION = "ROOT_CAUSE_QUESTION"
    RECOMMENDATION_QUESTION = "RECOMMENDATION_QUESTION"
    SCENARIO_QUESTION = "SCENARIO_QUESTION"
    HEALTH_SCORE_QUESTION = "HEALTH_SCORE_QUESTION"
    GENERAL_BUSINESS_QUESTION = "GENERAL_BUSINESS_QUESTION"


class ResponseType(str, Enum):
    """Categorized response type for telemetry and dashboard analytics."""
    ROOT_CAUSE = "ROOT_CAUSE"
    FORECAST = "FORECAST"
    SCENARIO = "SCENARIO"
    RECOMMENDATION = "RECOMMENDATION"
    HEALTH_SCORE = "HEALTH_SCORE"
    GENERAL = "GENERAL"


# Prohibited ungrounded / speculative trigger phrases
HALLUCINATION_TRIGGERS: List[str] = [
    "i think",
    "i believe",
    "probably",
    "maybe",
    "likely because",
    "outside the dataset",
    "assume",
    "in my opinion",
    "i suspect",
    "i guess",
    "based on external knowledge",
    "generally speaking",
]
