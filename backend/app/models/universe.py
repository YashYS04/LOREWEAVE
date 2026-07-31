from enum import StrEnum

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.mixins import BaseEntity


class UniverseStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    draft = "draft"
    active = "active"
    archived = "archived"

class UniverseGenre(StrEnum):
    FANTASY = "fantasy"
    MYSTERY = "mystery"
    HORROR = "horror"
    THRILLER = "thriller"
    ADVENTURE = "adventure"
    ROMANCE = "romance"
    STEAMPUNK = "steampunk"
    CYBERPUNK = "cyberpunk"
    SCI_FI = "sci_fi"
    HISTORICAL = "historical"
    MODERN = "modern"
    OTHER = "other"
    fantasy = "fantasy"
    mystery = "mystery"
    horror = "horror"
    thriller = "thriller"
    adventure = "adventure"
    romance = "romance"
    steampunk = "steampunk"
    cyberpunk = "cyberpunk"
    sci_fi = "sci_fi"
    historical = "historical"
    modern = "modern"
    other = "other"

class Universe(BaseEntity, Base):
    __tablename__ = "universes"
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    genre: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tone: Mapped[str | None] = mapped_column(String(200), nullable=True)
    target_audience: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="draft")
    cover_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
