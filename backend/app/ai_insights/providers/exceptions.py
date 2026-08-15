"""Custom exceptions for the Ollama LLM Provider in DecisionOS.

All exceptions inherit from OllamaProviderError so callers can catch the
entire hierarchy with a single except clause when appropriate.

Hierarchy
---------
OllamaProviderError
├── OllamaConnectionError      — Daemon not reachable at configured URL
├── OllamaTimeoutError         — Request exceeded the configured timeout
├── OllamaModelNotFoundError   — Requested model not installed in Ollama
└── OllamaInvalidResponseError — Unexpected/malformed API response
"""


class OllamaProviderError(Exception):
    """Base exception for all Ollama provider failures in DecisionOS."""


class OllamaConnectionError(OllamaProviderError):
    """Raised when the Ollama daemon is unreachable at the configured base URL.

    Typical causes:
    - Ollama service not started (run `ollama serve`).
    - Wrong `OLLAMA_BASE_URL` in `.env`.
    - Firewall or network issue in non-local deployments.
    """


class OllamaTimeoutError(OllamaProviderError):
    """Raised when an Ollama HTTP request exceeds `OLLAMA_TIMEOUT` seconds.

    Typical causes:
    - Model too large for available hardware (slow inference).
    - Prompt too long producing excessive generation.
    - System under high load.

    Mitigation: reduce `max_tokens`, use a smaller model, or increase `OLLAMA_TIMEOUT`.
    """


class OllamaModelNotFoundError(OllamaProviderError):
    """Raised when the configured model is not installed in the Ollama instance.

    Resolution: run `ollama pull <model_name>` with the value from `OLLAMA_MODEL`.
    """


class OllamaInvalidResponseError(OllamaProviderError):
    """Raised when Ollama returns an HTTP error or non-parseable response body.

    Typical causes:
    - Ollama version mismatch (unexpected API response shape).
    - Model crashed mid-generation.
    - JSON generation produced non-JSON output that could not be parsed.
    """
