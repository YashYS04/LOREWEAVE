"""Centralised exception handling for the FastAPI application."""

import logging

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.schemas.response import error

logger = logging.getLogger(__name__)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic / FastAPI request-validation failures (422)."""
    logger.warning(
        "Validation error on %s %s: %s", request.method, request.url, exc.errors()
    )
    first = exc.errors()[0] if exc.errors() else {}
    field = ".".join(str(loc) for loc in first.get("loc", [])) if first else "unknown"
    msg = first.get("msg", "Validation failed") if first else "Validation failed"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error(code="VALIDATION_ERROR", message=f"{field}: {msg}"),
    )


async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle 404 Not Found — raised manually via HTTPException(404)."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=error(code="NOT_FOUND", message=str(exc)),
    )


async def conflict_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Handle database integrity conflicts (e.g. duplicate slug)."""
    logger.warning("Integrity conflict on %s %s: %s", request.method, request.url, exc)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error(
            code="CONFLICT", message="A resource with that identifier already exists."
        ),
    )


async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled 500 errors."""
    logger.exception("Unhandled error on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error(code="INTERNAL_ERROR", message="An unexpected error occurred."),
    )
