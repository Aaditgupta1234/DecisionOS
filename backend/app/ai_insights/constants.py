"""Constants, model providers, and prompt versioning for Phase 6.0 AI Insights Layer."""

# Supported Provider Names
PROVIDER_OPENAI = "openai"
PROVIDER_MOCK = "mock"
PROVIDER_ANTHROPIC = "anthropic"
PROVIDER_GEMINI = "gemini"

# Default Model Specifications
DEFAULT_MODEL_PROVIDER = PROVIDER_OPENAI
DEFAULT_MODEL_NAME = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 2500

# Canonical Versioning Identifiers
INSIGHT_VERSION = "1.0"
PROMPT_VERSION = "1.0"
REPORT_VERSION = "1.0"
