"""Pydantic v2 schemas for the Timeline resource."""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.models.timeline import EventStatus, EventType, ParticipantEntityType

# ── Participant schemas ─────────────────────────────────────────────────────────


class ParticipantCreate(BaseModel):
    entity_type: ParticipantEntityType
    entity_id: str = Field(..., min_length=1)
    role: str | None = Field(None, max_length=200)


class ParticipantResponse(BaseModel):
    id: str
    event_id: str
    entity_type: str
    entity_id: str
    role: str | None

    model_config = {"from_attributes": True}


# ── TimelineEvent schemas ──────────────────────────────────────────────────────


class TimelineEventCreate(BaseModel):
    universe_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=300)
    description: str | None = Field(None, max_length=10000)
    event_type: EventType = EventType.CUSTOM
    status: EventStatus = EventStatus.COMPLETED
    start_date: str | None = Field(None, max_length=100)
    end_date: str | None = Field(None, max_length=100)
    importance: int | None = Field(None, ge=1, le=10)
    metadata: dict[str, Any] | None = None
    participants: list[ParticipantCreate] = []

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be blank")
        return v.strip()


class TimelineEventUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=300)
    description: str | None = Field(None, max_length=10000)
    event_type: EventType | None = None
    status: EventStatus | None = None
    start_date: str | None = Field(None, max_length=100)
    end_date: str | None = Field(None, max_length=100)
    importance: int | None = Field(None, ge=1, le=10)
    metadata: dict[str, Any] | None = None
    participants: list[ParticipantCreate] | None = (
        None  # None = no change; [] = clear all
    )


class TimelineEventResponse(BaseModel):
    """Read model for a TimelineEvent.

    Uses ``from_attributes=True`` so it can be built from SQLAlchemy ORM
    instances.  ``metadata`` is decoded from ``metadata_json`` via
    ``model_validator``/``field_validator`` approach.
    """

    id: str
    universe_id: str
    title: str
    description: str | None
    event_type: str
    status: str
    start_date: str | None
    end_date: str | None
    importance: int | None
    metadata: dict[str, Any] | None = None
    participants: list[ParticipantResponse] = []
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, event: Any) -> "TimelineEventResponse":
        """Construct from an ORM TimelineEvent instance.

        Decodes ``metadata_json`` TEXT → dict to avoid field shadowing.
        """
        raw_meta = getattr(event, "metadata_json", None)
        meta: dict[str, Any] | None = None
        if isinstance(raw_meta, str):
            try:
                meta = json.loads(raw_meta)
            except (json.JSONDecodeError, TypeError):
                meta = None

        return cls.model_validate(
            {
                "id": event.id,
                "universe_id": event.universe_id,
                "title": event.title,
                "description": event.description,
                "event_type": event.event_type,
                "status": event.status,
                "start_date": event.start_date,
                "end_date": event.end_date,
                "importance": event.importance,
                "metadata": meta,
                "participants": [
                    {
                        "id": p.id,
                        "event_id": p.event_id,
                        "entity_type": p.entity_type,
                        "entity_id": p.entity_id,
                        "role": p.role,
                    }
                    for p in (event.participants or [])
                ],
                "created_at": event.created_at,
                "updated_at": event.updated_at,
                "deleted_at": event.deleted_at,
            }
        )


class TimelineEventListResponse(BaseModel):
    items: list[TimelineEventResponse]
    total: int
    limit: int
    offset: int
