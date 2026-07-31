"""Pydantic v2 schemas for the WorldRule resource."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WorldRuleCreate(BaseModel):
    universe_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=200)
    category: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=5000)
    limitations: str | None = Field(None, max_length=2000)
    exceptions: str | None = Field(None, max_length=2000)
    notes: str | None = Field(None, max_length=2000)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be blank")
        return v.strip()


class WorldRuleUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    category: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=5000)
    limitations: str | None = Field(None, max_length=2000)
    exceptions: str | None = Field(None, max_length=2000)
    notes: str | None = Field(None, max_length=2000)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("title must not be blank")
        return v.strip() if v else v


class WorldRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    universe_id: str
    title: str
    category: str | None
    description: str | None
    limitations: str | None
    exceptions: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class WorldRuleListResponse(BaseModel):
    items: list[WorldRuleResponse]
    total: int
    limit: int
    offset: int
