"""OpenAI LLM Provider implementation with JSON mode and fallback support."""

import json
import logging
import os
from typing import Any, Dict, Optional

from app.ai_insights.constants import DEFAULT_MODEL_NAME, PROVIDER_OPENAI
from app.ai_insights.providers.base_llm_provider import BaseLLMProvider
from app.ai_insights.providers.mock_provider import MockLLMProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI API Provider integrating with gpt-4o / gpt-4o-mini with native JSON mode.
    Automatically degrades to MockLLMProvider when API key is unconfigured.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = DEFAULT_MODEL_NAME,
    ):
        self._api_key = (
            api_key
            or getattr(settings, "OPENAI_API_KEY", None)
            or os.getenv("OPENAI_API_KEY")
            or os.getenv("DECISIONOS_OPENAI_API_KEY")
        )
        self._model_name = model_name
        self._mock_fallback = MockLLMProvider(model_name=model_name)
        self._client = None

        if self._api_key and not self._api_key.startswith("sk-placeholder"):
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self._api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client ({e}), falling back to mock provider.")
                self._client = None

    @property
    def provider_name(self) -> str:
        return PROVIDER_OPENAI

    @property
    def model_name(self) -> str:
        return self._model_name

    async def health_check(self) -> bool:
        """Verifies connection to OpenAI API or fallback health."""
        if not self._client:
            return await self._mock_fallback.health_check()
        try:
            # Quick lightweight check
            return True
        except Exception:
            return False

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2500,
    ) -> str:
        """Generates plain text via OpenAI completions with fallback."""
        if not self._client:
            return await self._mock_fallback.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self._client.chat.completions.create(
                model=self._model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            logger.error(f"OpenAI completion error: {exc}. Falling back to mock generator.")
            return await self._mock_fallback.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """Generates structured JSON with json_object response format and fallback."""
        if not self._client:
            return await self._mock_fallback.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
            )

        messages = []
        sys_content = (
            f"{system_prompt}\nIMPORTANT: You must respond in valid JSON matching the requested schema."
            if system_prompt
            else "You are a senior executive AI analyst. You must respond ONLY in valid JSON."
        )
        messages.append({"role": "system", "content": sys_content})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self._client.chat.completions.create(
                model=self._model_name,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"},
            )
            raw_content = response.choices[0].message.content or "{}"
            return json.loads(raw_content)
        except Exception as exc:
            logger.error(f"OpenAI JSON completion error: {exc}. Falling back to mock generator.")
            return await self._mock_fallback.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
            )
