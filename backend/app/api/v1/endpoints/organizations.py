"""Organization CRUD endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationListResponse,
    OrganizationResponse,
    OrganizationUpdate,
)
from app.schemas.response import success
from app.services.organization import OrganizationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/organizations", tags=["organizations"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


def _svc(db: DbDep) -> OrganizationService:
    return OrganizationService(db)


SvcDep = Annotated[OrganizationService, Depends(_svc)]


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create an organization")
async def create_organization(payload: OrganizationCreate, svc: SvcDep) -> JSONResponse:
    item = await svc.create(payload)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=success(
            data=OrganizationResponse.model_validate(item).model_dump(mode="json"),
            message="Organization created successfully.",
        ),
    )


@router.get("", summary="List organizations by universe")
async def list_organizations(
    svc: SvcDep,
    universe_id: Annotated[str, Query(min_length=1)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> JSONResponse:
    items, total = await svc.list_entities(universe_id=universe_id, skip=skip, limit=limit)
    payload = OrganizationListResponse(
        items=[OrganizationResponse.model_validate(i) for i in items],
        total=total,
        limit=limit,
        offset=skip,
    )
    return JSONResponse(content=success(data=payload.model_dump(mode="json"), message="OK"))


@router.get("/{organization_id}", summary="Get an organization by ID")
async def get_organization(organization_id: str, svc: SvcDep) -> JSONResponse:
    item = await svc.get_by_id(organization_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )
    return JSONResponse(
        content=success(
            data=OrganizationResponse.model_validate(item).model_dump(mode="json"), message="OK"
        )
    )


@router.patch("/{organization_id}", summary="Update an organization")
async def update_organization(
    organization_id: str, payload: OrganizationUpdate, svc: SvcDep
) -> JSONResponse:
    item = await svc.update(organization_id, payload)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )
    return JSONResponse(
        content=success(
            data=OrganizationResponse.model_validate(item).model_dump(mode="json"),
            message="Organization updated successfully.",
        )
    )


@router.delete(
    "/{organization_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an organization",
)
async def delete_organization(organization_id: str, svc: SvcDep) -> JSONResponse:
    deleted = await svc.delete(organization_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )
    return JSONResponse(
        content=success(data=None, message="Organization deleted successfully.")
    )
