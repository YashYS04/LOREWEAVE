"""Character CRUD endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.character import (
    CharacterCreate,
    CharacterListResponse,
    CharacterResponse,
    CharacterUpdate,
)
from app.schemas.response import success
from app.services.character import CharacterService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/characters", tags=["characters"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


def _get_service(db: DbDep) -> CharacterService:
    return CharacterService(db)


ServiceDep = Annotated[CharacterService, Depends(_get_service)]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a character",
)
async def create_character(payload: CharacterCreate, svc: ServiceDep) -> JSONResponse:
    character = await svc.create_character(payload)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=success(
            data=CharacterResponse.model_validate(character).model_dump(mode="json"),
            message="Character created successfully.",
        ),
    )


@router.get(
    "",
    summary="List characters by universe",
)
async def list_characters(
    svc: ServiceDep,
    universe_id: Annotated[str, Query(min_length=1)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> JSONResponse:
    characters, total = await svc.list_characters(
        universe_id=universe_id, skip=skip, limit=limit
    )
    payload = CharacterListResponse(
        items=[CharacterResponse.model_validate(c) for c in characters],
        total=total,
        limit=limit,
        offset=skip,
    )
    return JSONResponse(
        content=success(data=payload.model_dump(mode="json"), message="OK")
    )


@router.get(
    "/{character_id}",
    summary="Get a character by ID",
)
async def get_character(character_id: str, svc: ServiceDep) -> JSONResponse:
    character = await svc.get_by_id(character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Character not found"
        )
    return JSONResponse(
        content=success(
            data=CharacterResponse.model_validate(character).model_dump(mode="json"),
            message="OK",
        )
    )


@router.patch(
    "/{character_id}",
    summary="Update a character",
)
async def update_character(
    character_id: str, payload: CharacterUpdate, svc: ServiceDep
) -> JSONResponse:
    character = await svc.update_character(character_id, payload)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Character not found"
        )
    return JSONResponse(
        content=success(
            data=CharacterResponse.model_validate(character).model_dump(mode="json"),
            message="Character updated successfully.",
        )
    )


@router.delete(
    "/{character_id}",
    status_code=status.HTTP_200_OK,
    summary="Soft-delete a character",
)
async def delete_character(character_id: str, svc: ServiceDep) -> JSONResponse:
    deleted = await svc.delete_character(character_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Character not found"
        )
    return JSONResponse(
        content=success(data=None, message="Character deleted successfully.")
    )
