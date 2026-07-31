"""Timeline CRUD endpoints — Timeline Intelligence Engine.

POST   /api/v1/timeline/events
GET    /api/v1/timeline/events?universe_id=X
GET    /api/v1/timeline/events/{id}
PATCH  /api/v1/timeline/events/{id}
DELETE /api/v1/timeline/events/{id}
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.response import success
from app.schemas.timeline import (
    TimelineEventCreate,
    TimelineEventListResponse,
    TimelineEventResponse,
    TimelineEventUpdate,
)
from app.services.timeline import TimelineService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/timeline/events", tags=["timeline"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


def _get_service(db: DbDep) -> TimelineService:
    return TimelineService(db)


ServiceDep = Annotated[TimelineService, Depends(_get_service)]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a timeline event",
)
async def create_event(payload: TimelineEventCreate, svc: ServiceDep) -> JSONResponse:
    event = await svc.create_event(payload)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=success(
            data=TimelineEventResponse.from_orm(event).model_dump(mode="json"),
            message="Timeline event created.",
        ),
    )


@router.get(
    "",
    summary="List timeline events for a universe",
)
async def list_events(
    svc: ServiceDep,
    universe_id: Annotated[str, Query(min_length=1)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    event_type: Annotated[str | None, Query()] = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    search: Annotated[str | None, Query()] = None,
) -> JSONResponse:
    items, total = await svc.list_events(
        universe_id,
        skip=skip,
        limit=limit,
        event_type=event_type,
        status=status_filter,
        search=search,
    )
    payload = TimelineEventListResponse(
        items=[TimelineEventResponse.from_orm(e) for e in items],
        total=total,
        limit=limit,
        offset=skip,
    )
    return JSONResponse(content=success(data=payload.model_dump(mode="json"), message="OK"))


@router.get(
    "/{event_id}",
    summary="Get a timeline event by ID",
)
async def get_event(event_id: str, svc: ServiceDep) -> JSONResponse:
    event = await svc.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return JSONResponse(
        content=success(
            data=TimelineEventResponse.from_orm(event).model_dump(mode="json"),
            message="OK",
        )
    )


@router.patch(
    "/{event_id}",
    summary="Update a timeline event",
)
async def update_event(
    event_id: str, payload: TimelineEventUpdate, svc: ServiceDep
) -> JSONResponse:
    event = await svc.update_event(event_id, payload)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return JSONResponse(
        content=success(
            data=TimelineEventResponse.from_orm(event).model_dump(mode="json"),
            message="Timeline event updated.",
        )
    )


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_200_OK,
    summary="Soft-delete a timeline event",
)
async def delete_event(event_id: str, svc: ServiceDep) -> JSONResponse:
    deleted = await svc.delete_event(event_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return JSONResponse(content=success(data=None, message="Timeline event deleted."))
