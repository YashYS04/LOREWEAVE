from enum import StrEnum

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.mixins import BaseEntity


class EntityType(StrEnum):
    CHARACTER = "character"
    LOCATION = "location"
    ORGANIZATION = "organization"
    WORLD_OBJECT = "world_object"
    WORLD_RULE = "world_rule"
    character = "character"
    location = "location"
    organization = "organization"
    world_object = "world_object"
    world_rule = "world_rule"


class RelationshipType(StrEnum):
    ALLY_OF = "ally_of"
    ENEMY_OF = "enemy_of"
    LIVES_IN = "lives_in"
    MEMBER_OF = "member_of"
    ally_of = "ally_of"
    enemy_of = "enemy_of"
    lives_in = "lives_in"
    member_of = "member_of"


class RelationshipDirection(StrEnum):
    UNIDIRECTIONAL = "unidirectional"
    BIDIRECTIONAL = "bidirectional"
    unidirectional = "unidirectional"
    bidirectional = "bidirectional"


class Relationship(BaseEntity, Base):
    __tablename__ = "relationships"
    universe_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("universes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_entity_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True
    )
    target_entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_entity_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True
    )
    relationship_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )
    title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    strength: Mapped[int | None] = mapped_column(Integer, nullable=True)
    direction: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="unidirectional"
    )
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
