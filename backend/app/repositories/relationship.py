"""Relationship repository — CRUD + rich filtering for the Universal Relationship Engine."""

import logging
from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.relationship import Relationship

logger = logging.getLogger(__name__)

_ACTIVE = Relationship.deleted_at.is_(None)


class RelationshipRepository:
    """All database operations for Relationship records."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Write operations ───────────────────────────────────────────────────────

    async def create(self, rel: Relationship) -> Relationship:
        self._session.add(rel)
        await self._session.flush()
        await self._session.refresh(rel)
        logger.info(
            "Created relationship id=%s universe=%s type=%s",
            rel.id,
            rel.universe_id,
            rel.relationship_type,
        )
        return rel

    async def update(self, rel: Relationship) -> Relationship:
        await self._session.flush()
        await self._session.refresh(rel)
        logger.info("Updated relationship id=%s", rel.id)
        return rel

    async def soft_delete(self, rel: Relationship) -> None:
        rel.deleted_at = datetime.now(tz=UTC)
        await self._session.flush()
        logger.info("Soft-deleted relationship id=%s", rel.id)

    # ── Read operations ────────────────────────────────────────────────────────

    async def get_by_id(self, rel_id: str) -> Relationship | None:
        result = await self._session.execute(
            select(Relationship).where(Relationship.id == rel_id, _ACTIVE)
        )
        return result.scalar_one_or_none()

    async def list_by_universe(
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
        """Paginated list with optional filters.

        When ``entity_id`` is provided the query returns relationships where that
        entity is either the source OR the target (union).  ``entity_type`` can
        further restrict which side matches.
        """
        base_q = select(Relationship).where(
            Relationship.universe_id == universe_id, _ACTIVE
        )

        # Entity filter — matches source OR target
        if entity_id:
            if entity_type:
                base_q = base_q.where(
                    or_(
                        (
                            (Relationship.source_entity_id == entity_id)
                            & (Relationship.source_entity_type == entity_type)
                        ),
                        (
                            (Relationship.target_entity_id == entity_id)
                            & (Relationship.target_entity_type == entity_type)
                        ),
                    )
                )
            else:
                base_q = base_q.where(
                    or_(
                        Relationship.source_entity_id == entity_id,
                        Relationship.target_entity_id == entity_id,
                    )
                )

        if relationship_type:
            base_q = base_q.where(
                Relationship.relationship_type == relationship_type
            )

        if search:
            pattern = f"%{search}%"
            base_q = base_q.where(
                or_(
                    Relationship.title.ilike(pattern),
                    Relationship.description.ilike(pattern),
                )
            )

        # Count
        count_q = select(func.count()).select_from(base_q.subquery())
        total_result = await self._session.execute(count_q)
        total = total_result.scalar_one() or 0

        # Data
        data_q = (
            base_q
            .order_by(Relationship.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        data_result = await self._session.execute(data_q)
        items = list(data_result.scalars().all())

        return items, total

    async def list_for_context(
        self, universe_id: str, limit: int = 500
    ) -> list[Relationship]:
        """Fetch all active relationships for AI context assembly (no pagination)."""
        result = await self._session.execute(
            select(Relationship)
            .where(Relationship.universe_id == universe_id, _ACTIVE)
            .order_by(Relationship.created_at)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_universe(self, universe_id: str) -> int:
        result = await self._session.execute(
            select(func.count(Relationship.id)).where(
                Relationship.universe_id == universe_id, _ACTIVE
            )
        )
        return result.scalar_one() or 0
