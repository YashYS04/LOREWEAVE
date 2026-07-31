"""Pydantic v2 schemas for the Universe resource."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.universe import UniverseGenre, UniverseStatus


class UniverseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    genre: UniverseGenre
    description: str | None = Field(None, max_length=3000)
    tone: str | None = Field(None, max_length=200)
    target_audience: str | None = Field(None, max_length=200)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be blank")
        return v.strip()


class UniverseUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=120)
    genre: UniverseGenre | None = None
    description: str | None = Field(None, max_length=3000)
    tone: str | None = Field(None, max_length=200)
    target_audience: str | None = Field(None, max_length=200)
    status: UniverseStatus | None = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("name must not be blank")
        return v.strip() if v else v


class UniverseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    genre: str
    description: str | None
    tone: str | None
    target_audience: str | None
    status: str
    cover_image: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class UniverseListResponse(BaseModel):
    """Paginated list response — includes pagination metadata."""

    items: list[UniverseResponse]
    total: int
    limit: int
    offset: int
