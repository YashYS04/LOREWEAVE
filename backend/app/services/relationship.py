"""Relationship service — business logic for the Universal Relationship Engine."""

import json
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import audit
from app.models.relationship import (
    Relationship,
)
from app.repositories.relationship import RelationshipRepository
from app.schemas.relationship import RelationshipCreate, RelationshipUpdate

logger = logging.getLogger(__name__)


class RelationshipService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = RelationshipRepository(session)

    async def create_relationship(self, payload: RelationshipCreate) -> Relationship:
        metadata_json: str | None = None
        if payload.metadata is not None:
            metadata_json = json.dumps(payload.metadata)

        rel = Relationship(
            id=str(uuid.uuid4()),
            universe_id=payload.universe_id,
            source_entity_type=payload.source_entity_type.value,
            source_entity_id=payload.source_entity_id,
            target_entity_type=payload.target_entity_type.value,
            target_entity_id=payload.target_entity_id,
            relationship_type=payload.relationship_type.value,
            title=payload.title,
            description=payload.description,
            strength=payload.strength,
            direction=payload.direction.value,
            metadata_json=metadata_json,
        )
        result = await self._repo.create(rel)
        audit.relationship_created(
            result.id, result.relationship_type, result.universe_id
        )
        return result

    async def get_by_id(self, rel_id: str) -> Relationship | None:
        return await self._repo.get_by_id(rel_id)

    async def list_relationships(
        self,
        universe_id: str,
        skip: int = 0,
        limit: int = 50,
        *,
        entity_id: str | None = None,
        entity_type: str | None = None,
        relationship_type: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Relationship], int]:
        return await self._repo.list_by_universe(
            universe_id,
            skip=skip,
            limit=limit,
            entity_id=entity_id,
            entity_type=entity_type,
            relationship_type=relationship_type,
            search=search,
        )

    async def update_relationship(
        self, rel_id: str, payload: RelationshipUpdate
    ) -> Relationship | None:
        rel = await self._repo.get_by_id(rel_id)
        if not rel:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "metadata":
                rel.metadata_json = json.dumps(value) if value is not None else None
            elif field in ("relationship_type", "direction") and value is not None:
                setattr(rel, field, value.value if hasattr(value, "value") else value)
            else:
                setattr(rel, field, value)

        result = await self._repo.update(rel)
        audit.relationship_updated(result.id, result.relationship_type)
        return result

    async def delete_relationship(self, rel_id: str) -> bool:
        rel = await self._repo.get_by_id(rel_id)
        if not rel:
            return False
        await self._repo.soft_delete(rel)
        audit.relationship_deleted(rel.id, rel.relationship_type)
        return True
