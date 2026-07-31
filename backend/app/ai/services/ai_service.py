"""AIService — orchestrates the entire AI pipeline.

Responsibilities:
    1. Build universe context via UniverseContextBuilder
    2. Select and render a prompt template
    3. Delegate generation to the injected AIProvider
    4. Return a structured GenerationResponse

This service MUST NOT contain any HTTP logic.
All network communication lives in the provider layer.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.context.builder import UniverseContextBuilder
from app.ai.prompts.templates import get_prompt
from app.ai.providers.base import AIProvider, GenerationResult, ProviderHealth
from app.ai.schemas.ai import GenerationRequest, GenerationResponse, UniverseContext

logger = logging.getLogger(__name__)


class AIService:
    """Orchestrates context building, prompt rendering, and provider calls."""

    def __init__(self, session: AsyncSession, provider: AIProvider) -> None:
        self._session = session
        self._provider = provider
        self._builder = UniverseContextBuilder(session)

    # ── Context ────────────────────────────────────────────────────────────────

    async def get_context(self, universe_id: str) -> UniverseContext | None:
        """Build and return the AI-ready context for a universe."""
        return await self._builder.build(universe_id)

    # ── Provider status ────────────────────────────────────────────────────────

    async def provider_health(self) -> ProviderHealth:
        """Delegate a health probe to the active provider."""
        return await self._provider.health()

    @property
    def active_provider_name(self) -> str:
        return self._provider.provider_name

    # ── Generation ─────────────────────────────────────────────────────────────

    async def generate(self, request: GenerationRequest) -> GenerationResponse | None:
        """Full pipeline: build context → render prompt → call provider → return result.

        Returns ``None`` if the universe is not found.
        """
        ctx = await self._builder.build(request.universe_id)
        if ctx is None:
            return None

        prompt = get_prompt(request.prompt_key, ctx, request.user_question)
        logger.info(
            "Generating with template=%s universe_id=%s prompt_len=%d",
            request.prompt_key,
            request.universe_id,
            len(prompt),
        )

        result: GenerationResult = await self._provider.generate(
            prompt=prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return GenerationResponse(
            text=result.text,
            model=result.model,
            provider=result.provider,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
        )
