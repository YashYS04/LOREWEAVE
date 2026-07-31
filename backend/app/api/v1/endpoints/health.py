"""Health-check endpoint — reports status, DB connectivity, and version."""

import logging

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.session import get_db
from app.schemas.response import error, success

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    summary="Health check",
    description="Returns operational status, database connectivity, and application version.",
)
async def health_check(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    db_ok = False
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        logger.exception("Database health probe failed")

    payload = {
        "status": "healthy" if db_ok else "degraded",
        "version": settings.APP_VERSION,
        "database": "ok" if db_ok else "unreachable",
    }

    if not db_ok:
        return JSONResponse(
            status_code=503,
            content=error(
                code="DATABASE_UNAVAILABLE", message="Database is unreachable."
            ),
        )

    return JSONResponse(content=success(data=payload, message="OK"))
