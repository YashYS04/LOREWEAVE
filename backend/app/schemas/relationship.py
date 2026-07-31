"""Pydantic v2 schemas for the Relationship resource."""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.relationship import (
    EntityType,
    RelationshipDirection,
    RelationshipType,
)


def _orm_to_dict(rel: Any) -> dict[str, Any]:
    """Convert a Relationship ORM object to a plain dict for Pydantic validation.

    SQLAlchemy models expose a class-level ``metadata`` attribute (the
    ``MetaData`` object) which shadows our field.  We read ``metadata_json``
    directly and decode it ourselves.
    """
    raw_meta = getattr(rel, "metadata_json", None)
    meta: dict[str, Any] | None = None
    if isinstance(raw_meta, str):
        try:
            meta = json.loads(raw_meta)
        except (json.JSONDecodeError, TypeError):
            meta = None

    return {
        "id": rel.id,
        "universe_id": rel.universe_id,
        "source_entity_type": rel.source_entity_type,
        "source_entity_id": rel.source_entity_id,
        "target_entity_type": rel.target_entity_type,
        "target_entity_id": rel.target_entity_id,
        "relationship_type": rel.relationship_type,
        "title": rel.title,
        "description": rel.description,
        "strength": rel.strength,
        "direction": rel.direction,
        "metadata": meta,
        "created_at": rel.created_at,
        "updated_at": rel.updated_at,
        "deleted_at": rel.deleted_at,
    }


class RelationshipCreate(BaseModel):
    universe_id: str = Field(..., min_length=1)
    source_entity_type: EntityType
    source_entity_id: str = Field(..., min_length=1)
    target_entity_type: EntityType
    target_entity_id: str = Field(..., min_length=1)
    relationship_type: RelationshipType
    title: str | None = Field(None, max_length=300)
    description: str | None = Field(None, max_length=5000)
    strength: int | None = Field(None, ge=1, le=10)
    direction: RelationshipDirection = RelationshipDirection.UNIDIRECTIONAL
    metadata: dict[str, Any] | None = None

    @field_validator("source_entity_id", "target_entity_id")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("entity id must not be blank")
        return v.strip()

    @model_validator(mode="after")
    def source_and_target_differ(self) -> "RelationshipCreate":
        if (
            self.source_entity_type == self.target_entity_type
            and self.source_entity_id == self.target_entity_id
        ):
            raise ValueError("A relationship cannot connect an entity to itself.")
        return self


class RelationshipUpdate(BaseModel):
    relationship_type: RelationshipType | None = None
    title: str | None = Field(None, max_length=300)
    description: str | None = Field(None, max_length=5000)
    strength: int | None = Field(None, ge=1, le=10)
    direction: RelationshipDirection | None = None
    metadata: dict[str, Any] | None = None


class RelationshipResponse(BaseModel):
    """Read model for a Relationship.

    Always constructed from a plain dict via ``_orm_to_dict()`` to avoid
    SQLAlchemy's class-level ``metadata`` attribute shadowing.
    """

    id: str
    universe_id: str
    source_entity_type: str
    source_entity_id: str
    target_entity_type: str
    target_entity_id: str
    relationship_type: str
    title: str | None
    description: str | None
    strength: int | None
    direction: str
    metadata: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    @classmethod
    def from_orm(cls, rel: Any) -> "RelationshipResponse":
        """Construct from an ORM Relationship instance."""
        return cls.model_validate(_orm_to_dict(rel))


class RelationshipListResponse(BaseModel):
    items: list[RelationshipResponse]
    total: int
    limit: int
    offset: int
