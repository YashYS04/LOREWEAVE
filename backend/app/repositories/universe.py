"""Universe repository — all database operations for the Universe model."""

import logging
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.universe import Universe

logger = logging.getLogger(__name__)

# Reusable filter expression: exclude soft-deleted rows.
_ACTIVE = Universe.deleted_at.is_(None)


class UniverseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, universe: Universe) -> Universe:
        self._session.add(universe)
        await self._session.flush()
        await self._session.refresh(universe)
        logger.info("Created universe id=%s slug=%s", universe.id, universe.slug)
        return universe

    async def get_by_id(self, universe_id: str) -> Universe | None:
        result = await self._session.execute(
            select(Universe).where(Universe.id == universe_id, _ACTIVE)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Universe | None:
        result = await self._session.execute(
            select(Universe).where(Universe.slug == slug, _ACTIVE)
        )
        return result.scalar_one_or_none()

    async def slug_exists(self, slug: str) -> bool:
        result = await self._session.execute(
            select(func.count()).where(Universe.slug == slug, _ACTIVE)
        )
        return (result.scalar_one() or 0) > 0

    async def list_all(self, skip: int = 0, limit: int = 50) -> list[Universe]:
        result = await self._session.execute(
            select(Universe)
            .where(_ACTIVE)
            .order_by(Universe.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self._session.execute(
            select(func.count(Universe.id)).where(_ACTIVE)
        )
        return result.scalar_one() or 0

    async def update(self, universe: Universe) -> Universe:
        await self._session.flush()
        await self._session.refresh(universe)
        logger.info("Updated universe id=%s", universe.id)
        return universe

    async def soft_delete(self, universe: Universe) -> None:
        """Set deleted_at instead of removing the row."""
        universe.deleted_at = datetime.now(tz=UTC)
        await self._session.flush()
        logger.info("Soft-deleted universe id=%s", universe.id)
