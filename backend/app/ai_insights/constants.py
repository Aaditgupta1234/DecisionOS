"""Constants, model providers, and prompt versioning for Phase 6.0 AI Insights Layer."""

# Supported Provider Names
PROVIDER_OPENAI = "openai"
PROVIDER_MOCK = "mock"
PROVIDER_ANTHROPIC = "anthropic"
PROVIDER_GEMINI = "gemini"
PROVIDER_OLLAMA = "ollama"

# Default Model Specifications
# DEFAULT_MODEL_PROVIDER is the static fallback used before settings are available.
# At runtime, settings.AI_PROVIDER is authoritative (read in provider factory).
DEFAULT_MODEL_PROVIDER = PROVIDER_MOCK
DEFAULT_MODEL_NAME = "qwen2.5:1.5b"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 2500

# Canonical Versioning Identifiers
INSIGHT_VERSION = "1.0"
PROMPT_VERSION = "1.0"
REPORT_VERSION = "1.0"
