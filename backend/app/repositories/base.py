"""Generic async repository base.

Provides standard CRUD operations for any SQLAlchemy model that has
``id``, ``universe_id``, and ``deleted_at`` columns (i.e., inherits
``BaseEntity`` and belongs to a Universe).

Usage::

    class LocationRepository(EntityRepository[Location]):
        pass
"""

import logging
from datetime import UTC, datetime
from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")

logger = logging.getLogger(__name__)


class EntityRepository(Generic[ModelT]):  # noqa: UP046
    """Reusable async repository for world-building entities."""

    model: type  # subclasses must set this

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _active(self):
        """Return a filter expression that excludes soft-deleted rows."""
        return self.model.deleted_at.is_(None)

    async def create(self, entity: ModelT) -> ModelT:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def get_by_id(self, entity_id: str) -> ModelT | None:
        result = await self._session.execute(
            select(self.model).where(self.model.id == entity_id, self._active())
        )
        return result.scalar_one_or_none()

    async def list_by_universe(
        self,
        universe_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> list[ModelT]:
        result = await self._session.execute(
            select(self.model)
            .where(self.model.universe_id == universe_id, self._active())
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_universe(self, universe_id: str) -> int:
        result = await self._session.execute(
            select(func.count(self.model.id)).where(
                self.model.universe_id == universe_id, self._active()
            )
        )
        return result.scalar_one() or 0

    async def update(self, entity: ModelT) -> ModelT:
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def soft_delete(self, entity: ModelT) -> None:
        entity.deleted_at = datetime.now(tz=UTC)
        await self._session.flush()
