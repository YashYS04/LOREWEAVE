"""AI endpoints.

POST /ai/context  — build and return the full universe context
GET  /ai/health   — provider health probe
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers.granite import OllamaGraniteProvider
from app.ai.schemas.ai import ContextRequest, ProviderHealthResponse
from app.ai.services.ai_service import AIService
from app.database.session import get_db
from app.schemas.response import error, success

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


def _get_service(db: DbDep) -> AIService:
    """Dependency: construct AIService with the default Ollama provider."""
    return AIService(session=db, provider=OllamaGraniteProvider())


ServiceDep = Annotated[AIService, Depends(_get_service)]


@router.post(
    "/context",
    summary="Build AI context for a universe",
    description=(
        "Collects all world-building entities for the given universe and returns a "
        "complete, serialized AI-ready context object."
    ),
)
async def get_universe_context(
    payload: ContextRequest, svc: ServiceDep
) -> JSONResponse:
    ctx = await svc.get_context(payload.universe_id)
    if ctx is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Universe not found",
        )
    return JSONResponse(
        content=success(
            data=ctx.model_dump(mode="json"),
            message="Context built successfully.",
        )
    )


@router.get(
    "/health",
    summary="AI provider health check",
    description="Probes the active AI provider and returns its operational status.",
)
async def ai_health(svc: ServiceDep) -> JSONResponse:
    health = await svc.provider_health()
    payload = ProviderHealthResponse(
        provider_name=health.provider_name,
        model=health.model,
        healthy=health.healthy,
        message=health.message,
        version=health.version,
    )

    if not health.healthy:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error(
                code="AI_PROVIDER_UNAVAILABLE",
                message=health.message,
            ),
        )

    return JSONResponse(
        content=success(
            data=payload.model_dump(mode="json"),
            message="AI provider is healthy.",
        )
    )
