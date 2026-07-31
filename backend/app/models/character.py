from enum import StrEnum

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.mixins import BaseEntity


class CharacterStatus(StrEnum):
    ACTIVE = "active"
    DECEASED = "deceased"
    UNKNOWN = "unknown"
    ARCHIVED = "archived"
    active = "active"
    deceased = "deceased"
    unknown = "unknown"
    archived = "archived"


class Character(BaseEntity, Base):
    __tablename__ = "characters"
    universe_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("universes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str | None] = mapped_column(String(200), nullable=True)
    age: Mapped[str | None] = mapped_column(String(50), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(100), nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(200), nullable=True)
    biography: Mapped[str | None] = mapped_column(Text, nullable=True)
    personality: Mapped[str | None] = mapped_column(Text, nullable=True)
    goals: Mapped[str | None] = mapped_column(Text, nullable=True)
    motivations: Mapped[str | None] = mapped_column(Text, nullable=True)
    strengths: Mapped[str | None] = mapped_column(Text, nullable=True)
    weaknesses: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="active"
    )
