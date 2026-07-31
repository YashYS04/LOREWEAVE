"""UniverseContextBuilder.

Collects all world-building entities for a given universe from the database
and delegates serialization to the serializer layer.

This class knows about the database but nothing about AI — it is a pure
data-assembly step in the pipeline.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.context.serializer import build_context
from app.ai.schemas.ai import UniverseContext
from app.repositories.character import CharacterRepository
from app.repositories.location import LocationRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.relationship import RelationshipRepository
from app.repositories.timeline import TimelineRepository
from app.repositories.universe import UniverseRepository
from app.repositories.world_object import WorldObjectRepository
from app.repositories.world_rule import WorldRuleRepository

logger = logging.getLogger(__name__)

# Cap the number of entities fetched per category to keep context size sane.
_ENTITY_LIMIT = 200
_RELATIONSHIP_LIMIT = 500
_TIMELINE_LIMIT = 200


class UniverseContextBuilder:
    """Assembles a complete, serialized ``UniverseContext`` for a given universe."""

    def __init__(self, session: AsyncSession) -> None:
        self._universes = UniverseRepository(session)
        self._characters = CharacterRepository(session)
        self._locations = LocationRepository(session)
        self._organizations = OrganizationRepository(session)
        self._objects = WorldObjectRepository(session)
        self._rules = WorldRuleRepository(session)
        self._relationships = RelationshipRepository(session)
        self._timeline = TimelineRepository(session)

    async def build(self, universe_id: str) -> UniverseContext | None:
        """Fetch all universe data and return a serialized context.

        Returns ``None`` if the universe does not exist or has been deleted.
        """
        universe = await self._universes.get_by_id(universe_id)
        if not universe:
            logger.warning(
                "Context build requested for unknown universe_id=%s", universe_id
            )
            return None

        characters = await self._characters.list_by_universe(
            universe_id, limit=_ENTITY_LIMIT
        )
        locations = await self._locations.list_by_universe(
            universe_id, limit=_ENTITY_LIMIT
        )
        organizations = await self._organizations.list_by_universe(
            universe_id, limit=_ENTITY_LIMIT
        )
        objects = await self._objects.list_by_universe(universe_id, limit=_ENTITY_LIMIT)
        rules = await self._rules.list_by_universe(universe_id, limit=_ENTITY_LIMIT)
        relationships = await self._relationships.list_for_context(
            universe_id, limit=_RELATIONSHIP_LIMIT
        )
        timeline_events = await self._timeline.list_for_context(
            universe_id, limit=_TIMELINE_LIMIT
        )

        logger.info(
            "Context built for universe_id=%s: "
            "chars=%d locs=%d orgs=%d objs=%d rules=%d rels=%d events=%d",
            universe_id,
            len(characters),
            len(locations),
            len(organizations),
            len(objects),
            len(rules),
            len(relationships),
            len(timeline_events),
        )

        return build_context(
            universe=universe,
            characters=characters,
            locations=locations,
            organizations=organizations,
            objects=objects,
            world_rules=rules,
            relationships=relationships,
            timeline_events=timeline_events,
        )
