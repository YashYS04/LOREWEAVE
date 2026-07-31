"""Pydantic v2 schemas for the Character resource."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.character import CharacterStatus


class CharacterCreate(BaseModel):
    universe_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=200)
    role: str | None = Field(None, max_length=200)
    age: str | None = Field(None, max_length=50)
    gender: str | None = Field(None, max_length=100)
    occupation: str | None = Field(None, max_length=200)
    biography: str | None = Field(None, max_length=5000)
    personality: str | None = Field(None, max_length=2000)
    goals: str | None = Field(None, max_length=2000)
    motivations: str | None = Field(None, max_length=2000)
    strengths: str | None = Field(None, max_length=2000)
    weaknesses: str | None = Field(None, max_length=2000)
    notes: str | None = Field(None, max_length=2000)
    status: CharacterStatus = CharacterStatus.active

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be blank")
        return v.strip()

    @field_validator("role", "occupation", mode="before")
    @classmethod
    def strip_optional_strings(cls, v: str | None) -> str | None:
        if isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else None
        return v


class CharacterUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    role: str | None = Field(None, max_length=200)
    age: str | None = Field(None, max_length=50)
    gender: str | None = Field(None, max_length=100)
    occupation: str | None = Field(None, max_length=200)
    biography: str | None = Field(None, max_length=5000)
    personality: str | None = Field(None, max_length=2000)
    goals: str | None = Field(None, max_length=2000)
    motivations: str | None = Field(None, max_length=2000)
    strengths: str | None = Field(None, max_length=2000)
    weaknesses: str | None = Field(None, max_length=2000)
    notes: str | None = Field(None, max_length=2000)
    status: CharacterStatus | None = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("name must not be blank")
        return v.strip() if v else v


class CharacterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    universe_id: str
    name: str
    role: str | None
    age: str | None
    gender: str | None
    occupation: str | None
    biography: str | None
    personality: str | None
    goals: str | None
    motivations: str | None
    strengths: str | None
    weaknesses: str | None
    notes: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class CharacterListResponse(BaseModel):
    """Paginated list response."""

    items: list[CharacterResponse]
    total: int
    limit: int
    offset: int
