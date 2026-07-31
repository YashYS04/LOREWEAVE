"""Character service — business logic layer."""

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import audit
from app.models.character import Character
from app.repositories.character import CharacterRepository
from app.schemas.character import CharacterCreate, CharacterUpdate

logger = logging.getLogger(__name__)


class CharacterService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = CharacterRepository(session)

    async def create_character(self, payload: CharacterCreate) -> Character:
        character = Character(
            id=str(uuid.uuid4()),
            universe_id=payload.universe_id,
            name=payload.name,
            role=payload.role,
            age=payload.age,
            gender=payload.gender,
            occupation=payload.occupation,
            biography=payload.biography,
            personality=payload.personality,
            goals=payload.goals,
            motivations=payload.motivations,
            strengths=payload.strengths,
            weaknesses=payload.weaknesses,
            notes=payload.notes,
            status=payload.status.value,
        )
        result = await self._repo.create(character)
        audit.character_created(result.id, result.name, result.universe_id)
        return result

    async def get_by_id(self, character_id: str) -> Character | None:
        return await self._repo.get_by_id(character_id)

    async def list_characters(
        self,
        universe_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Character], int]:
        characters = await self._repo.list_by_universe(
            universe_id=universe_id, skip=skip, limit=limit
        )
        total = await self._repo.count_by_universe(universe_id=universe_id)
        return characters, total

    async def update_character(
        self, character_id: str, payload: CharacterUpdate
    ) -> Character | None:
        character = await self._repo.get_by_id(character_id)
        if not character:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "status" and value is not None:
                value = value.value if hasattr(value, "value") else value
            setattr(character, field, value)

        result = await self._repo.update(character)
        audit.character_updated(result.id, result.name)
        return result

    async def delete_character(self, character_id: str) -> bool:
        character = await self._repo.get_by_id(character_id)
        if not character:
            return False
        await self._repo.soft_delete(character)
        audit.character_deleted(character.id, character.name)
        return True
