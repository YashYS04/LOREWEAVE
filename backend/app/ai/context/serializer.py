"""Universe context serializer.

Converts raw ORM objects into clean, AI-ready Pydantic snippets.
The service layer and prompt templates must never touch SQLAlchemy models
directly — this module is the only translation layer between the
database and the AI pipeline.
"""

from datetime import UTC, datetime

from app.ai.schemas.ai import (
    CharacterSnippet,
    ContextMetadata,
    LocationSnippet,
    OrganizationSnippet,
    RelationshipSnippet,
    TimelineEventSnippet,
    UniverseContext,
    UniverseSnippet,
    WorldObjectSnippet,
    WorldRuleSnippet,
)
from app.core.config import settings
from app.models.character import Character
from app.models.location import Location
from app.models.organization import Organization
from app.models.relationship import Relationship
from app.models.timeline import TimelineEvent
from app.models.universe import Universe
from app.models.world_object import WorldObject
from app.models.world_rule import WorldRule


def serialize_universe(universe: Universe) -> UniverseSnippet:
    return UniverseSnippet(
        id=universe.id,
        name=universe.name,
        genre=universe.genre,
        description=universe.description,
        tone=universe.tone,
        status=universe.status,
    )


def serialize_character(character: Character) -> CharacterSnippet:
    return CharacterSnippet(
        id=character.id,
        name=character.name,
        role=character.role,
        biography=character.biography,
        personality=character.personality,
        goals=character.goals,
        motivations=character.motivations,
        strengths=character.strengths,
        weaknesses=character.weaknesses,
    )


def serialize_location(location: Location) -> LocationSnippet:
    return LocationSnippet(
        id=location.id,
        name=location.name,
        type=location.type,
        description=location.description,
        climate=location.climate,
        culture=location.culture,
    )


def serialize_organization(org: Organization) -> OrganizationSnippet:
    return OrganizationSnippet(
        id=org.id,
        name=org.name,
        type=org.type,
        description=org.description,
        leader=org.leader,
        purpose=org.purpose,
    )


def serialize_world_object(obj: WorldObject) -> WorldObjectSnippet:
    return WorldObjectSnippet(
        id=obj.id,
        name=obj.name,
        category=obj.category,
        description=obj.description,
        origin=obj.origin,
        abilities=obj.abilities,
    )


def serialize_world_rule(rule: WorldRule) -> WorldRuleSnippet:
    return WorldRuleSnippet(
        id=rule.id,
        title=rule.title,
        category=rule.category,
        description=rule.description,
        limitations=rule.limitations,
        exceptions=rule.exceptions,
    )


def _resolve_entity_name(
    entity_id: str,
    entity_type: str,
    chars: list[Character],
    locs: list[Location],
    orgs: list[Organization],
    objs: list[WorldObject],
    rules: list[WorldRule],
) -> str:
    """Return a human-readable name for an entity, falling back to its ID."""
    lookups: dict[str, dict[str, str]] = {
        "character": {c.id: c.name for c in chars},
        "location": {lo.id: lo.name for lo in locs},
        "organization": {o.id: o.name for o in orgs},
        "object": {ob.id: ob.name for ob in objs},
        "world_rule": {r.id: r.title for r in rules},
    }
    return lookups.get(entity_type, {}).get(entity_id, entity_id)


def serialize_relationship(
    rel: Relationship,
    chars: list[Character],
    locs: list[Location],
    orgs: list[Organization],
    objs: list[WorldObject],
    rules: list[WorldRule],
) -> RelationshipSnippet:
    source_name = _resolve_entity_name(
        rel.source_entity_id, rel.source_entity_type, chars, locs, orgs, objs, rules
    )
    target_name = _resolve_entity_name(
        rel.target_entity_id, rel.target_entity_type, chars, locs, orgs, objs, rules
    )
    return RelationshipSnippet(
        id=rel.id,
        source=source_name,
        source_type=rel.source_entity_type,
        relationship=rel.relationship_type,
        target=target_name,
        target_type=rel.target_entity_type,
        strength=rel.strength,
        direction=rel.direction,
        description=rel.description,
    )


def serialize_timeline_event(event: TimelineEvent) -> TimelineEventSnippet:
    """Convert a TimelineEvent ORM into an AI-ready snippet."""
    participant_summaries: list[str] = []
    for p in event.participants or []:
        summary = f"{p.entity_type}:{p.entity_id}"
        if p.role:
            summary += f" ({p.role})"
        participant_summaries.append(summary)

    return TimelineEventSnippet(
        id=event.id,
        title=event.title,
        event_type=event.event_type,
        status=event.status,
        start_date=event.start_date,
        end_date=event.end_date,
        importance=event.importance,
        description=event.description,
        participants=participant_summaries,
    )


def build_context(
    universe: Universe,
    characters: list[Character],
    locations: list[Location],
    organizations: list[Organization],
    objects: list[WorldObject],
    world_rules: list[WorldRule],
    relationships: list[Relationship] | None = None,
    timeline_events: list[TimelineEvent] | None = None,
) -> UniverseContext:
    """Assemble a fully-serialized UniverseContext from ORM collections."""
    rels = relationships or []
    events = timeline_events or []
    metadata = ContextMetadata(
        generated_at=datetime.now(tz=UTC),
        counts={
            "characters": len(characters),
            "locations": len(locations),
            "organizations": len(organizations),
            "objects": len(objects),
            "world_rules": len(world_rules),
            "relationships": len(rels),
            "timeline_events": len(events),
        },
        version=settings.APP_VERSION,
    )

    return UniverseContext(
        universe=serialize_universe(universe),
        characters=[serialize_character(c) for c in characters],
        locations=[serialize_location(loc) for loc in locations],
        organizations=[serialize_organization(o) for o in organizations],
        objects=[serialize_world_object(o) for o in objects],
        world_rules=[serialize_world_rule(r) for r in world_rules],
        relationships=[
            serialize_relationship(
                r, characters, locations, organizations, objects, world_rules
            )
            for r in rels
        ],
        timeline=[serialize_timeline_event(e) for e in events],
        metadata=metadata,
    )
