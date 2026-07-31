from enum import StrEnum

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import BaseEntity


class EventType(StrEnum):
    CUSTOM = "custom"
    BATTLE = "battle"
    CORONATION = "coronation"
    TREATY = "treaty"
    DISCOVERY = "discovery"
    BIRTH = "birth"
    DEATH = "death"
    DISASTER = "disaster"
    custom = "custom"
    battle = "battle"
    coronation = "coronation"
    treaty = "treaty"
    discovery = "discovery"
    birth = "birth"
    death = "death"
    disaster = "disaster"

class EventStatus(StrEnum):
    COMPLETED = "completed"
    completed = "completed"

class ParticipantEntityType(StrEnum):
    CHARACTER = "character"
    LOCATION = "location"
    ORGANIZATION = "organization"
    WORLD_OBJECT = "world_object"
    character = "character"
    location = "location"
    organization = "organization"
    world_object = "world_object"

class TimelineEvent(BaseEntity, Base):
    __tablename__ = "timeline_events"
    universe_id: Mapped[str] = mapped_column(String(36), ForeignKey("universes.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, server_default="custom", index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="completed")
    start_date: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    end_date: Mapped[str | None] = mapped_column(String(100), nullable=True)
    importance: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    participants: Mapped[list["TimelineParticipant"]] = relationship("TimelineParticipant", cascade="all, delete-orphan")

class TimelineParticipant(Base):
    __tablename__ = "timeline_participants"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    event_id: Mapped[str] = mapped_column(String(36), ForeignKey("timeline_events.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    role: Mapped[str | None] = mapped_column(String(200), nullable=True)
