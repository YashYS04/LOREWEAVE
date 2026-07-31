"""Universe CRUD endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.response import success
from app.schemas.universe import (
    UniverseCreate,
    UniverseListResponse,
    UniverseResponse,
    UniverseUpdate,
)
from app.services.universe import UniverseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/universes", tags=["universes"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


def _get_service(db: DbDep) -> UniverseService:
    return UniverseService(db)


ServiceDep = Annotated[UniverseService, Depends(_get_service)]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a universe",
)
async def create_universe(payload: UniverseCreate, svc: ServiceDep) -> JSONResponse:
    universe = await svc.create_universe(payload)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=success(
            data=UniverseResponse.model_validate(universe).model_dump(mode="json"),
            message="Universe created successfully.",
        ),
    )


@router.get(
    "",
    summary="List all universes",
)
async def list_universes(
    svc: ServiceDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> JSONResponse:
    universes, total = await svc.list_universes(skip=skip, limit=limit)
    payload = UniverseListResponse(
        items=[UniverseResponse.model_validate(u) for u in universes],
        total=total,
        limit=limit,
        offset=skip,
    )
    return JSONResponse(
        content=success(
            data=payload.model_dump(mode="json"),
            message="OK",
        )
    )


@router.get(
    "/{universe_id}",
    summary="Get a universe by ID",
)
async def get_universe(universe_id: str, svc: ServiceDep) -> JSONResponse:
    universe = await svc.get_by_id(universe_id)
    if not universe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Universe not found"
        )
    return JSONResponse(
        content=success(
            data=UniverseResponse.model_validate(universe).model_dump(mode="json"),
            message="OK",
        )
    )


@router.patch(
    "/{universe_id}",
    summary="Update a universe",
)
async def update_universe(
    universe_id: str, payload: UniverseUpdate, svc: ServiceDep
) -> JSONResponse:
    universe = await svc.update_universe(universe_id, payload)
    if not universe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Universe not found"
        )
    return JSONResponse(
        content=success(
            data=UniverseResponse.model_validate(universe).model_dump(mode="json"),
            message="Universe updated successfully.",
        )
    )


@router.delete(
    "/{universe_id}",
    status_code=status.HTTP_200_OK,
    summary="Soft-delete a universe",
)
async def delete_universe(universe_id: str, svc: ServiceDep) -> JSONResponse:
    deleted = await svc.delete_universe(universe_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Universe not found"
        )
    return JSONResponse(
        content=success(data=None, message="Universe deleted successfully.")
    )
