"""WorldRule service."""

from app.models.world_rule import WorldRule
from app.repositories.world_rule import WorldRuleRepository
from app.schemas.world_rule import WorldRuleCreate
from app.services.base import EntityService


class WorldRuleService(EntityService[WorldRule, WorldRuleCreate, object]):
    repo_class = WorldRuleRepository

    def _build(self, payload: WorldRuleCreate, entity_id: str) -> WorldRule:
        return WorldRule(
            id=entity_id,
            universe_id=payload.universe_id,
            title=payload.title,
            category=payload.category,
            description=payload.description,
            limitations=payload.limitations,
            exceptions=payload.exceptions,
            notes=payload.notes,
        )

    def _entity_name(self, entity: WorldRule) -> str:
        return entity.title
