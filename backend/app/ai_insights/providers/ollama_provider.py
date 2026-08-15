"""Ollama LLM Provider for DecisionOS — local Qwen 2.5 inference via the Ollama HTTP API.

Architecture note
-----------------
This provider communicates with a locally-running Ollama daemon using plain httpx.
No Ollama Python SDK is imported deliberately — the SDK adds version-coupling risk
and the REST API is stable enough to depend on directly.

All AI services (AIInsightManager, ChatAnalystService, StrategyPlannerService, etc.)
receive this provider through get_llm_provider() or FastAPI DI, never instantiating
it directly. This preserves the provider-agnostic contract.

The AI layer in DecisionOS NEVER calculates metrics, runs diagnostics, or reads raw
datasets. It only explains pre-computed structured intelligence.
"""

import json
import logging
import re
import time
from typing import Any, Dict, Optional

import httpx

from app.ai_insights.constants import PROVIDER_OLLAMA
from app.ai_insights.providers.base_llm_provider import BaseLLMProvider
from app.ai_insights.providers.exceptions import (
    OllamaConnectionError,
    OllamaInvalidResponseError,
    OllamaModelNotFoundError,
    OllamaTimeoutError,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Ollama REST API endpoint paths (relative to base_url)
# ---------------------------------------------------------------------------
_GENERATE_PATH = "/api/generate"
_TAGS_PATH = "/api/tags"


class OllamaProvider(BaseLLMProvider):
    """
    Production Ollama LLM provider for DecisionOS.

    Communicates with a locally running Ollama daemon to perform text generation
    and JSON synthesis using Qwen 2.5 1.5B (or any other installed local model).

    Design decisions
    ----------------
    * Uses httpx.AsyncClient for all HTTP communication — fully async, no sync blocking.
    * Does NOT fall back to MockLLMProvider on failure. Errors surface explicitly so
      misconfiguration is visible rather than silently degraded.
    * JSON extraction includes a regex fence-stripper because small Qwen models
      frequently wrap their JSON output in ```json ... ``` markdown blocks.
    * Timeout is configurable at construction time, defaulting to settings.OLLAMA_TIMEOUT.
    """

    def __init__(
        self,
        base_url: str,
        model_name: str,
        timeout: int = 60,
    ) -> None:
        """
        Args:
            base_url:   Ollama daemon base URL, e.g. ``http://localhost:11434``.
            model_name: Model tag to use, e.g. ``qwen2.5:1.5b``.
            timeout:    HTTP request timeout in seconds.
        """
        self._base_url = base_url.rstrip("/")
        self._model_name = model_name
        self._timeout = timeout
        logger.info(
            "[OllamaProvider] Initialized — base_url=%s model=%s timeout=%ds",
            self._base_url,
            self._model_name,
            self._timeout,
        )

    # ------------------------------------------------------------------
    # BaseLLMProvider properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        return PROVIDER_OLLAMA

    @property
    def model_name(self) -> str:
        return self._model_name

    # ------------------------------------------------------------------
    # Text generation
    # ------------------------------------------------------------------

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2500,
    ) -> str:
        """
        Sends a prompt to Ollama and returns the generated text string.

        Args:
            prompt:        The user-facing instruction or question.
            system_prompt: Optional system-level instruction prepended to context.
            temperature:   Sampling temperature (0.0 = deterministic, 1.0 = creative).
            max_tokens:    Maximum tokens to generate (mapped to Ollama ``num_predict``).

        Returns:
            Generated text as a clean string.

        Raises:
            OllamaConnectionError:     Daemon unreachable.
            OllamaTimeoutError:        Request exceeded ``timeout`` seconds.
            OllamaModelNotFoundError:  Configured model not installed in Ollama.
            OllamaInvalidResponseError: Unexpected response structure.
        """
        payload: Dict[str, Any] = {
            "model": self._model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if system_prompt:
            payload["system"] = system_prompt

        logger.debug(
            "[OllamaProvider] generate_text — model=%s prompt_len=%d",
            self._model_name,
            len(prompt),
        )

        response_data = await self._post(_GENERATE_PATH, payload)

        generated = response_data.get("response", "")
        if not isinstance(generated, str):
            raise OllamaInvalidResponseError(
                f"Expected 'response' to be str, got {type(generated).__name__}."
            )

        logger.debug(
            "[OllamaProvider] generate_text complete — response_len=%d",
            len(generated),
        )
        return generated

    # ------------------------------------------------------------------
    # JSON generation
    # ------------------------------------------------------------------

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """
        Sends a prompt to Ollama and parses the response as JSON.

        Small quantized models such as Qwen 2.5 1.5B frequently wrap their JSON
        in markdown code fences (```json ... ```). The response is passed through
        a fence-stripper before ``json.loads()`` is attempted.

        Args:
            prompt:        Instruction requesting structured JSON output.
            system_prompt: System-level context injected before the prompt.
            temperature:   Lower values (0.1–0.2) produce more consistent JSON.

        Returns:
            Parsed Python dict from the model's JSON output.

        Raises:
            OllamaInvalidResponseError: Model returned non-parseable output.
            OllamaConnectionError, OllamaTimeoutError, OllamaModelNotFoundError.
        """
        json_system = (
            (system_prompt + "\n\n" if system_prompt else "")
            + "You must respond with valid JSON only. Do not include explanations, "
            "preamble, or markdown formatting outside the JSON object."
        )

        payload: Dict[str, Any] = {
            "model": self._model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
            "system": json_system,
        }

        logger.debug(
            "[OllamaProvider] generate_json — model=%s prompt_len=%d",
            self._model_name,
            len(prompt),
        )

        response_data = await self._post(_GENERATE_PATH, payload)
        raw_text = response_data.get("response", "")

        cleaned = self._strip_markdown_fences(raw_text)

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.error(
                "[OllamaProvider] generate_json — JSON parse failure: %s | raw_text=%r",
                exc,
                raw_text[:300],
            )
            raise OllamaInvalidResponseError(
                f"Ollama returned non-JSON output. Parse error: {exc}. "
                f"Raw response (truncated): {raw_text[:200]!r}"
            ) from exc

        logger.debug(
            "[OllamaProvider] generate_json complete — keys=%s",
            list(parsed.keys()) if isinstance(parsed, dict) else type(parsed).__name__,
        )
        return parsed

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    async def health_check(self) -> bool:
        """
        Verifies that the Ollama daemon is reachable and the configured model
        is installed (present in the ``GET /api/tags`` response).

        Returns:
            True  if the daemon responds and the model is available.
            False if the daemon is unreachable or the model is missing.
        """
        try:
            tags = await self._get_tags()
        except (OllamaConnectionError, OllamaTimeoutError, OllamaInvalidResponseError) as exc:
            logger.warning("[OllamaProvider] health_check failed: %s", exc)
            return False

        model_names = self._extract_model_names(tags)
        available = self._model_name in model_names

        if not available:
            logger.warning(
                "[OllamaProvider] health_check — model '%s' not found. Available: %s",
                self._model_name,
                model_names,
            )

        return available

    # ------------------------------------------------------------------
    # Model discovery
    # ------------------------------------------------------------------

    async def list_models(self) -> list[str]:
        """
        Queries the Ollama daemon for all installed model tags.

        Returns:
            Sorted list of model name strings (e.g. ``['llama3.2:1b', 'qwen2.5:1.5b']``).
            Returns an empty list if the daemon is unreachable rather than raising,
            keeping the health endpoint non-fatal when Ollama is temporarily down.
        """
        try:
            tags = await self._get_tags()
        except (OllamaConnectionError, OllamaTimeoutError, OllamaInvalidResponseError) as exc:
            logger.warning("[OllamaProvider] list_models failed: %s", exc)
            return []

        names = self._extract_model_names(tags)
        logger.debug("[OllamaProvider] list_models — found %d models", len(names))
        return sorted(names)

    # ------------------------------------------------------------------
    # Private HTTP helpers
    # ------------------------------------------------------------------

    async def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a POST request against the Ollama HTTP API.

        Translates httpx exceptions into the DecisionOS Ollama exception hierarchy
        so callers never need to import httpx directly.
        """
        url = f"{self._base_url}{path}"
        start_ts = time.monotonic()

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data: Dict[str, Any] = resp.json()

        except httpx.TimeoutException as exc:
            elapsed = round((time.monotonic() - start_ts) * 1000, 1)
            logger.error(
                "[OllamaProvider] POST %s timed out after %dms — timeout_cfg=%ds",
                path,
                elapsed,
                self._timeout,
            )
            raise OllamaTimeoutError(
                f"Ollama request to {path} timed out after {self._timeout}s."
            ) from exc

        except httpx.ConnectError as exc:
            logger.error(
                "[OllamaProvider] POST %s — connection refused at %s: %s",
                path,
                self._base_url,
                exc,
            )
            raise OllamaConnectionError(
                f"Cannot connect to Ollama at {self._base_url}. "
                "Ensure Ollama is running (`ollama serve`)."
            ) from exc

        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            body = exc.response.text[:300]
            logger.error(
                "[OllamaProvider] POST %s — HTTP %d: %s",
                path,
                status_code,
                body,
            )
            # Ollama returns 404 when the requested model is not installed
            if status_code == 404 and self._model_name in body:
                raise OllamaModelNotFoundError(
                    f"Model '{self._model_name}' is not installed in Ollama. "
                    f"Run: ollama pull {self._model_name}"
                ) from exc
            raise OllamaInvalidResponseError(
                f"Ollama returned HTTP {status_code}: {body}"
            ) from exc

        except (httpx.RequestError, ValueError) as exc:
            logger.error("[OllamaProvider] POST %s — unexpected error: %s", path, exc)
            raise OllamaInvalidResponseError(
                f"Unexpected error communicating with Ollama: {exc}"
            ) from exc

        elapsed_ms = round((time.monotonic() - start_ts) * 1000, 1)
        logger.debug("[OllamaProvider] POST %s completed in %dms", path, elapsed_ms)
        return data

    async def _get_tags(self) -> Dict[str, Any]:
        """
        Performs ``GET /api/tags`` and returns the parsed JSON body.

        Used by both health_check() and list_models().
        """
        url = f"{self._base_url}{_TAGS_PATH}"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                return resp.json()
        except httpx.TimeoutException as exc:
            raise OllamaTimeoutError(
                f"Ollama /api/tags request timed out after {self._timeout}s."
            ) from exc
        except httpx.ConnectError as exc:
            raise OllamaConnectionError(
                f"Cannot connect to Ollama at {self._base_url}."
            ) from exc
        except (httpx.HTTPStatusError, httpx.RequestError, ValueError) as exc:
            raise OllamaInvalidResponseError(
                f"Failed to retrieve Ollama model tags: {exc}"
            ) from exc

    @staticmethod
    def _extract_model_names(tags_response: Dict[str, Any]) -> list[str]:
        """
        Extracts model name strings from the ``GET /api/tags`` JSON response.

        Ollama tags response shape::

            {
                "models": [
                    {"name": "qwen2.5:1.5b", "size": 123456, ...},
                    ...
                ]
            }
        """
        models = tags_response.get("models", [])
        return [m.get("name", "") for m in models if isinstance(m, dict) and m.get("name")]

    @staticmethod
    def _strip_markdown_fences(text: str) -> str:
        """
        Removes markdown code fences from model output.

        Small quantized models (Qwen 2.5 1.5B, LLaMA 3.2 1B, etc.) frequently
        produce output like::

            ```json
            {"key": "value"}
            ```

        This method strips the fences and returns the raw JSON string.
        """
        pattern = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
        return text.strip()
