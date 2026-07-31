"""Ollama provider for IBM Granite 3.3 2B.

Communicates exclusively with the local Ollama REST API.
Configuration is read from ``app.core.config.settings`` — never hardcoded.

Ollama REST API reference:
    POST /api/generate   — single-shot completion
    POST /api/chat       — chat-style completion (used for streaming)
    GET  /api/tags       — list models (used for health check)
"""

import logging
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from app.ai.providers.base import AIProvider, GenerationResult, ProviderHealth
from app.core.config import settings

logger = logging.getLogger(__name__)

_GENERATE_PATH = "/api/generate"
_TAGS_PATH = "/api/tags"


class OllamaGraniteProvider(AIProvider):
    """Communicates with a locally running Ollama instance serving Granite 3.3 2B."""

    @property
    def provider_name(self) -> str:
        return "Ollama (IBM Granite 3.3 2B)"

    def _client(self) -> httpx.AsyncClient:
        """Return a configured async HTTP client for Ollama."""
        return httpx.AsyncClient(
            base_url=settings.OLLAMA_BASE_URL,
            timeout=settings.OLLAMA_TIMEOUT,
        )

    def _default_temperature(self, temperature: float | None) -> float:
        return temperature if temperature is not None else settings.AI_TEMPERATURE

    def _default_max_tokens(self, max_tokens: int | None) -> int:
        return max_tokens if max_tokens is not None else settings.AI_MAX_TOKENS

    def _build_options(
        self, temperature: float | None, max_tokens: int | None
    ) -> dict[str, Any]:
        return {
            "temperature": self._default_temperature(temperature),
            "num_predict": self._default_max_tokens(max_tokens),
        }

    async def generate(
        self,
        prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> GenerationResult:
        """Send a single-shot generation request to Ollama and return the result."""
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": self._build_options(temperature, max_tokens),
        }
        logger.debug(
            "Ollama generate: model=%s prompt_len=%d",
            settings.OLLAMA_MODEL,
            len(prompt),
        )

        async with self._client() as client:
            response = await client.post(_GENERATE_PATH, json=payload)
            response.raise_for_status()
            body = response.json()

        return GenerationResult(
            text=body.get("response", ""),
            model=body.get("model", settings.OLLAMA_MODEL),
            provider=self.provider_name,
            prompt_tokens=body.get("prompt_eval_count"),
            completion_tokens=body.get("eval_count"),
        )

    async def stream_generate(
        self,
        prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens from Ollama one chunk at a time."""
        import json

        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": True,
            "options": self._build_options(temperature, max_tokens),
        }

        async with self._client() as client:
            async with client.stream("POST", _GENERATE_PATH, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("response", "")
                        if token:
                            yield token
                        if chunk.get("done"):
                            break
                    except json.JSONDecodeError:
                        logger.warning("Unparseable Ollama stream chunk: %r", line)

    async def health(self) -> ProviderHealth:
        """Verify that Ollama is reachable and the configured model is available."""
        try:
            async with self._client() as client:
                response = await client.get(_TAGS_PATH)
                response.raise_for_status()
                body = response.json()

            model_names: list[str] = [m.get("name", "") for m in body.get("models", [])]
            model_available = any(settings.OLLAMA_MODEL in name for name in model_names)

            if not model_available:
                return ProviderHealth(
                    healthy=False,
                    provider_name=self.provider_name,
                    model=settings.OLLAMA_MODEL,
                    message=f"Model '{settings.OLLAMA_MODEL}' not found in Ollama. "
                    f"Available: {model_names or ['none']}",
                    version=body.get("version"),
                )

            return ProviderHealth(
                healthy=True,
                provider_name=self.provider_name,
                model=settings.OLLAMA_MODEL,
                message="Ollama is reachable and model is available.",
                version=body.get("version"),
            )

        except httpx.ConnectError:
            return ProviderHealth(
                healthy=False,
                provider_name=self.provider_name,
                model=settings.OLLAMA_MODEL,
                message=f"Cannot connect to Ollama at {settings.OLLAMA_BASE_URL}. "
                "Ensure Ollama is running locally.",
            )
        except httpx.TimeoutException:
            return ProviderHealth(
                healthy=False,
                provider_name=self.provider_name,
                model=settings.OLLAMA_MODEL,
                message="Ollama health check timed out.",
            )
        except Exception as exc:
            logger.exception("Unexpected error during Ollama health check")
            return ProviderHealth(
                healthy=False,
                provider_name=self.provider_name,
                model=settings.OLLAMA_MODEL,
                message=f"Unexpected error: {exc}",
            )
