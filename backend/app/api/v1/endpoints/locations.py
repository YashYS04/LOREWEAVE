"""Location CRUD endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.location import (
    LocationCreate,
    LocationListResponse,
    LocationResponse,
    LocationUpdate,
)
from app.schemas.response import success
from app.services.location import LocationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/locations", tags=["locations"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


def _svc(db: DbDep) -> LocationService:
    return LocationService(db)


SvcDep = Annotated[LocationService, Depends(_svc)]


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create a location")
async def create_location(payload: LocationCreate, svc: SvcDep) -> JSONResponse:
    item = await svc.create(payload)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=success(
            data=LocationResponse.model_validate(item).model_dump(mode="json"),
            message="Location created successfully.",
        ),
    )


@router.get("", summary="List locations by universe")
async def list_locations(
    svc: SvcDep,
    universe_id: Annotated[str, Query(min_length=1)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> JSONResponse:
    items, total = await svc.list_entities(universe_id=universe_id, skip=skip, limit=limit)
    payload = LocationListResponse(
        items=[LocationResponse.model_validate(i) for i in items],
        total=total,
        limit=limit,
        offset=skip,
    )
    return JSONResponse(content=success(data=payload.model_dump(mode="json"), message="OK"))


@router.get("/{location_id}", summary="Get a location by ID")
async def get_location(location_id: str, svc: SvcDep) -> JSONResponse:
    item = await svc.get_by_id(location_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return JSONResponse(
        content=success(
            data=LocationResponse.model_validate(item).model_dump(mode="json"), message="OK"
        )
    )


@router.patch("/{location_id}", summary="Update a location")
async def update_location(
    location_id: str, payload: LocationUpdate, svc: SvcDep
) -> JSONResponse:
    item = await svc.update(location_id, payload)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return JSONResponse(
        content=success(
            data=LocationResponse.model_validate(item).model_dump(mode="json"),
            message="Location updated successfully.",
        )
    )


@router.delete("/{location_id}", status_code=status.HTTP_200_OK, summary="Delete a location")
async def delete_location(location_id: str, svc: SvcDep) -> JSONResponse:
    deleted = await svc.delete(location_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return JSONResponse(content=success(data=None, message="Location deleted successfully."))
