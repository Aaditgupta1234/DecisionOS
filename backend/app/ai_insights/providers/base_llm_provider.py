"""Abstract base interface for LLM Providers in DecisionOS."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List


class BaseLLMProvider(ABC):
    """
    Abstract LLM Provider interface ensuring modularity across OpenAI, Anthropic, Gemini,
    Ollama, and Mock fallback providers without leaking vendor dependencies.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the identifier name of the provider (e.g. 'ollama', 'mock')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Returns the specific model identifier (e.g. 'qwen2.5:1.5b')."""
        pass

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2500,
    ) -> str:
        """
        Asynchronously generates free-form text given prompt and system instructions.
        """
        pass

    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """
        Asynchronously generates and parses structured JSON matching the generator schema.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Verifies availability of the LLM provider service.
        Returns True if the provider is reachable and the configured model is accessible.
        """
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        """
        Returns a list of model identifiers available on this provider.

        Used by the AI health endpoint and provider discovery.
        For local providers (Ollama) this queries the running service.
        For cloud providers this returns a static set of supported model IDs.
        """
        pass
