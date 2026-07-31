"""WorldRule repository."""

from app.models.world_rule import WorldRule
from app.repositories.base import EntityRepository


class WorldRuleRepository(EntityRepository[WorldRule]):
    model = WorldRule
