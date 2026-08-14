"""Abstract base interface for LLM Providers in DecisionOS."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseLLMProvider(ABC):
    """
    Abstract LLM Provider interface ensuring modularity across OpenAI, Anthropic, Gemini,
    and Mock fallback providers without leaking vendor dependencies.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the identifier name of the provider (e.g. 'openai', 'mock')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Returns the specific model identifier (e.g. 'gpt-4o-mini')."""
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
        """
        pass
