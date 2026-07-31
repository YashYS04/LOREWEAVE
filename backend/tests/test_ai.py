"""Tests for the AI Foundation layer.

All Ollama network calls are mocked — tests must pass without a running Ollama
instance.  The test scope covers:

  - UniverseContextBuilder (unit)
  - Serializer (unit)
  - Prompt templates (unit)
  - AIService (unit, mocked provider)
  - OllamaGraniteProvider (unit, mocked httpx)
  - POST /api/v1/ai/context  (integration)
  - GET  /api/v1/ai/health   (integration)
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ai.context.builder import UniverseContextBuilder
from app.ai.context.serializer import (
    build_context,
    serialize_character,
    serialize_location,
    serialize_organization,
    serialize_universe,
    serialize_world_object,
    serialize_world_rule,
)
from app.ai.prompts.templates import (
    PROMPT_REGISTRY,
    character_analysis,
    consistency_check,
    get_prompt,
    lore_summary,
    universe_summary,
)
from app.ai.providers.base import GenerationResult, ProviderHealth
from app.ai.providers.granite import OllamaGraniteProvider
from app.ai.schemas.ai import (
    GenerationRequest,
    UniverseContext,
)
from app.ai.services.ai_service import AIService
from app.models.character import Character
from app.models.location import Location
from app.models.organization import Organization
from app.models.universe import Universe
from app.models.world_object import WorldObject
from app.models.world_rule import WorldRule

# ── Shared helpers ─────────────────────────────────────────────────────────────


def _make_universe() -> Universe:
    u = Universe()
    u.id = "uni-001"
    u.name = "The Shattered Realm"
    u.slug = "the-shattered-realm"
    u.genre = "fantasy"
    u.description = "A world torn apart by ancient magic."
    u.tone = "Dark and epic"
    u.status = "active"
    u.created_at = datetime.now(tz=UTC)
    u.updated_at = datetime.now(tz=UTC)
    u.deleted_at = None
    return u


def _make_character() -> Character:
    c = Character()
    c.id = "char-001"
    c.universe_id = "uni-001"
    c.name = "Kael Dorn"
    c.role = "Protagonist"
    c.biography = "A seasoned explorer."
    c.personality = "Curious and determined."
    c.goals = "Uncover the truth."
    c.motivations = "A lost family member."
    c.strengths = "Resourceful."
    c.weaknesses = "Overconfident."
    c.status = "active"
    c.created_at = datetime.now(tz=UTC)
    c.updated_at = datetime.now(tz=UTC)
    c.deleted_at = None
    return c


def _make_location() -> Location:
    loc = Location()
    loc.id = "loc-001"
    loc.universe_id = "uni-001"
    loc.name = "Ember Falls"
    loc.type = "City"
    loc.description = "A city built on volcanic rock."
    loc.climate = "Arid"
    loc.culture = "Militaristic"
    loc.population = "~30,000"
    loc.created_at = datetime.now(tz=UTC)
    loc.updated_at = datetime.now(tz=UTC)
    loc.deleted_at = None
    return loc


def _make_organization() -> Organization:
    o = Organization()
    o.id = "org-001"
    o.universe_id = "uni-001"
    o.name = "Order of the Flame"
    o.type = "Military"
    o.description = "Guardians of the realm."
    o.leader = "High Commander Asha"
    o.purpose = "Protect the Last Gate."
    o.created_at = datetime.now(tz=UTC)
    o.updated_at = datetime.now(tz=UTC)
    o.deleted_at = None
    return o


def _make_world_object() -> WorldObject:
    obj = WorldObject()
    obj.id = "obj-001"
    obj.universe_id = "uni-001"
    obj.name = "Voidbane Blade"
    obj.category = "Weapon"
    obj.description = "A sword forged from a collapsed star."
    obj.origin = "Ancient forge."
    obj.owner = "Kael Dorn"
    obj.abilities = "Cuts through magical barriers."
    obj.created_at = datetime.now(tz=UTC)
    obj.updated_at = datetime.now(tz=UTC)
    obj.deleted_at = None
    return obj


def _make_world_rule() -> WorldRule:
    r = WorldRule()
    r.id = "rule-001"
    r.universe_id = "uni-001"
    r.title = "Law of Conservation of Magic"
    r.category = "Magic System"
    r.description = "Magic cannot be created or destroyed."
    r.limitations = "Applies above the Veil."
    r.exceptions = "Void entities are exempt."
    r.created_at = datetime.now(tz=UTC)
    r.updated_at = datetime.now(tz=UTC)
    r.deleted_at = None
    return r


def _make_context() -> UniverseContext:
    return build_context(
        universe=_make_universe(),
        characters=[_make_character()],
        locations=[_make_location()],
        organizations=[_make_organization()],
        objects=[_make_world_object()],
        world_rules=[_make_world_rule()],
    )


# ══════════════════════════════════════════════════════════════════════════════
# SERIALIZER UNIT TESTS
# ══════════════════════════════════════════════════════════════════════════════


def test_serialize_universe_fields():
    snippet = serialize_universe(_make_universe())
    assert snippet.id == "uni-001"
    assert snippet.name == "The Shattered Realm"
    assert snippet.genre == "fantasy"
    assert snippet.tone == "Dark and epic"


def test_serialize_character_fields():
    snippet = serialize_character(_make_character())
    assert snippet.id == "char-001"
    assert snippet.name == "Kael Dorn"
    assert snippet.role == "Protagonist"
    assert snippet.biography == "A seasoned explorer."


def test_serialize_location_fields():
    snippet = serialize_location(_make_location())
    assert snippet.id == "loc-001"
    assert snippet.name == "Ember Falls"
    assert snippet.type == "City"
    assert snippet.climate == "Arid"


def test_serialize_organization_fields():
    snippet = serialize_organization(_make_organization())
    assert snippet.id == "org-001"
    assert snippet.name == "Order of the Flame"
    assert snippet.leader == "High Commander Asha"


def test_serialize_world_object_fields():
    snippet = serialize_world_object(_make_world_object())
    assert snippet.id == "obj-001"
    assert snippet.name == "Voidbane Blade"
    assert snippet.abilities == "Cuts through magical barriers."


def test_serialize_world_rule_fields():
    snippet = serialize_world_rule(_make_world_rule())
    assert snippet.id == "rule-001"
    assert snippet.title == "Law of Conservation of Magic"
    assert snippet.limitations == "Applies above the Veil."


def test_build_context_metadata_counts():
    ctx = _make_context()
    assert ctx.metadata.counts["characters"] == 1
    assert ctx.metadata.counts["locations"] == 1
    assert ctx.metadata.counts["organizations"] == 1
    assert ctx.metadata.counts["objects"] == 1
    assert ctx.metadata.counts["world_rules"] == 1


def test_build_context_empty_entities():
    ctx = build_context(
        universe=_make_universe(),
        characters=[],
        locations=[],
        organizations=[],
        objects=[],
        world_rules=[],
    )
    assert ctx.metadata.counts == {
        "characters": 0,
        "locations": 0,
        "organizations": 0,
        "objects": 0,
        "world_rules": 0,
        "relationships": 0,
        "timeline_events": 0,
    }
    assert ctx.characters == []
    assert ctx.relationships == []
    assert ctx.timeline == []


# ══════════════════════════════════════════════════════════════════════════════
# PROMPT TEMPLATE UNIT TESTS
# ══════════════════════════════════════════════════════════════════════════════


def test_universe_summary_contains_universe_name():
    ctx = _make_context()
    prompt = universe_summary(ctx)
    assert "The Shattered Realm" in prompt


def test_universe_summary_with_user_question():
    ctx = _make_context()
    prompt = universe_summary(ctx, user_question="What is the tone?")
    assert "What is the tone?" in prompt


def test_lore_summary_prompt():
    ctx = _make_context()
    prompt = lore_summary(ctx)
    assert "lore" in prompt.lower()


def test_character_analysis_prompt_contains_json():
    ctx = _make_context()
    prompt = character_analysis(ctx)
    assert "Kael Dorn" in prompt


def test_consistency_check_prompt():
    ctx = _make_context()
    prompt = consistency_check(ctx)
    assert "inconsistencies" in prompt.lower() or "consistency" in prompt.lower()


def test_all_templates_render_without_error():
    ctx = _make_context()
    for key in PROMPT_REGISTRY:
        result = get_prompt(key, ctx, "test question")
        assert isinstance(result, str)
        assert len(result) > 50


def test_get_prompt_unknown_key_raises():
    ctx = _make_context()
    with pytest.raises(ValueError, match="Unknown prompt key"):
        get_prompt("nonexistent_key", ctx)


def test_prompt_registry_contains_all_required_templates():
    required = {
        "universe_summary",
        "lore_summary",
        "character_analysis",
        "conflict_suggestions",
        "consistency_check",
        "relationship_analysis",
        "timeline_summary",
        "story_expansion",
    }
    assert required.issubset(set(PROMPT_REGISTRY.keys()))


# ══════════════════════════════════════════════════════════════════════════════
# CONTEXT BUILDER UNIT TESTS (mocked session)
# ══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_context_builder_returns_none_for_unknown_universe():
    mock_session = MagicMock()
    builder = UniverseContextBuilder(mock_session)

    with patch.object(
        builder._universes, "get_by_id", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = None
        result = await builder.build("does-not-exist")
        assert result is None


@pytest.mark.asyncio
async def test_context_builder_builds_full_context():
    mock_session = MagicMock()
    builder = UniverseContextBuilder(mock_session)

    universe = _make_universe()
    character = _make_character()
    location = _make_location()

    with (
        patch.object(
            builder._universes,
            "get_by_id",
            new_callable=AsyncMock,
            return_value=universe,
        ),
        patch.object(
            builder._characters,
            "list_by_universe",
            new_callable=AsyncMock,
            return_value=[character],
        ),
        patch.object(
            builder._locations,
            "list_by_universe",
            new_callable=AsyncMock,
            return_value=[location],
        ),
        patch.object(
            builder._organizations,
            "list_by_universe",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch.object(
            builder._objects,
            "list_by_universe",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch.object(
            builder._rules, "list_by_universe", new_callable=AsyncMock, return_value=[]
        ),
        patch.object(
            builder._relationships,
            "list_for_context",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch.object(
            builder._timeline,
            "list_for_context",
            new_callable=AsyncMock,
            return_value=[],
        ),
    ):
        ctx = await builder.build("uni-001")

    assert ctx is not None
    assert ctx.universe.name == "The Shattered Realm"
    assert len(ctx.characters) == 1
    assert ctx.characters[0].name == "Kael Dorn"
    assert len(ctx.locations) == 1
    assert ctx.metadata.counts["characters"] == 1


# ══════════════════════════════════════════════════════════════════════════════
# AI SERVICE UNIT TESTS (mocked provider + builder)
# ══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_ai_service_get_context_delegates_to_builder():
    mock_session = MagicMock()
    mock_provider = MagicMock()
    svc = AIService(session=mock_session, provider=mock_provider)
    expected_ctx = _make_context()

    with patch.object(
        svc._builder, "build", new_callable=AsyncMock, return_value=expected_ctx
    ):
        result = await svc.get_context("uni-001")
    assert result is expected_ctx


@pytest.mark.asyncio
async def test_ai_service_returns_none_for_unknown_universe():
    mock_session = MagicMock()
    mock_provider = MagicMock()
    svc = AIService(session=mock_session, provider=mock_provider)

    with patch.object(svc._builder, "build", new_callable=AsyncMock, return_value=None):
        result = await svc.get_context("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_ai_service_provider_health():
    mock_session = MagicMock()
    mock_provider = AsyncMock()
    expected_health = ProviderHealth(
        healthy=True,
        provider_name="Ollama (IBM Granite 3.3 2B)",
        model="granite3.3:2b",
        message="OK",
    )
    mock_provider.health.return_value = expected_health
    svc = AIService(session=mock_session, provider=mock_provider)

    health = await svc.provider_health()
    assert health.healthy is True
    assert health.provider_name == "Ollama (IBM Granite 3.3 2B)"


@pytest.mark.asyncio
async def test_ai_service_generate_calls_provider():
    mock_session = MagicMock()
    mock_provider = AsyncMock()
    mock_provider.provider_name = "Ollama (IBM Granite 3.3 2B)"
    mock_provider.generate.return_value = GenerationResult(
        text="Generated text.",
        model="granite3.3:2b",
        provider="Ollama (IBM Granite 3.3 2B)",
        prompt_tokens=50,
        completion_tokens=30,
    )
    svc = AIService(session=mock_session, provider=mock_provider)
    ctx = _make_context()

    with patch.object(svc._builder, "build", new_callable=AsyncMock, return_value=ctx):
        req = GenerationRequest(universe_id="uni-001", prompt_key="universe_summary")
        response = await svc.generate(req)

    assert response is not None
    assert response.text == "Generated text."
    assert response.model == "granite3.3:2b"
    mock_provider.generate.assert_called_once()


@pytest.mark.asyncio
async def test_ai_service_generate_returns_none_for_missing_universe():
    mock_session = MagicMock()
    mock_provider = AsyncMock()
    svc = AIService(session=mock_session, provider=mock_provider)

    with patch.object(svc._builder, "build", new_callable=AsyncMock, return_value=None):
        req = GenerationRequest(universe_id="ghost", prompt_key="universe_summary")
        result = await svc.generate(req)
    assert result is None
    mock_provider.generate.assert_not_called()


# ══════════════════════════════════════════════════════════════════════════════
# OLLAMA PROVIDER UNIT TESTS (mocked httpx)
# ══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_granite_provider_name():
    provider = OllamaGraniteProvider()
    assert provider.provider_name == "Ollama (IBM Granite 3.3 2B)"


@pytest.mark.asyncio
async def test_granite_generate_success():
    provider = OllamaGraniteProvider()

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "response": "A great story begins here.",
        "model": "granite3.3:2b",
        "prompt_eval_count": 40,
        "eval_count": 20,
    }
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.ai.providers.granite.httpx.AsyncClient", return_value=mock_client):
        result = await provider.generate("Tell me about this world.")

    assert result.text == "A great story begins here."
    assert result.model == "granite3.3:2b"
    assert result.prompt_tokens == 40


@pytest.mark.asyncio
async def test_granite_health_model_available():
    provider = OllamaGraniteProvider()

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "models": [{"name": "granite3.3:2b"}],
    }
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.ai.providers.granite.httpx.AsyncClient", return_value=mock_client):
        health = await provider.health()

    assert health.healthy is True
    assert health.provider_name == "Ollama (IBM Granite 3.3 2B)"


@pytest.mark.asyncio
async def test_granite_health_model_not_available():
    provider = OllamaGraniteProvider()

    mock_response = MagicMock()
    mock_response.json.return_value = {"models": [{"name": "llama3:8b"}]}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.ai.providers.granite.httpx.AsyncClient", return_value=mock_client):
        health = await provider.health()

    assert health.healthy is False
    assert "not found" in health.message.lower()


@pytest.mark.asyncio
async def test_granite_health_connect_error():
    import httpx

    provider = OllamaGraniteProvider()

    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.ConnectError("Connection refused")
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.ai.providers.granite.httpx.AsyncClient", return_value=mock_client):
        health = await provider.health()

    assert health.healthy is False
    assert "Cannot connect" in health.message


# ══════════════════════════════════════════════════════════════════════════════
# API INTEGRATION TESTS  (uses test DB via client fixture)
# ══════════════════════════════════════════════════════════════════════════════


async def _create_universe_via_api(client) -> str:
    resp = await client.post(
        "/api/v1/universes",
        json={"name": "AI Test Universe", "genre": "fantasy"},
    )
    assert resp.status_code == 201
    return resp.json()["data"]["id"]


@pytest.mark.asyncio
async def test_ai_health_endpoint_unhealthy_when_no_ollama(client):
    """When Ollama is not running the health endpoint returns 503."""
    import httpx

    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.ConnectError("refused")
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.ai.providers.granite.httpx.AsyncClient", return_value=mock_client):
        resp = await client.get("/api/v1/ai/health")

    assert resp.status_code == 503
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "AI_PROVIDER_UNAVAILABLE"


@pytest.mark.asyncio
async def test_ai_health_endpoint_healthy(client):
    """Health endpoint returns 200 when Ollama responds correctly."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"models": [{"name": "granite3.3:2b"}]}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.ai.providers.granite.httpx.AsyncClient", return_value=mock_client):
        resp = await client.get("/api/v1/ai/health")

    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["healthy"] is True
    assert data["model"] == "granite3.3:2b"


