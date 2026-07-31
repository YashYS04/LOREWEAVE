"""WorldObject CRUD endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.response import success
from app.schemas.world_object import (
    WorldObjectCreate,
    WorldObjectListResponse,
    WorldObjectResponse,
    WorldObjectUpdate,
)
from app.services.world_object import WorldObjectService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/objects", tags=["objects"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


def _svc(db: DbDep) -> WorldObjectService:
    return WorldObjectService(db)


SvcDep = Annotated[WorldObjectService, Depends(_svc)]


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create an object")
async def create_world_object(payload: WorldObjectCreate, svc: SvcDep) -> JSONResponse:
    item = await svc.create(payload)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=success(
            data=WorldObjectResponse.model_validate(item).model_dump(mode="json"),
            message="Object created successfully.",
        ),
    )


@router.get("", summary="List objects by universe")
async def list_world_objects(
    svc: SvcDep,
    universe_id: Annotated[str, Query(min_length=1)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> JSONResponse:
    items, total = await svc.list_entities(universe_id=universe_id, skip=skip, limit=limit)
    payload = WorldObjectListResponse(
        items=[WorldObjectResponse.model_validate(i) for i in items],
        total=total,
        limit=limit,
        offset=skip,
    )
    return JSONResponse(content=success(data=payload.model_dump(mode="json"), message="OK"))


@router.get("/{object_id}", summary="Get an object by ID")
async def get_world_object(object_id: str, svc: SvcDep) -> JSONResponse:
    item = await svc.get_by_id(object_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found")
    return JSONResponse(
        content=success(
            data=WorldObjectResponse.model_validate(item).model_dump(mode="json"), message="OK"
        )
    )


@router.patch("/{object_id}", summary="Update an object")
async def update_world_object(
    object_id: str, payload: WorldObjectUpdate, svc: SvcDep
) -> JSONResponse:
    item = await svc.update(object_id, payload)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found")
    return JSONResponse(
        content=success(
            data=WorldObjectResponse.model_validate(item).model_dump(mode="json"),
            message="Object updated successfully.",
        )
    )


@router.delete("/{object_id}", status_code=status.HTTP_200_OK, summary="Delete an object")
async def delete_world_object(object_id: str, svc: SvcDep) -> JSONResponse:
    deleted = await svc.delete(object_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found")
    return JSONResponse(content=success(data=None, message="Object deleted successfully."))
