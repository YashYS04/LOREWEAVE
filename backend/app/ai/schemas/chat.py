"""Chat Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

# ── Message ────────────────────────────────────────────────────────────────────


class MessageRole:
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    role: str
    content: str
    prompt_type: str | None
    created_at: datetime


# ── Session ────────────────────────────────────────────────────────────────────


class ChatSessionCreate(BaseModel):
    universe_id: str = Field(..., min_length=1)
    title: str = Field("New Conversation", max_length=300)


class ChatSessionUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)


class ChatSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    universe_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    messages: list[ChatMessageResponse] = []


class ChatSessionListResponse(BaseModel):
    items: list[ChatSessionResponse]
    total: int


# ── Message send request ───────────────────────────────────────────────────────


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    prompt_type: str = Field(
        "general",
        description=(
            "Template key: general | universe_summary | lore_summary | "
            "character_analysis | conflict_suggestions | consistency_check | "
            "relationship_analysis | timeline_summary | story_expansion"
        ),
    )
