"""AI Pydantic schemas — request/response models for the AI layer."""

from datetime import datetime

from pydantic import BaseModel, Field

# ── Context request / response ─────────────────────────────────────────────────


class ContextRequest(BaseModel):
    universe_id: str = Field(
        ..., min_length=1, description="UUID of the universe to contextualise."
    )


class UniverseSnippet(BaseModel):
    id: str
    name: str
    genre: str
    description: str | None
    tone: str | None
    status: str


class CharacterSnippet(BaseModel):
    id: str
    name: str
    role: str | None
    biography: str | None
    personality: str | None
    goals: str | None
    motivations: str | None
    strengths: str | None
    weaknesses: str | None


class LocationSnippet(BaseModel):
    id: str
    name: str
    type: str | None
    description: str | None
    climate: str | None
    culture: str | None


class OrganizationSnippet(BaseModel):
    id: str
    name: str
    type: str | None
    description: str | None
    leader: str | None
    purpose: str | None


class WorldObjectSnippet(BaseModel):
    id: str
    name: str
    category: str | None
    description: str | None
    origin: str | None
    abilities: str | None


class WorldRuleSnippet(BaseModel):
    id: str
    title: str
    category: str | None
    description: str | None
    limitations: str | None
    exceptions: str | None


class RelationshipSnippet(BaseModel):
    id: str
    source: str  # resolved display name or entity_id fallback
    source_type: str
    relationship: str  # relationship_type value
    target: str  # resolved display name or entity_id fallback
    target_type: str
    strength: int | None
    direction: str
    description: str | None


class TimelineEventSnippet(BaseModel):
    id: str
    title: str
    event_type: str
    status: str
    start_date: str | None
    end_date: str | None
    importance: int | None
    description: str | None
    # Participant summary: "EntityType:EntityId (role)" strings
    participants: list[str] = []


class ContextMetadata(BaseModel):
    generated_at: datetime
    counts: dict[str, int]
    version: str = "1.0"


class UniverseContext(BaseModel):
    """Complete AI-ready representation of a universe."""

    universe: UniverseSnippet
    characters: list[CharacterSnippet]
    locations: list[LocationSnippet]
    organizations: list[OrganizationSnippet]
    objects: list[WorldObjectSnippet]
    world_rules: list[WorldRuleSnippet]
    relationships: list[RelationshipSnippet] = []
    timeline: list[TimelineEventSnippet] = []
    metadata: ContextMetadata


# ── Provider health ────────────────────────────────────────────────────────────


class ProviderHealthResponse(BaseModel):
    provider_name: str
    model: str
    healthy: bool
    message: str
    version: str | None = None


# ── Generation (future use) ────────────────────────────────────────────────────


class GenerationRequest(BaseModel):
    universe_id: str
    prompt_key: str = Field(
        ...,
        description="Prompt template key, e.g. 'universe_summary' or 'character_analysis'.",
    )
    user_question: str | None = None
    temperature: float | None = Field(None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(None, ge=1, le=8192)


class GenerationResponse(BaseModel):
    text: str
    model: str
    provider: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
