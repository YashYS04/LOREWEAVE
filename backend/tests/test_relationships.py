"""Tests for the Universal Relationship Engine.

Covers:
  - RelationshipRepository  (CRUD, soft-delete, filters, pagination)
  - RelationshipService     (create, update, delete)
  - Relationship API        (all five endpoints, filter params)
  - UniverseContextBuilder  (relationships included in context)
"""

import pytest

from app.models.relationship import EntityType, RelationshipType

# ── Helpers ────────────────────────────────────────────────────────────────────


async def _create_universe(client, name: str = "Test Universe") -> str:
    resp = await client.post(
        "/api/v1/universes",
        json={"name": name, "genre": "fantasy"},
    )
    assert resp.status_code == 201
    return resp.json()["data"]["id"]


async def _create_relationship(
    client,
    uid: str,
    src_type: str = "character",
    src_id: str = "char-001",
    tgt_type: str = "organization",
    tgt_id: str = "org-001",
    rel_type: str = "member_of",
) -> dict:
    resp = await client.post(
        "/api/v1/relationships",
        json={
            "universe_id": uid,
            "source_entity_type": src_type,
            "source_entity_id": src_id,
            "target_entity_type": tgt_type,
            "target_entity_id": tgt_id,
            "relationship_type": rel_type,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["data"]


# ── Repository unit tests ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_repo_create_and_get(test_session) -> None:
    import uuid

    from app.models.relationship import Relationship
    from app.repositories.relationship import RelationshipRepository

    repo = RelationshipRepository(test_session)
    rel = Relationship(
        id=str(uuid.uuid4()),
        universe_id="u1",
        source_entity_type=EntityType.CHARACTER.value,
        source_entity_id="c1",
        target_entity_type=EntityType.ORGANIZATION.value,
        target_entity_id="o1",
        relationship_type=RelationshipType.MEMBER_OF.value,
        direction="unidirectional",
    )
    created = await repo.create(rel)
    assert created.id is not None

    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.relationship_type == "member_of"


@pytest.mark.asyncio
async def test_repo_soft_delete(test_session) -> None:
    import uuid

    from app.models.relationship import Relationship
    from app.repositories.relationship import RelationshipRepository

    repo = RelationshipRepository(test_session)
    rel = Relationship(
        id=str(uuid.uuid4()),
        universe_id="u1",
        source_entity_type=EntityType.CHARACTER.value,
        source_entity_id="c1",
        target_entity_type=EntityType.LOCATION.value,
        target_entity_id="l1",
        relationship_type=RelationshipType.LIVES_IN.value,
        direction="unidirectional",
    )
    created = await repo.create(rel)
    await repo.soft_delete(created)

    fetched = await repo.get_by_id(created.id)
    assert fetched is None


@pytest.mark.asyncio
async def test_repo_list_by_universe(test_session) -> None:
    import uuid

    from app.models.relationship import Relationship
    from app.repositories.relationship import RelationshipRepository

    repo = RelationshipRepository(test_session)

    for i in range(3):
        rel = Relationship(
            id=str(uuid.uuid4()),
            universe_id="u1",
            source_entity_type=EntityType.CHARACTER.value,
            source_entity_id=f"c{i}",
            target_entity_type=EntityType.ORGANIZATION.value,
            target_entity_id="o1",
            relationship_type=RelationshipType.MEMBER_OF.value,
            direction="unidirectional",
        )
        await repo.create(rel)

    # Different universe
    rel_other = Relationship(
        id=str(uuid.uuid4()),
        universe_id="u2",
        source_entity_type=EntityType.CHARACTER.value,
        source_entity_id="c99",
        target_entity_type=EntityType.ORGANIZATION.value,
        target_entity_id="o99",
        relationship_type=RelationshipType.ALLY_OF.value,
        direction="unidirectional",
    )
    await repo.create(rel_other)

    items, total = await repo.list_by_universe("u1")
    assert total == 3
    assert len(items) == 3


@pytest.mark.asyncio
async def test_repo_filter_by_entity_id(test_session) -> None:
    import uuid

    from app.models.relationship import Relationship
    from app.repositories.relationship import RelationshipRepository

    repo = RelationshipRepository(test_session)

    for i in range(2):
        rel = Relationship(
            id=str(uuid.uuid4()),
            universe_id="u1",
            source_entity_type=EntityType.CHARACTER.value,
            source_entity_id="c1",
            target_entity_type=EntityType.ORGANIZATION.value,
            target_entity_id=f"o{i}",
            relationship_type=RelationshipType.MEMBER_OF.value,
            direction="unidirectional",
        )
        await repo.create(rel)

    # Unrelated
    other = Relationship(
        id=str(uuid.uuid4()),
        universe_id="u1",
        source_entity_type=EntityType.CHARACTER.value,
        source_entity_id="c2",
        target_entity_type=EntityType.ORGANIZATION.value,
        target_entity_id="o9",
        relationship_type=RelationshipType.ALLY_OF.value,
        direction="unidirectional",
    )
    await repo.create(other)

    items, total = await repo.list_by_universe("u1", entity_id="c1")
    assert total == 2


@pytest.mark.asyncio
async def test_repo_filter_by_relationship_type(test_session) -> None:
    import uuid

    from app.models.relationship import Relationship
    from app.repositories.relationship import RelationshipRepository

    repo = RelationshipRepository(test_session)

    rel1 = Relationship(
        id=str(uuid.uuid4()),
        universe_id="u1",
        source_entity_type=EntityType.CHARACTER.value,
        source_entity_id="c1",
        target_entity_type=EntityType.CHARACTER.value,
        target_entity_id="c2",
        relationship_type=RelationshipType.ALLY_OF.value,
        direction="bidirectional",
    )
    rel2 = Relationship(
        id=str(uuid.uuid4()),
        universe_id="u1",
        source_entity_type=EntityType.CHARACTER.value,
        source_entity_id="c1",
        target_entity_type=EntityType.CHARACTER.value,
        target_entity_id="c3",
        relationship_type=RelationshipType.ENEMY_OF.value,
        direction="unidirectional",
    )
    await repo.create(rel1)
    await repo.create(rel2)

    items, total = await repo.list_by_universe("u1", relationship_type="ally_of")
    assert total == 1
    assert items[0].relationship_type == "ally_of"


@pytest.mark.asyncio
async def test_repo_search(test_session) -> None:
    import uuid

    from app.models.relationship import Relationship
    from app.repositories.relationship import RelationshipRepository

    repo = RelationshipRepository(test_session)

    rel = Relationship(
        id=str(uuid.uuid4()),
        universe_id="u1",
        source_entity_type=EntityType.CHARACTER.value,
        source_entity_id="c1",
        target_entity_type=EntityType.ORGANIZATION.value,
        target_entity_id="o1",
        relationship_type=RelationshipType.MEMBER_OF.value,
        title="Founding Member",
        description="Aria founded the Guild of Light long ago.",
        direction="unidirectional",
    )
    await repo.create(rel)

    items, total = await repo.list_by_universe("u1", search="Guild of Light")
    assert total == 1

    no_items, no_total = await repo.list_by_universe("u1", search="nonexistent_xyz")
    assert no_total == 0


@pytest.mark.asyncio
async def test_repo_pagination(test_session) -> None:
    import uuid

    from app.models.relationship import Relationship
    from app.repositories.relationship import RelationshipRepository

    repo = RelationshipRepository(test_session)
    for i in range(5):
        rel = Relationship(
            id=str(uuid.uuid4()),
            universe_id="u1",
            source_entity_type=EntityType.CHARACTER.value,
            source_entity_id=f"c{i}",
            target_entity_type=EntityType.ORGANIZATION.value,
            target_entity_id="o1",
            relationship_type=RelationshipType.MEMBER_OF.value,
            direction="unidirectional",
        )
        await repo.create(rel)

    page1, total = await repo.list_by_universe("u1", skip=0, limit=3)
    assert total == 5
    assert len(page1) == 3

    page2, _ = await repo.list_by_universe("u1", skip=3, limit=3)
    assert len(page2) == 2


# ── Service tests ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_service_create(test_session) -> None:
    from app.models.relationship import (
        EntityType,
        RelationshipDirection,
        RelationshipType,
    )
    from app.schemas.relationship import RelationshipCreate
    from app.services.relationship import RelationshipService

    svc = RelationshipService(test_session)
    payload = RelationshipCreate(
        universe_id="u1",
        source_entity_type=EntityType.CHARACTER,
        source_entity_id="char-abc",
        target_entity_type=EntityType.ORGANIZATION,
        target_entity_id="org-abc",
        relationship_type=RelationshipType.MEMBER_OF,
        strength=8,
        direction=RelationshipDirection.UNIDIRECTIONAL,
        metadata={"founded_year": 1200},
    )
    rel = await svc.create_relationship(payload)
    assert rel.id is not None
    assert rel.strength == 8
    assert rel.metadata_json is not None
    assert "1200" in rel.metadata_json


@pytest.mark.asyncio
async def test_service_update(test_session) -> None:
    from app.models.relationship import EntityType, RelationshipType
    from app.schemas.relationship import RelationshipCreate, RelationshipUpdate
    from app.services.relationship import RelationshipService

    svc = RelationshipService(test_session)
    create_payload = RelationshipCreate(
        universe_id="u1",
        source_entity_type=EntityType.CHARACTER,
        source_entity_id="c1",
        target_entity_type=EntityType.CHARACTER,
        target_entity_id="c2",
        relationship_type=RelationshipType.ALLY_OF,
    )
    rel = await svc.create_relationship(create_payload)

    updated = await svc.update_relationship(
        rel.id,
        RelationshipUpdate(relationship_type=RelationshipType.ENEMY_OF, strength=10),
    )
    assert updated is not None
    assert updated.relationship_type == "enemy_of"
    assert updated.strength == 10


@pytest.mark.asyncio
async def test_service_delete(test_session) -> None:
    from app.models.relationship import EntityType, RelationshipType
    from app.schemas.relationship import RelationshipCreate
    from app.services.relationship import RelationshipService

    svc = RelationshipService(test_session)
    payload = RelationshipCreate(
        universe_id="u1",
        source_entity_type=EntityType.CHARACTER,
        source_entity_id="c1",
        target_entity_type=EntityType.LOCATION,
        target_entity_id="l1",
        relationship_type=RelationshipType.LIVES_IN,
    )
    rel = await svc.create_relationship(payload)
    deleted = await svc.delete_relationship(rel.id)
    assert deleted is True
    assert await svc.get_by_id(rel.id) is None


# ── API integration tests ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_api_create_relationship(client) -> None:
    uid = await _create_universe(client)
    data = await _create_relationship(client, uid)
    assert data["id"] is not None
    assert data["relationship_type"] == "member_of"
    assert data["source_entity_type"] == "character"
    assert data["target_entity_type"] == "organization"


@pytest.mark.asyncio
async def test_api_create_self_relationship_fails(client) -> None:
    uid = await _create_universe(client)
    resp = await client.post(
        "/api/v1/relationships",
        json={
            "universe_id": uid,
            "source_entity_type": "character",
            "source_entity_id": "same-id",
            "target_entity_type": "character",
            "target_entity_id": "same-id",
            "relationship_type": "ally_of",
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_api_list_relationships(client) -> None:
    uid = await _create_universe(client)
    await _create_relationship(client, uid, src_id="c1", tgt_id="o1")
    await _create_relationship(client, uid, src_id="c2", tgt_id="o1")

    resp = await client.get(f"/api/v1/relationships?universe_id={uid}")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] == 2
    assert data["limit"] == 50
    assert data["offset"] == 0


@pytest.mark.asyncio
async def test_api_list_requires_universe_id(client) -> None:
    resp = await client.get("/api/v1/relationships")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_api_get_relationship_by_id(client) -> None:
    uid = await _create_universe(client)
    rel = await _create_relationship(client, uid)
    resp = await client.get(f"/api/v1/relationships/{rel['id']}")
    assert resp.status_code == 200
    assert resp.json()["data"]["id"] == rel["id"]


@pytest.mark.asyncio
async def test_api_get_relationship_not_found(client) -> None:
    resp = await client.get("/api/v1/relationships/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_api_patch_relationship(client) -> None:
    uid = await _create_universe(client)
    rel = await _create_relationship(client, uid)
    resp = await client.patch(
        f"/api/v1/relationships/{rel['id']}",
        json={"strength": 9, "description": "Updated description"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["strength"] == 9
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_api_patch_not_found(client) -> None:
    resp = await client.patch(
        "/api/v1/relationships/ghost",
        json={"strength": 5},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_api_delete_relationship(client) -> None:
    uid = await _create_universe(client)
    rel = await _create_relationship(client, uid)
    del_resp = await client.delete(f"/api/v1/relationships/{rel['id']}")
    assert del_resp.status_code == 200
    get_resp = await client.get(f"/api/v1/relationships/{rel['id']}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_api_delete_not_found(client) -> None:
    resp = await client.delete("/api/v1/relationships/ghost")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_api_filter_by_entity_id(client) -> None:
    uid = await _create_universe(client)
    await _create_relationship(client, uid, src_id="char-A", tgt_id="org-001")
    await _create_relationship(client, uid, src_id="char-A", tgt_id="org-002")
    await _create_relationship(client, uid, src_id="char-B", tgt_id="org-001")

    resp = await client.get(f"/api/v1/relationships?universe_id={uid}&entity_id=char-A")
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 2


@pytest.mark.asyncio
async def test_api_filter_by_relationship_type(client) -> None:
    uid = await _create_universe(client)
    await _create_relationship(
        client, uid, src_id="c1", tgt_id="c2", rel_type="ally_of"
    )
    await _create_relationship(
        client, uid, src_id="c1", tgt_id="c3", rel_type="enemy_of"
    )

    resp = await client.get(
        f"/api/v1/relationships?universe_id={uid}&relationship_type=ally_of"
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 1


@pytest.mark.asyncio
async def test_api_search(client) -> None:
    uid = await _create_universe(client)
    resp = await client.post(
        "/api/v1/relationships",
        json={
            "universe_id": uid,
            "source_entity_type": "character",
            "source_entity_id": "c1",
            "target_entity_type": "organization",
            "target_entity_id": "o1",
            "relationship_type": "member_of",
            "title": "Founding Member",
            "description": "Aria is the founder of the Guild of Light.",
        },
    )
    assert resp.status_code == 201

    search_resp = await client.get(
        f"/api/v1/relationships?universe_id={uid}&search=Guild+of+Light"
    )
    assert search_resp.status_code == 200
    assert search_resp.json()["data"]["total"] == 1


@pytest.mark.asyncio
async def test_api_pagination(client) -> None:
    uid = await _create_universe(client)
    for i in range(5):
        await _create_relationship(client, uid, src_id=f"c{i}", tgt_id="o1")

    page1 = await client.get(f"/api/v1/relationships?universe_id={uid}&skip=0&limit=3")
    assert page1.json()["data"]["total"] == 5
    assert len(page1.json()["data"]["items"]) == 3

    page2 = await client.get(f"/api/v1/relationships?universe_id={uid}&skip=3&limit=3")
    assert len(page2.json()["data"]["items"]) == 2


@pytest.mark.asyncio
async def test_api_metadata_roundtrip(client) -> None:
    uid = await _create_universe(client)
    resp = await client.post(
        "/api/v1/relationships",
        json={
            "universe_id": uid,
            "source_entity_type": "character",
            "source_entity_id": "c1",
            "target_entity_type": "organization",
            "target_entity_id": "o1",
            "relationship_type": "member_of",
            "metadata": {"since_year": 1200, "rank": "captain"},
        },
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["metadata"]["since_year"] == 1200
    assert data["metadata"]["rank"] == "captain"


@pytest.mark.asyncio
async def test_api_relationships_isolated_by_universe(client) -> None:
    uid1 = await _create_universe(client, "Universe Alpha")
    uid2 = await _create_universe(client, "Universe Beta")

    await _create_relationship(client, uid1)

    resp = await client.get(f"/api/v1/relationships?universe_id={uid2}")
    assert resp.json()["data"]["total"] == 0


# ── Context builder integration tests ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_context_includes_relationships(client) -> None:
    """Verify POST /ai/context returns relationships in the context payload."""
    uid = await _create_universe(client)
    await _create_relationship(client, uid)

    resp = await client.post(
        "/api/v1/ai/context",
        json={"universe_id": uid},
    )
    assert resp.status_code == 200
    ctx = resp.json()["data"]
    assert "relationships" in ctx
    assert isinstance(ctx["relationships"], list)
    assert len(ctx["relationships"]) == 1
    assert ctx["metadata"]["counts"]["relationships"] == 1


@pytest.mark.asyncio
async def test_context_relationship_snippet_fields(client) -> None:
    uid = await _create_universe(client)
    await client.post(
        "/api/v1/relationships",
        json={
            "universe_id": uid,
            "source_entity_type": "character",
            "source_entity_id": "char-x",
            "target_entity_type": "organization",
            "target_entity_id": "org-x",
            "relationship_type": "member_of",
            "strength": 7,
            "direction": "unidirectional",
            "description": "Core member since founding.",
        },
    )
    resp = await client.post("/api/v1/ai/context", json={"universe_id": uid})
    assert resp.status_code == 200
    snippet = resp.json()["data"]["relationships"][0]
    assert snippet["relationship"] == "member_of"
    assert snippet["strength"] == 7
    assert snippet["direction"] == "unidirectional"
    assert snippet["description"] == "Core member since founding."
    assert snippet["source_type"] == "character"
    assert snippet["target_type"] == "organization"


@pytest.mark.asyncio
async def test_context_empty_relationships(client) -> None:
    uid = await _create_universe(client)
    resp = await client.post("/api/v1/ai/context", json={"universe_id": uid})
    assert resp.status_code == 200
    assert resp.json()["data"]["relationships"] == []
    assert resp.json()["data"]["metadata"]["counts"]["relationships"] == 0
