"""LOREWEAVE Backend — application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

import app.models.character  # noqa: F401 — registers model with Base.metadata
import app.models.chat  # noqa: F401 — registers model with Base.metadata
import app.models.location  # noqa: F401 — registers model with Base.metadata
import app.models.organization  # noqa: F401 — registers model with Base.metadata
import app.models.relationship  # noqa: F401 — registers model with Base.metadata
import app.models.timeline  # noqa: F401 — registers model with Base.metadata
import app.models.universe  # noqa: F401 — registers model with Base.metadata
import app.models.world_object  # noqa: F401 — registers model with Base.metadata
import app.models.world_rule  # noqa: F401 — registers model with Base.metadata
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import (
    conflict_handler,
    internal_error_handler,
    not_found_handler,
    validation_exception_handler,
)
from app.core.logging import configure_logging
from app.database.base import Base
from app.database.session import engine
from app.schemas.response import error


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    configure_logging()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


def create_application() -> FastAPI:
    """Construct and configure the FastAPI application instance."""
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
        lifespan=lifespan,
    )

    # ── Middleware ──────────────────────────────────────────────────────────────
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception handlers ──────────────────────────────────────────────────────
    application.add_exception_handler(
        RequestValidationError, validation_exception_handler
    )
    application.add_exception_handler(IntegrityError, conflict_handler)
    application.add_exception_handler(Exception, internal_error_handler)

    # HTTPException 404 needs special handling to keep our envelope shape.
    @application.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException):
        if exc.status_code == 404:
            return await not_found_handler(request, Exception(exc.detail))
        return JSONResponse(
            status_code=exc.status_code,
            content=error(code=str(exc.status_code), message=exc.detail),
        )

    # ── Routers ─────────────────────────────────────────────────────────────────
    application.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # ── Root ────────────────────────────────────────────────────────────────────
    @application.get("/", include_in_schema=False)
    async def root() -> JSONResponse:
        return JSONResponse(
            {
                "application": "LOREWEAVE API",
                "status": "running",
                "version": settings.APP_VERSION,
                "docs": f"{settings.API_V1_PREFIX}/docs",
                "health": f"{settings.API_V1_PREFIX}/health",
            }
        )

    return application


app = create_application()
