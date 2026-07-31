"""WorldRule CRUD endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.response import success
from app.schemas.world_rule import (
    WorldRuleCreate,
    WorldRuleListResponse,
    WorldRuleResponse,
    WorldRuleUpdate,
)
from app.services.world_rule import WorldRuleService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rules", tags=["rules"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


def _svc(db: DbDep) -> WorldRuleService:
    return WorldRuleService(db)


SvcDep = Annotated[WorldRuleService, Depends(_svc)]


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create a world rule")
async def create_world_rule(payload: WorldRuleCreate, svc: SvcDep) -> JSONResponse:
    item = await svc.create(payload)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=success(
            data=WorldRuleResponse.model_validate(item).model_dump(mode="json"),
            message="World rule created successfully.",
        ),
    )


@router.get("", summary="List world rules by universe")
async def list_world_rules(
    svc: SvcDep,
    universe_id: Annotated[str, Query(min_length=1)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> JSONResponse:
    items, total = await svc.list_entities(
        universe_id=universe_id, skip=skip, limit=limit
    )
    payload = WorldRuleListResponse(
        items=[WorldRuleResponse.model_validate(i) for i in items],
        total=total,
        limit=limit,
        offset=skip,
    )
    return JSONResponse(
        content=success(data=payload.model_dump(mode="json"), message="OK")
    )


@router.get("/{rule_id}", summary="Get a world rule by ID")
async def get_world_rule(rule_id: str, svc: SvcDep) -> JSONResponse:
    item = await svc.get_by_id(rule_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="World rule not found"
        )
    return JSONResponse(
        content=success(
            data=WorldRuleResponse.model_validate(item).model_dump(mode="json"),
            message="OK",
        )
    )


@router.patch("/{rule_id}", summary="Update a world rule")
async def update_world_rule(
    rule_id: str, payload: WorldRuleUpdate, svc: SvcDep
) -> JSONResponse:
    item = await svc.update(rule_id, payload)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="World rule not found"
        )
    return JSONResponse(
        content=success(
            data=WorldRuleResponse.model_validate(item).model_dump(mode="json"),
            message="World rule updated successfully.",
        )
    )


@router.delete(
    "/{rule_id}", status_code=status.HTTP_200_OK, summary="Delete a world rule"
)
async def delete_world_rule(rule_id: str, svc: SvcDep) -> JSONResponse:
    deleted = await svc.delete(rule_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="World rule not found"
        )
    return JSONResponse(
        content=success(data=None, message="World rule deleted successfully.")
    )
