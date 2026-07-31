"""Starter world generator service."""

import asyncio

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.character import CharacterRepository
from app.repositories.location import LocationRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.relationship import RelationshipRepository
from app.repositories.timeline import TimelineRepository
from app.repositories.world_object import WorldObjectRepository
from app.repositories.world_rule import WorldRuleRepository
from app.schemas.character import CharacterCreate
from app.schemas.location import LocationCreate
from app.schemas.organization import OrganizationCreate
from app.schemas.relationship import RelationshipCreate
from app.schemas.timeline import TimelineEventCreate
from app.schemas.world_object import WorldObjectCreate
from app.schemas.world_rule import WorldRuleCreate
from app.services.character import CharacterService
from app.services.location import LocationService
from app.services.organization import OrganizationService
from app.services.relationship import RelationshipService
from app.services.timeline import TimelineService
from app.services.world_object import WorldObjectService
from app.services.world_rule import WorldRuleService


class StarterWorldService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.char_svc = CharacterService(session)
        self.loc_svc = LocationService(session)
        self.org_svc = OrganizationService(session)
        self.obj_svc = WorldObjectService(session)
        self.rule_svc = WorldRuleService(session)
        self.rel_svc = RelationshipService(session)
        self.timeline_svc = TimelineService(session)

        self.char_repo = CharacterRepository(session)
        self.loc_repo = LocationRepository(session)
        self.org_repo = OrganizationRepository(session)
        self.obj_repo = WorldObjectRepository(session)
        self.rule_repo = WorldRuleRepository(session)
        self.rel_repo = RelationshipRepository(session)
        self.timeline_repo = TimelineRepository(session)

    async def generate_starter_world(self, universe_id: str) -> None:
        """Generate a fully interconnected starter world within a single transaction."""
        # 1. Ensure the universe is empty
        counts = await asyncio.gather(
            self.char_repo.count_by_universe(universe_id),
            self.loc_repo.count_by_universe(universe_id),
            self.org_repo.count_by_universe(universe_id),
            self.obj_repo.count_by_universe(universe_id),
            self.rule_repo.count_by_universe(universe_id),
            self.rel_repo.count_by_universe(universe_id),
            self.timeline_repo.count_by_universe(universe_id),
        )
        if sum(counts) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Universe must be empty to generate a starter world",
            )

        # 2. Characters
        char_names = [
            "Queen Elara Solis",
            "Prince Adrian Solis",
            "General Kael Thorn",
            "Archmage Orion Vale",
            "Captain Lyra Ashwind",
            "Scholar Selene Voss",
            "Nyx Ravenshade",
            "Darius Goldcrest",
        ]
        chars = {}
        for name in char_names:
            ent = await self.char_svc.create_character(
                CharacterCreate(
                    universe_id=universe_id,
                    name=name,
                    biography="A generated character in the starter world.",
                )
            )
            chars[name] = ent.id

        # 3. Locations
        loc_names = [
            "Solara Capital",
            "Sunspire Castle",
            "Crystal Forest",
            "Shadow Mountains",
            "Moon Temple",
            "Arcane Academy",
            "Azure Harbor",
            "Whispering Ruins",
        ]
        locs = {}
        for name in loc_names:
            ent = await self.loc_svc.create_location(
                LocationCreate(
                    universe_id=universe_id,
                    name=name,
                    description="A generated location in the starter world.",
                )
            )
            locs[name] = ent.id

        # 4. Organizations
        org_names = [
            "Royal Council",
            "Arcane Guild",
            "Silver Legion",
            "Merchant Alliance",
            "Shadow Order",
        ]
        orgs = {}
        for name in org_names:
            ent = await self.org_svc.create_organization(
                OrganizationCreate(
                    universe_id=universe_id,
                    name=name,
                    description="A generated organization in the starter world.",
                )
            )
            orgs[name] = ent.id

        # 5. World Objects
        obj_names = [
            "Crown of Dawn",
            "Sun Crystal",
            "Blade of Eternity",
            "Ancient Codex",
            "Orb of Echoes",
        ]
        objs = {}
        for name in obj_names:
            ent = await self.obj_svc.create_world_object(
                WorldObjectCreate(
                    universe_id=universe_id,
                    name=name,
                    description="A generated artifact in the starter world.",
                )
            )
            objs[name] = ent.id

        # 6. World Rules
        rule_names = [
            "Magic requires life energy",
            "Only the monarch may wield the Crown of Dawn",
            "The Sun Crystal cannot leave Solara",
            "Time magic is forbidden",
            "Dragons remain neutral in human politics",
        ]
        rules = {}
        for name in rule_names:
            ent = await self.rule_svc.create_world_rule(
                WorldRuleCreate(
                    universe_id=universe_id,
                    name=name,
                    description="A fundamental law of this universe.",
                )
            )
            rules[name] = ent.id

        # 7. Relationships
        # Format: (Source Name, Source Type, Target Name, Target Type, Relationship Type)
        relationships = [
            (
                "Queen Elara Solis",
                "character",
                "Royal Council",
                "organization",
                "member_of",
            ),
            (
                "General Kael Thorn",
                "character",
                "Silver Legion",
                "organization",
                "member_of",
            ),
            (
                "Archmage Orion Vale",
                "character",
                "Arcane Guild",
                "organization",
                "member_of",
            ),
            (
                "Nyx Ravenshade",
                "character",
                "Shadow Order",
                "organization",
                "member_of",
            ),
            (
                "Merchant Alliance",
                "organization",
                "Royal Council",
                "organization",
                "ally_of",
            ),
            (
                "Shadow Order",
                "organization",
                "Royal Council",
                "organization",
                "enemy_of",
            ),
            ("Sunspire Castle", "location", "Solara Capital", "location", "lives_in"),
            ("Arcane Academy", "location", "Solara Capital", "location", "lives_in"),
            ("Moon Temple", "location", "Crystal Forest", "location", "lives_in"),
            ("Crown of Dawn", "world_object", "Queen Elara Solis", "character", "ally_of"),
            (
                "Blade of Eternity",
                "world_object",
                "Whispering Ruins",
                "location",
                "lives_in",
            ),
            ("Sun Crystal", "world_object", "Sunspire Castle", "location", "lives_in"),
        ]

        def get_id(name: str, entity_type: str) -> str:
            if entity_type == "character":
                return chars[name]
            if entity_type == "location":
                return locs[name]
            if entity_type == "organization":
                return orgs[name]
            if entity_type == "world_object":
                return objs[name]
            raise ValueError(f"Unknown entity type: {entity_type}")

        for (
            source_name,
            source_type,
            target_name,
            target_type,
            rel_type,
        ) in relationships:
            await self.rel_svc.create_relationship(
                RelationshipCreate(
                    universe_id=universe_id,
                    source_entity_type=source_type,
                    source_entity_id=get_id(source_name, source_type),
                    target_entity_type=target_type,
                    target_entity_id=get_id(target_name, target_type),
                    relationship_type=rel_type,
                    description=f"{source_name} is {rel_type} {target_name}",
                )
            )

        # 8. Timeline Events
        timeline_events = [
            ("Founding of Solara", 1),
            ("Discovery of the Sun Crystal", 50),
            ("Formation of the Arcane Guild", 120),
            ("The Great Shadow War", 300),
            ("Coronation of Queen Elara", 450),
            ("Rise of the Shadow Order", 452),
            ("Battle of Crystal Pass", 455),
            ("Present Day", 460),
        ]
        for name, year in timeline_events:
            await self.timeline_svc.create_event(
                TimelineEventCreate(
                    universe_id=universe_id,
                    name=name,
                    date_display=f"Year {year}",
                    sort_order=year,
                    description=f"The {name} took place in Year {year}.",
                )
            )
