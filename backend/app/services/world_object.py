"""WorldObject service."""

from app.models.world_object import WorldObject
from app.repositories.world_object import WorldObjectRepository
from app.schemas.world_object import WorldObjectCreate
from app.services.base import EntityService


class WorldObjectService(EntityService[WorldObject, WorldObjectCreate, object]):
    repo_class = WorldObjectRepository

    def _build(self, payload: WorldObjectCreate, entity_id: str) -> WorldObject:
        return WorldObject(
            id=entity_id,
            universe_id=payload.universe_id,
            name=payload.name,
            category=payload.category,
            description=payload.description,
            origin=payload.origin,
            owner=payload.owner,
            abilities=payload.abilities,
            notes=payload.notes,
        )
