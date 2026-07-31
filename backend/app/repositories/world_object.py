"""WorldObject repository."""

from app.models.world_object import WorldObject
from app.repositories.base import EntityRepository


class WorldObjectRepository(EntityRepository[WorldObject]):
    model = WorldObject
