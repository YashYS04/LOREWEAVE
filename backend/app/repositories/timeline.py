"""Timeline repository — CRUD + filtering for TimelineEvent records."""

import logging
from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.timeline import TimelineEvent, TimelineParticipant

logger = logging.getLogger(__name__)

_ACTIVE = TimelineEvent.deleted_at.is_(None)


class TimelineRepository:
    """All database operations for TimelineEvent and TimelineParticipant."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Write operations ───────────────────────────────────────────────────────

    async def create(self, event: TimelineEvent) -> TimelineEvent:
        self._session.add(event)
        await self._session.flush()
        # Reload with participants eager-loaded
        return await self._load_with_participants(event.id)  # type: ignore[return-value]

    async def update(self, event: TimelineEvent) -> TimelineEvent:
        await self._session.flush()
        return await self._load_with_participants(event.id)  # type: ignore[return-value]

    async def soft_delete(self, event: TimelineEvent) -> None:
        event.deleted_at = datetime.now(tz=UTC)
        await self._session.flush()
        logger.info("Soft-deleted timeline event id=%s", event.id)

    async def replace_participants(
        self,
        event_id: str,
        participants: list[TimelineParticipant],
    ) -> None:
        """Delete existing participants for the event, then add the new list."""
        existing = await self._session.execute(
            select(TimelineParticipant).where(TimelineParticipant.event_id == event_id)
        )
        for p in existing.scalars().all():
            await self._session.delete(p)
        await self._session.flush()

        for p in participants:
            self._session.add(p)
        await self._session.flush()

    # ── Read operations ────────────────────────────────────────────────────────

    async def get_by_id(self, event_id: str) -> TimelineEvent | None:
        result = await self._session.execute(
            select(TimelineEvent)
            .options(selectinload(TimelineEvent.participants))
            .where(TimelineEvent.id == event_id, _ACTIVE)
            .execution_options(populate_existing=True)
        )
        return result.scalar_one_or_none()

    async def list_by_universe(
        self,
        universe_id: str,
        skip: int = 0,
        limit: int = 50,
        *,
        event_type: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> tuple[list[TimelineEvent], int]:
        """Paginated list with optional filters."""
        base_q = select(TimelineEvent).where(
            TimelineEvent.universe_id == universe_id, _ACTIVE
        )

        if event_type:
            base_q = base_q.where(TimelineEvent.event_type == event_type)

        if status:
            base_q = base_q.where(TimelineEvent.status == status)

        if search:
            pattern = f"%{search}%"
            base_q = base_q.where(
                or_(
                    TimelineEvent.title.ilike(pattern),
                    TimelineEvent.description.ilike(pattern),
                )
            )

        # Count
        count_q = select(func.count()).select_from(base_q.subquery())
        total_result = await self._session.execute(count_q)
        total = total_result.scalar_one() or 0

        # Data — order by start_date (alphabetical works for fantasy dates too),
        # then by created_at for stability
        data_q = (
            base_q.options(selectinload(TimelineEvent.participants))
            .order_by(
                TimelineEvent.start_date.asc().nulls_last(),
                TimelineEvent.created_at.asc(),
            )
            .offset(skip)
            .limit(limit)
        )
        data_result = await self._session.execute(data_q)
        items = list(data_result.scalars().all())

        return items, total

    async def list_for_context(
        self, universe_id: str, limit: int = 200
    ) -> list[TimelineEvent]:
        """Fetch active events ordered by start_date for AI context assembly."""
        result = await self._session.execute(
            select(TimelineEvent)
            .options(selectinload(TimelineEvent.participants))
            .where(TimelineEvent.universe_id == universe_id, _ACTIVE)
            .order_by(
                TimelineEvent.start_date.asc().nulls_last(),
                TimelineEvent.created_at.asc(),
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_universe(self, universe_id: str) -> int:
        result = await self._session.execute(
            select(func.count(TimelineEvent.id)).where(
                TimelineEvent.universe_id == universe_id, _ACTIVE
            )
        )
        return result.scalar_one() or 0

    # ── Helpers ────────────────────────────────────────────────────────────────

    async def _load_with_participants(self, event_id: str) -> TimelineEvent | None:
        result = await self._session.execute(
            select(TimelineEvent)
            .options(selectinload(TimelineEvent.participants))
            .where(TimelineEvent.id == event_id)
            .execution_options(populate_existing=True)
        )
        return result.scalar_one_or_none()