@pytest.mark.asyncio
async def test_ai_context_endpoint_universe_not_found(client):
    resp = await client.post(
        "/api/v1/ai/context",
        json={"universe_id": "does-not-exist"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_ai_context_endpoint_success(client):
    """Context endpoint returns a fully assembled UniverseContext."""
    uid = await _create_universe_via_api(client)

    # Add a character and a location for richer context
    await client.post(
        "/api/v1/characters",
        json={"universe_id": uid, "name": "Context Hero", "role": "Protagonist"},
    )
    await client.post(
        "/api/v1/locations",
        json={"universe_id": uid, "name": "The Hollow Peaks", "type": "Mountain Range"},
    )

    resp = await client.post("/api/v1/ai/context", json={"universe_id": uid})
    assert resp.status_code == 200

    body = resp.json()
    assert body["success"] is True
    data = body["data"]

    # Validate top-level structure
    assert data["universe"]["id"] == uid
    assert data["universe"]["name"] == "AI Test Universe"
    assert len(data["characters"]) == 1
    assert data["characters"][0]["name"] == "Context Hero"
    assert len(data["locations"]) == 1
    assert data["locations"][0]["name"] == "The Hollow Peaks"
    assert data["metadata"]["counts"]["characters"] == 1
    assert data["metadata"]["counts"]["locations"] == 1
    assert data["metadata"]["counts"]["organizations"] == 0


@pytest.mark.asyncio
async def test_ai_context_metadata_version_present(client):
    uid = await _create_universe_via_api(client)
    resp = await client.post("/api/v1/ai/context", json={"universe_id": uid})
    data = resp.json()["data"]
    assert "version" in data["metadata"]
    assert "generated_at" in data["metadata"]
