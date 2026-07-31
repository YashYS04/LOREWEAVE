"""Generic entity service base.

Subclasses wire a concrete repository and a Pydantic create/update schema
to provide standard CRUD with universe-scoped listing.

Usage::

    class LocationService(EntityService[Location, LocationCreate, LocationUpdate]):
        repo_class = LocationRepository

        def _build(self, payload: LocationCreate, entity_id: str) -> Location:
            return Location(id=entity_id, **payload.model_dump())
"""

import logging
import uuid
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import audit

ModelT = TypeVar("ModelT")
CreateT = TypeVar("CreateT")
UpdateT = TypeVar("UpdateT")

logger = logging.getLogger(__name__)


class EntityService(Generic[ModelT, CreateT, UpdateT]):  # noqa: UP046
    """Reusable CRUD service for world-building entities."""

    repo_class: type  # concrete EntityRepository subclass

    def __init__(self, session: AsyncSession) -> None:
        self._repo = self.repo_class(session)

    def _build(self, payload: CreateT, entity_id: str) -> ModelT:  # type: ignore[misc]
        """Construct a new ORM instance from a create payload.

        Subclasses must override this method.
        """
        raise NotImplementedError

    def _entity_name(self, entity: ModelT) -> str:  # type: ignore[misc]
        """Return a human-readable name for audit logging."""
        return getattr(entity, "name", None) or getattr(entity, "title", str(entity))

    async def create(self, payload: CreateT) -> ModelT:  # type: ignore[misc]
        entity = self._build(payload, str(uuid.uuid4()))
        result = await self._repo.create(entity)
        audit.entity_created(
            result.__class__.__tablename__,  # type: ignore[attr-defined]
            result.id,  # type: ignore[attr-defined]
            self._entity_name(result),
        )
        return result

    async def get_by_id(self, entity_id: str) -> ModelT | None:  # type: ignore[misc]
        return await self._repo.get_by_id(entity_id)

    async def list_entities(
        self,
        universe_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[ModelT], int]:  # type: ignore[misc]
        items = await self._repo.list_by_universe(
            universe_id=universe_id, skip=skip, limit=limit
        )
        total = await self._repo.count_by_universe(universe_id=universe_id)
        return items, total

    async def update(
        self,
        entity_id: str,
        payload: UpdateT,  # type: ignore[misc]
    ) -> ModelT | None:  # type: ignore[misc]
        entity = await self._repo.get_by_id(entity_id)
        if not entity:
            return None
        for field, value in payload.model_dump(exclude_unset=True).items():  # type: ignore[union-attr]
            setattr(entity, field, value)
        result = await self._repo.update(entity)
        audit.entity_updated(
            result.__class__.__tablename__,  # type: ignore[attr-defined]
            result.id,  # type: ignore[attr-defined]
            self._entity_name(result),
        )
        return result

    async def delete(self, entity_id: str) -> bool:
        entity = await self._repo.get_by_id(entity_id)
        if not entity:
            return False
        await self._repo.soft_delete(entity)
        audit.entity_deleted(
            entity.__class__.__tablename__,  # type: ignore[attr-defined]
            entity.id,  # type: ignore[attr-defined]
            self._entity_name(entity),
        )
        return True
