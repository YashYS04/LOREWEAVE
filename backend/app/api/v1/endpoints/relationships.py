"""Relationship CRUD endpoints — Universal Relationship Engine.

POST   /api/v1/relationships
GET    /api/v1/relationships?universe_id=X
GET    /api/v1/relationships/{id}
PATCH  /api/v1/relationships/{id}
DELETE /api/v1/relationships/{id}
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.relationship import (
    RelationshipCreate,
    RelationshipListResponse,
    RelationshipResponse,
    RelationshipUpdate,
)
from app.schemas.response import success
from app.services.relationship import RelationshipService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/relationships", tags=["relationships"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


def _get_service(db: DbDep) -> RelationshipService:
    return RelationshipService(db)


ServiceDep = Annotated[RelationshipService, Depends(_get_service)]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a relationship between two entities",
)
async def create_relationship(
    payload: RelationshipCreate, svc: ServiceDep
) -> JSONResponse:
    rel = await svc.create_relationship(payload)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=success(
            data=RelationshipResponse.from_orm(rel).model_dump(mode="json"),
            message="Relationship created.",
        ),
    )


@router.get(
    "",
    summary="List relationships for a universe with optional filters",
)
async def list_relationships(
    svc: ServiceDep,
    universe_id: Annotated[str, Query(min_length=1)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    entity_id: Annotated[str | None, Query()] = None,
    entity_type: Annotated[str | None, Query()] = None,
    relationship_type: Annotated[str | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
) -> JSONResponse:
    items, total = await svc.list_relationships(
        universe_id,
        skip=skip,
        limit=limit,
        entity_id=entity_id,
        entity_type=entity_type,
        relationship_type=relationship_type,
        search=search,
    )
    payload = RelationshipListResponse(
        items=[RelationshipResponse.from_orm(r) for r in items],
        total=total,
        limit=limit,
        offset=skip,
    )
    return JSONResponse(content=success(data=payload.model_dump(mode="json"), message="OK"))


@router.get(
    "/{relationship_id}",
    summary="Get a relationship by ID",
)
async def get_relationship(relationship_id: str, svc: ServiceDep) -> JSONResponse:
    rel = await svc.get_by_id(relationship_id)
    if not rel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found"
        )
    return JSONResponse(
        content=success(
            data=RelationshipResponse.from_orm(rel).model_dump(mode="json"),
            message="OK",
        )
    )


@router.patch(
    "/{relationship_id}",
    summary="Update a relationship",
)
async def update_relationship(
    relationship_id: str, payload: RelationshipUpdate, svc: ServiceDep
) -> JSONResponse:
    rel = await svc.update_relationship(relationship_id, payload)
    if not rel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found"
        )
    return JSONResponse(
        content=success(
            data=RelationshipResponse.from_orm(rel).model_dump(mode="json"),
            message="Relationship updated.",
        )
    )


@router.delete(
    "/{relationship_id}",
    status_code=status.HTTP_200_OK,
    summary="Soft-delete a relationship",
)
async def delete_relationship(relationship_id: str, svc: ServiceDep) -> JSONResponse:
    deleted = await svc.delete_relationship(relationship_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found"
        )
    return JSONResponse(content=success(data=None, message="Relationship deleted."))
