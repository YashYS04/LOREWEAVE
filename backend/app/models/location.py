from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.mixins import BaseEntity


class Location(BaseEntity, Base):
    __tablename__ = "locations"
    universe_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("universes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    climate: Mapped[str | None] = mapped_column(String(200), nullable=True)
    culture: Mapped[str | None] = mapped_column(Text, nullable=True)
    population: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
