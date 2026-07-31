"""Pydantic v2 schemas for the Organization resource."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OrganizationCreate(BaseModel):
    universe_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=200)
    type: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=5000)
    leader: str | None = Field(None, max_length=200)
    purpose: str | None = Field(None, max_length=2000)
    notes: str | None = Field(None, max_length=2000)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be blank")
        return v.strip()


class OrganizationUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    type: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=5000)
    leader: str | None = Field(None, max_length=200)
    purpose: str | None = Field(None, max_length=2000)
    notes: str | None = Field(None, max_length=2000)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("name must not be blank")
        return v.strip() if v else v


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    universe_id: str
    name: str
    type: str | None
    description: str | None
    leader: str | None
    purpose: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class OrganizationListResponse(BaseModel):
    items: list[OrganizationResponse]
    total: int
    limit: int
    offset: int
