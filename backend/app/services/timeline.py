"""Timeline service — business logic for the Timeline Intelligence Engine."""

import json
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import audit
from app.models.timeline import TimelineEvent, TimelineParticipant
from app.repositories.timeline import TimelineRepository
from app.schemas.timeline import TimelineEventCreate, TimelineEventUpdate

logger = logging.getLogger(__name__)


class TimelineService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = TimelineRepository(session)

    async def create_event(self, payload: TimelineEventCreate) -> TimelineEvent:
        metadata_json: str | None = None
        if payload.metadata is not None:
            metadata_json = json.dumps(payload.metadata)

        event = TimelineEvent(
            id=str(uuid.uuid4()),
            universe_id=payload.universe_id,
            title=payload.title,
            description=payload.description,
            event_type=payload.event_type.value,
            status=payload.status.value,
            start_date=payload.start_date,
            end_date=payload.end_date,
            importance=payload.importance,
            metadata_json=metadata_json,
        )

        created = await self._repo.create(event)

        # Attach participants if provided
        if payload.participants:
            participants = [
                TimelineParticipant(
                    id=str(uuid.uuid4()),
                    event_id=created.id,
                    entity_type=p.entity_type.value,
                    entity_id=p.entity_id,
                    role=p.role,
                )
                for p in payload.participants
            ]
            await self._repo.replace_participants(created.id, participants)
            # Reload to reflect new participants
            result = await self._repo.get_by_id(created.id)
            if result:
                created = result

        audit.timeline_event_created(created.id, created.title, created.universe_id)
        return created

    async def get_by_id(self, event_id: str) -> TimelineEvent | None:
        return await self._repo.get_by_id(event_id)

    async def list_events(
        self,
        universe_id: str,
        skip: int = 0,
        limit: int = 50,
        *,
        event_type: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> tuple[list[TimelineEvent], int]:
        return await self._repo.list_by_universe(
            universe_id,
            skip=skip,
            limit=limit,
            event_type=event_type,
            status=status,
            search=search,
        )

    async def update_event(
        self, event_id: str, payload: TimelineEventUpdate
    ) -> TimelineEvent | None:
        event = await self._repo.get_by_id(event_id)
        if not event:
            return None

        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field == "metadata":
                event.metadata_json = json.dumps(value) if value is not None else None
            elif field == "participants":
                # handled separately below
                continue
            elif field in ("event_type", "status") and value is not None:
                setattr(event, field, value.value if hasattr(value, "value") else value)
            else:
                setattr(event, field, value)

        updated = await self._repo.update(event)

        # Replace participants if explicitly provided in the payload
        if "participants" in update_data and update_data["participants"] is not None:
            participants = [
                TimelineParticipant(
                    id=str(uuid.uuid4()),
                    event_id=updated.id,
                    entity_type=p.entity_type.value,
                    entity_id=p.entity_id,
                    role=p.role,
                )
                for p in payload.participants  # type: ignore[union-attr]
            ]
            await self._repo.replace_participants(updated.id, participants)
            result = await self._repo.get_by_id(updated.id)
            if result:
                updated = result

        audit.timeline_event_updated(updated.id, updated.title)
        return updated

    async def delete_event(self, event_id: str) -> bool:
        event = await self._repo.get_by_id(event_id)
        if not event:
            return False
        await self._repo.soft_delete(event)
        audit.timeline_event_deleted(event.id, event.title)
        return True
