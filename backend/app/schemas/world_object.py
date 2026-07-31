"""Pydantic v2 schemas for the WorldObject resource."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WorldObjectCreate(BaseModel):
    universe_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=200)
    category: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=5000)
    origin: str | None = Field(None, max_length=2000)
    owner: str | None = Field(None, max_length=200)
    abilities: str | None = Field(None, max_length=2000)
    notes: str | None = Field(None, max_length=2000)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be blank")
        return v.strip()


class WorldObjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    category: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=5000)
    origin: str | None = Field(None, max_length=2000)
    owner: str | None = Field(None, max_length=200)
    abilities: str | None = Field(None, max_length=2000)
    notes: str | None = Field(None, max_length=2000)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("name must not be blank")
        return v.strip() if v else v


class WorldObjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    universe_id: str
    name: str
    category: str | None
    description: str | None
    origin: str | None
    owner: str | None
    abilities: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class WorldObjectListResponse(BaseModel):
    items: list[WorldObjectResponse]
    total: int
    limit: int
    offset: int
