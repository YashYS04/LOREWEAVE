"""Tests for Universe CRUD endpoints — updated for standard response envelope."""

import pytest

# ── Root ───────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_root_endpoint(client) -> None:
    resp = await client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["application"] == "LOREWEAVE API"
    assert body["status"] == "running"


# ── Health ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_health_endpoint(client) -> None:
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["status"] == "healthy"


# ── Create ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_universe(client) -> None:
    resp = await client.post(
        "/api/v1/universes",
        json={
            "name": "The Shattered Realm",
            "genre": "fantasy",
            "description": "A world broken by ancient magic.",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["name"] == "The Shattered Realm"
    assert data["slug"] == "the-shattered-realm"
    assert data["genre"] == "fantasy"
    assert data["status"] == "draft"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_universe_slug_auto_generated(client) -> None:
    resp = await client.post(
        "/api/v1/universes",
        json={"name": "  Neon City 2099  ", "genre": "cyberpunk"},
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["slug"] == "neon-city-2099"


@pytest.mark.asyncio
async def test_create_universe_name_too_long(client) -> None:
    resp = await client.post(
        "/api/v1/universes",
        json={"name": "A" * 121, "genre": "fantasy"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_universe_invalid_genre(client) -> None:
    resp = await client.post(
        "/api/v1/universes",
        json={"name": "Test", "genre": "not_a_real_genre"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_universe_blank_name(client) -> None:
    resp = await client.post(
        "/api/v1/universes",
        json={"name": "   ", "genre": "fantasy"},
    )
    assert resp.status_code == 422


# ── List ───────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_universes_empty(client) -> None:
    resp = await client.get("/api/v1/universes")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_universes_after_create(client) -> None:
    await client.post(
        "/api/v1/universes",
        json={"name": "List Test Universe", "genre": "mystery"},
    )
    resp = await client.get("/api/v1/universes")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] == 1
    assert len(data["items"]) == 1


# ── Get ────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_universe_by_id(client) -> None:
    create_resp = await client.post(
        "/api/v1/universes",
        json={"name": "Fetch Me", "genre": "thriller"},
    )
    universe_id = create_resp.json()["data"]["id"]
    resp = await client.get(f"/api/v1/universes/{universe_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["id"] == universe_id


@pytest.mark.asyncio
async def test_get_universe_not_found(client) -> None:
    resp = await client.get("/api/v1/universes/nonexistent-id-12345")
    assert resp.status_code == 404


# ── Patch ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_patch_universe(client) -> None:
    create_resp = await client.post(
        "/api/v1/universes",
        json={"name": "Patchable Universe", "genre": "romance"},
    )
    universe_id = create_resp.json()["data"]["id"]
    resp = await client.patch(
        f"/api/v1/universes/{universe_id}",
        json={"status": "active", "tone": "hopeful"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["status"] == "active"
    assert data["tone"] == "hopeful"


@pytest.mark.asyncio
async def test_patch_universe_not_found(client) -> None:
    resp = await client.patch(
        "/api/v1/universes/ghost-id-99999",
        json={"tone": "dark"},
    )
    assert resp.status_code == 404


# ── Delete (now soft delete) ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_universe(client) -> None:
    create_resp = await client.post(
        "/api/v1/universes",
        json={"name": "Delete Me", "genre": "horror"},
    )
    universe_id = create_resp.json()["data"]["id"]
    del_resp = await client.delete(f"/api/v1/universes/{universe_id}")
    assert del_resp.status_code == 200
    get_resp = await client.get(f"/api/v1/universes/{universe_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_universe_not_found(client) -> None:
    resp = await client.delete("/api/v1/universes/ghost-id-99999")
    assert resp.status_code == 404


# ── Slug uniqueness ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_slug_uniqueness(client) -> None:
    """Two universes with the same name should get different slugs."""
    resp1 = await client.post(
        "/api/v1/universes",
        json={"name": "Twin Universe", "genre": "fantasy"},
    )
    resp2 = await client.post(
        "/api/v1/universes",
        json={"name": "Twin Universe", "genre": "mystery"},
    )
    assert resp1.status_code == 201
    assert resp2.status_code == 201
    assert resp1.json()["data"]["slug"] != resp2.json()["data"]["slug"]
