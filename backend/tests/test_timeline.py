"""Tests for the Timeline Intelligence Engine.

Covers:
    - TimelineRepository  (CRUD, filters, pagination, soft-delete)
    - TimelineService     (create, update with participant replacement)
    - API endpoints       (CRUD, filtering, 404s)
    - Participant CRUD    (inline create, replace, clear)
    - UniverseContextBuilder  (timeline included in context)
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.timeline import (
    EventStatus,
    EventType,
    TimelineEvent,
    TimelineParticipant,
)
from app.models.universe import Universe
from app.repositories.timeline import TimelineRepository
from app.schemas.timeline import (
    ParticipantCreate,
    TimelineEventCreate,
    TimelineEventUpdate,
)
from app.services.timeline import TimelineService

# ── Helpers ────────────────────────────────────────────────────────────────────


def _uid() -> str:
    return str(uuid.uuid4())


async def _make_universe(session: AsyncSession) -> Universe:
    u = Universe(
        id=_uid(),
        name="Test Universe",
        slug=f"test-{_uid()[:8]}",
        genre="fantasy",
        status="draft",
    )
    session.add(u)
    await session.flush()
    return u


# ── Repository tests ───────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_create_event_basic(test_session: AsyncSession):
    """Create a basic timeline event and verify it is persisted."""
    u = await _make_universe(test_session)
    repo = TimelineRepository(test_session)

    event = TimelineEvent(
        id=_uid(),
        universe_id=u.id,
        title="The Great Battle",
        event_type=EventType.BATTLE.value,
        status=EventStatus.COMPLETED.value,
    )
    created = await repo.create(event)

    assert created.id == event.id
    assert created.title == "The Great Battle"
    assert created.event_type == "battle"


@pytest.mark.anyio
async def test_get_by_id_returns_event(test_session: AsyncSession):
    u = await _make_universe(test_session)
    repo = TimelineRepository(test_session)

    event = TimelineEvent(id=_uid(), universe_id=u.id, title="Treaty Signing")
    await repo.create(event)

    fetched = await repo.get_by_id(event.id)
    assert fetched is not None
    assert fetched.title == "Treaty Signing"


@pytest.mark.anyio
async def test_get_by_id_not_found(test_session: AsyncSession):
    repo = TimelineRepository(test_session)
    result = await repo.get_by_id("nonexistent-id")
    assert result is None


@pytest.mark.anyio
async def test_list_by_universe_pagination(test_session: AsyncSession):
    u = await _make_universe(test_session)
    repo = TimelineRepository(test_session)

    for i in range(5):
        e = TimelineEvent(id=_uid(), universe_id=u.id, title=f"Event {i}")
        await repo.create(e)

    items, total = await repo.list_by_universe(u.id, skip=0, limit=3)
    assert total == 5
    assert len(items) == 3


@pytest.mark.anyio
async def test_list_by_universe_event_type_filter(test_session: AsyncSession):
    u = await _make_universe(test_session)
    repo = TimelineRepository(test_session)

    e1 = TimelineEvent(id=_uid(), universe_id=u.id, title="Battle", event_type="battle")
    e2 = TimelineEvent(id=_uid(), universe_id=u.id, title="Treaty", event_type="treaty")
    await repo.create(e1)
    await repo.create(e2)

    items, total = await repo.list_by_universe(u.id, event_type="battle")
    assert total == 1
    assert items[0].title == "Battle"


@pytest.mark.anyio
async def test_list_by_universe_search(test_session: AsyncSession):
    u = await _make_universe(test_session)
    repo = TimelineRepository(test_session)

    e1 = TimelineEvent(id=_uid(), universe_id=u.id, title="Dragon War")
    e2 = TimelineEvent(id=_uid(), universe_id=u.id, title="Peace Accord")
    await repo.create(e1)
    await repo.create(e2)

    items, total = await repo.list_by_universe(u.id, search="dragon")
    assert total == 1
    assert items[0].title == "Dragon War"


@pytest.mark.anyio
async def test_soft_delete_hides_event(test_session: AsyncSession):
    u = await _make_universe(test_session)
    repo = TimelineRepository(test_session)

    event = TimelineEvent(id=_uid(), universe_id=u.id, title="Old Event")
    await repo.create(event)

    await repo.soft_delete(event)
    result = await repo.get_by_id(event.id)
    assert result is None


@pytest.mark.anyio
async def test_count_by_universe(test_session: AsyncSession):
    u = await _make_universe(test_session)
    repo = TimelineRepository(test_session)

    for i in range(3):
        e = TimelineEvent(id=_uid(), universe_id=u.id, title=f"E{i}")
        await repo.create(e)

    count = await repo.count_by_universe(u.id)
    assert count == 3


@pytest.mark.anyio
async def test_replace_participants(test_session: AsyncSession):
    u = await _make_universe(test_session)
    repo = TimelineRepository(test_session)

    event = TimelineEvent(id=_uid(), universe_id=u.id, title="Battle of Kings")
    await repo.create(event)

    p1 = TimelineParticipant(
        id=_uid(),
        event_id=event.id,
        entity_type="character",
        entity_id=_uid(),
        role="General",
    )
    await repo.replace_participants(event.id, [p1])

    fetched = await repo.get_by_id(event.id)
    assert fetched is not None
    assert len(fetched.participants) == 1
    assert fetched.participants[0].role == "General"

    # Replace with a new participant
    p2 = TimelineParticipant(
        id=_uid(), event_id=event.id, entity_type="location", entity_id=_uid()
    )
    await repo.replace_participants(event.id, [p2])

    fetched2 = await repo.get_by_id(event.id)
    assert fetched2 is not None
    assert len(fetched2.participants) == 1
    assert fetched2.participants[0].entity_type == "location"


# ── Service tests ──────────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_service_create_with_participants(test_session: AsyncSession):
    u = await _make_universe(test_session)
    svc = TimelineService(test_session)

    payload = TimelineEventCreate(
        universe_id=u.id,
        title="Coronation of Queen Aelith",
        event_type=EventType.CORONATION,
        status=EventStatus.COMPLETED,
        start_date="Year 1042",
        importance=9,
        participants=[
            ParticipantCreate(entity_type="character", entity_id=_uid(), role="Queen"),
            ParticipantCreate(entity_type="location", entity_id=_uid(), role="Venue"),
        ],
    )
    event = await svc.create_event(payload)

    assert event.title == "Coronation of Queen Aelith"
    assert event.importance == 9
    assert len(event.participants) == 2
    roles = {p.role for p in event.participants}
    assert roles == {"Queen", "Venue"}


@pytest.mark.anyio
async def test_service_update_replaces_participants(test_session: AsyncSession):
    u = await _make_universe(test_session)
    svc = TimelineService(test_session)

    payload = TimelineEventCreate(
        universe_id=u.id,
        title="Rebellion of the North",
        participants=[
            ParticipantCreate(entity_type="organization", entity_id=_uid()),
        ],
    )
    event = await svc.create_event(payload)
    assert len(event.participants) == 1

    update = TimelineEventUpdate(
        title="Great Rebellion of the North",
        participants=[
            ParticipantCreate(
                entity_type="character", entity_id=_uid(), role="Rebel Leader"
            ),
            ParticipantCreate(
                entity_type="character", entity_id=_uid(), role="King's Champion"
            ),
        ],
    )
    updated = await svc.update_event(event.id, update)
    assert updated is not None
    assert updated.title == "Great Rebellion of the North"
    assert len(updated.participants) == 2


@pytest.mark.anyio
async def test_service_update_clears_participants(test_session: AsyncSession):
    u = await _make_universe(test_session)
    svc = TimelineService(test_session)

    cid = _uid()
    payload = TimelineEventCreate(
        universe_id=u.id,
        title="Treaty of Fire",
        participants=[ParticipantCreate(entity_type="character", entity_id=cid)],
    )
    event = await svc.create_event(payload)
    assert len(event.participants) == 1

    # Setting participants=[] clears all
    update = TimelineEventUpdate(participants=[])
    updated = await svc.update_event(event.id, update)
    assert updated is not None
    assert len(updated.participants) == 0


@pytest.mark.anyio
async def test_service_delete_returns_false_if_missing(test_session: AsyncSession):
    svc = TimelineService(test_session)
    result = await svc.delete_event("nonexistent")
    assert result is False


@pytest.mark.anyio
async def test_service_update_returns_none_if_missing(test_session: AsyncSession):
    svc = TimelineService(test_session)
    result = await svc.update_event("nonexistent", TimelineEventUpdate(title="X"))
    assert result is None


# ── API tests ──────────────────────────────────────────────────────────────────


async def _create_universe_via_api(client: AsyncClient) -> dict:
    resp = await client.post(
        "/api/v1/universes",
        json={"name": "Timeline Test Universe", "genre": "fantasy"},
    )
    assert resp.status_code == 201
    return resp.json()["data"]


@pytest.mark.anyio
async def test_api_create_event(client: AsyncClient):
    universe = await _create_universe_via_api(client)
    resp = await client.post(
        "/api/v1/timeline/events",
        json={
            "universe_id": universe["id"],
            "title": "Discovery of Magic",
            "event_type": "discovery",
            "status": "completed",
            "start_date": "Year 200",
            "importance": 7,
        },
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["title"] == "Discovery of Magic"
    assert data["event_type"] == "discovery"
    assert data["importance"] == 7


@pytest.mark.anyio
async def test_api_create_event_with_participants(client: AsyncClient):
    universe = await _create_universe_via_api(client)
    char_id = _uid()
    resp = await client.post(
        "/api/v1/timeline/events",
        json={
            "universe_id": universe["id"],
            "title": "Battle of Shadows",
            "event_type": "battle",
            "participants": [
                {"entity_type": "character", "entity_id": char_id, "role": "Commander"},
            ],
        },
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert len(data["participants"]) == 1
    assert data["participants"][0]["role"] == "Commander"
    assert data["participants"][0]["entity_id"] == char_id


@pytest.mark.anyio
async def test_api_list_events(client: AsyncClient):
    universe = await _create_universe_via_api(client)
    uid = universe["id"]

    for title in ["Event A", "Event B", "Event C"]:
        await client.post(
            "/api/v1/timeline/events",
            json={"universe_id": uid, "title": title},
        )

    resp = await client.get(f"/api/v1/timeline/events?universe_id={uid}")
    assert resp.status_code == 200
    body = resp.json()["data"]
    assert body["total"] == 3
    assert len(body["items"]) == 3


@pytest.mark.anyio
async def test_api_list_events_filter_by_type(client: AsyncClient):
    universe = await _create_universe_via_api(client)
    uid = universe["id"]

    await client.post(
        "/api/v1/timeline/events",
        json={"universe_id": uid, "title": "A War", "event_type": "battle"},
    )
    await client.post(
        "/api/v1/timeline/events",
        json={"universe_id": uid, "title": "A Birth", "event_type": "birth"},
    )

    resp = await client.get(
        f"/api/v1/timeline/events?universe_id={uid}&event_type=birth"
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["title"] == "A Birth"


@pytest.mark.anyio
async def test_api_list_events_search(client: AsyncClient):
    universe = await _create_universe_via_api(client)
    uid = universe["id"]

    await client.post(
        "/api/v1/timeline/events",
        json={"universe_id": uid, "title": "The Dragon Awakens"},
    )
    await client.post(
        "/api/v1/timeline/events",
        json={"universe_id": uid, "title": "Peace in the Valley"},
    )

    resp = await client.get(f"/api/v1/timeline/events?universe_id={uid}&search=dragon")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["title"] == "The Dragon Awakens"


@pytest.mark.anyio
async def test_api_get_event(client: AsyncClient):
    universe = await _create_universe_via_api(client)
    create_resp = await client.post(
        "/api/v1/timeline/events",
        json={"universe_id": universe["id"], "title": "The Final War"},
    )
    event_id = create_resp.json()["data"]["id"]

    resp = await client.get(f"/api/v1/timeline/events/{event_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["title"] == "The Final War"


@pytest.mark.anyio
async def test_api_get_event_not_found(client: AsyncClient):
    resp = await client.get(f"/api/v1/timeline/events/{_uid()}")
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_api_update_event(client: AsyncClient):
    universe = await _create_universe_via_api(client)
    create_resp = await client.post(
        "/api/v1/timeline/events",
        json={"universe_id": universe["id"], "title": "Old Title"},
    )
    event_id = create_resp.json()["data"]["id"]

    resp = await client.patch(
        f"/api/v1/timeline/events/{event_id}",
        json={"title": "New Title", "importance": 5},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["title"] == "New Title"
    assert data["importance"] == 5


@pytest.mark.anyio
async def test_api_delete_event(client: AsyncClient):
    universe = await _create_universe_via_api(client)
    create_resp = await client.post(
        "/api/v1/timeline/events",
        json={"universe_id": universe["id"], "title": "To Delete"},
    )
    event_id = create_resp.json()["data"]["id"]

    del_resp = await client.delete(f"/api/v1/timeline/events/{event_id}")
    assert del_resp.status_code == 200

    get_resp = await client.get(f"/api/v1/timeline/events/{event_id}")
    assert get_resp.status_code == 404


@pytest.mark.anyio
async def test_api_delete_event_not_found(client: AsyncClient):
    resp = await client.delete(f"/api/v1/timeline/events/{_uid()}")
    assert resp.status_code == 404


# ── Context builder tests ──────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_context_builder_includes_timeline(client: AsyncClient):
    """UniverseContextBuilder should include timeline events in AI context."""
    universe = await _create_universe_via_api(client)
    uid = universe["id"]

    await client.post(
        "/api/v1/timeline/events",
        json={
            "universe_id": uid,
            "title": "The Great Flood",
            "event_type": "disaster",
            "start_date": "Year 500",
            "importance": 10,
            "participants": [
                {"entity_type": "character", "entity_id": _uid(), "role": "Survivor"},
            ],
        },
    )

    resp = await client.post("/api/v1/ai/context", json={"universe_id": uid})
    assert resp.status_code == 200
    ctx = resp.json()["data"]
    assert "timeline" in ctx
    assert len(ctx["timeline"]) == 1
    event_ctx = ctx["timeline"][0]
    assert event_ctx["title"] == "The Great Flood"
    assert event_ctx["event_type"] == "disaster"
    assert event_ctx["start_date"] == "Year 500"
    assert event_ctx["importance"] == 10
    assert len(event_ctx["participants"]) == 1
    assert "Survivor" in event_ctx["participants"][0]


@pytest.mark.anyio
async def test_context_metadata_counts_timeline(client: AsyncClient):
    """context.metadata.counts should include timeline_events key."""
    universe = await _create_universe_via_api(client)
    uid = universe["id"]

    # Zero events
    resp = await client.post("/api/v1/ai/context", json={"universe_id": uid})
    assert resp.status_code == 200
    counts = resp.json()["data"]["metadata"]["counts"]
    assert "timeline_events" in counts
    assert counts["timeline_events"] == 0

    # One event
    await client.post(
        "/api/v1/timeline/events",
        json={"universe_id": uid, "title": "An Event"},
    )
    resp2 = await client.post("/api/v1/ai/context", json={"universe_id": uid})
    counts2 = resp2.json()["data"]["metadata"]["counts"]
    assert counts2["timeline_events"] == 1


@pytest.mark.anyio
async def test_list_for_context_ordering(test_session: AsyncSession):
    """Events returned for context should be ordered by start_date."""
    u = await _make_universe(test_session)
    repo = TimelineRepository(test_session)

    # Alphabetical order: "Year 100" < "Year 200" < "Year 300"
    for date, title in [
        ("Year 200", "Middle"),
        ("Year 100", "First"),
        ("Year 300", "Last"),
    ]:
        e = TimelineEvent(id=_uid(), universe_id=u.id, title=title, start_date=date)
        await repo.create(e)

    events = await repo.list_for_context(u.id)
    titles = [e.title for e in events]
    assert titles == ["First", "Middle", "Last"]
