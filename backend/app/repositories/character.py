"""Character repository — all database operations for the Character model."""

import logging
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.character import Character

logger = logging.getLogger(__name__)

_ACTIVE = Character.deleted_at.is_(None)


class CharacterRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, character: Character) -> Character:
        self._session.add(character)
        await self._session.flush()
        await self._session.refresh(character)
        logger.info(
            "Created character id=%s name=%s universe_id=%s",
            character.id,
            character.name,
            character.universe_id,
        )
        return character

    async def get_by_id(self, character_id: str) -> Character | None:
        result = await self._session.execute(
            select(Character).where(Character.id == character_id, _ACTIVE)
        )
        return result.scalar_one_or_none()

    async def list_by_universe(
        self,
        universe_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Character]:
        result = await self._session.execute(
            select(Character)
            .where(Character.universe_id == universe_id, _ACTIVE)
            .order_by(Character.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_universe(self, universe_id: str) -> int:
        result = await self._session.execute(
            select(func.count(Character.id)).where(
                Character.universe_id == universe_id, _ACTIVE
            )
        )
        return result.scalar_one() or 0

    async def update(self, character: Character) -> Character:
        await self._session.flush()
        await self._session.refresh(character)
        logger.info("Updated character id=%s", character.id)
        return character

    async def soft_delete(self, character: Character) -> None:
        character.deleted_at = datetime.now(tz=UTC)
        await self._session.flush()
        logger.info("Soft-deleted character id=%s", character.id)
