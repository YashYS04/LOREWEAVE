"""Tests for Character CRUD endpoints."""

import pytest

# ── Helpers ────────────────────────────────────────────────────────────────────


async def _create_universe(client, name: str = "Test Universe") -> str:
    """Create a universe and return its ID."""
    resp = await client.post(
        "/api/v1/universes",
        json={"name": name, "genre": "fantasy"},
    )
    assert resp.status_code == 201
    return resp.json()["data"]["id"]


# ── Create ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_character_minimal(client) -> None:
    universe_id = await _create_universe(client)
    resp = await client.post(
        "/api/v1/characters",
        json={"universe_id": universe_id, "name": "Asha Veil"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["name"] == "Asha Veil"
    assert data["universe_id"] == universe_id
    assert data["status"] == "active"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_character_full(client) -> None:
    universe_id = await _create_universe(client, "Full Universe")
    resp = await client.post(
        "/api/v1/characters",
        json={
            "universe_id": universe_id,
            "name": "Kael Dorn",
            "role": "Protagonist",
            "age": "32",
            "gender": "male",
            "occupation": "Archaeologist",
            "biography": "A seasoned explorer of ancient ruins.",
            "personality": "Curious, determined, sometimes reckless.",
            "goals": "Uncover the truth behind the Shattered Realm.",
            "motivations": "A lost family member vanished during an expedition.",
            "strengths": "Resourceful, excellent under pressure.",
            "weaknesses": "Overconfident, struggles to trust others.",
            "notes": "Has a scar above his left eye.",
            "status": "active",
        },
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["name"] == "Kael Dorn"
    assert data["role"] == "Protagonist"
    assert data["biography"] == "A seasoned explorer of ancient ruins."


@pytest.mark.asyncio
async def test_create_character_blank_name(client) -> None:
    universe_id = await _create_universe(client)
    resp = await client.post(
        "/api/v1/characters",
        json={"universe_id": universe_id, "name": "   "},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_character_name_too_long(client) -> None:
    universe_id = await _create_universe(client)
    resp = await client.post(
        "/api/v1/characters",
        json={"universe_id": universe_id, "name": "A" * 201},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_character_biography_too_long(client) -> None:
    universe_id = await _create_universe(client)
    resp = await client.post(
        "/api/v1/characters",
        json={"universe_id": universe_id, "name": "Bio Test", "biography": "B" * 5001},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_character_invalid_status(client) -> None:
    universe_id = await _create_universe(client)
    resp = await client.post(
        "/api/v1/characters",
        json={"universe_id": universe_id, "name": "Status Test", "status": "invisible"},
    )
    assert resp.status_code == 422


# ── List ───────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_characters_empty(client) -> None:
    universe_id = await _create_universe(client)
    resp = await client.get(f"/api/v1/characters?universe_id={universe_id}")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_characters_requires_universe_id(client) -> None:
    resp = await client.get("/api/v1/characters")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_characters_after_create(client) -> None:
    universe_id = await _create_universe(client)
    await client.post(
        "/api/v1/characters",
        json={"universe_id": universe_id, "name": "Character One"},
    )
    await client.post(
        "/api/v1/characters",
        json={"universe_id": universe_id, "name": "Character Two"},
    )
    resp = await client.get(f"/api/v1/characters?universe_id={universe_id}")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_characters_isolated_by_universe(client) -> None:
    """Characters from one universe must not appear in another."""
    u1 = await _create_universe(client, "Universe Alpha")
    u2 = await _create_universe(client, "Universe Beta")
    await client.post(
        "/api/v1/characters", json={"universe_id": u1, "name": "Alpha Hero"}
    )
    resp = await client.get(f"/api/v1/characters?universe_id={u2}")
    assert resp.json()["data"]["total"] == 0


# ── Get ────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_character_by_id(client) -> None:
    universe_id = await _create_universe(client)
    create_resp = await client.post(
        "/api/v1/characters",
        json={"universe_id": universe_id, "name": "Fetch Me"},
    )
    char_id = create_resp.json()["data"]["id"]
    resp = await client.get(f"/api/v1/characters/{char_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["id"] == char_id


@pytest.mark.asyncio
async def test_get_character_not_found(client) -> None:
    resp = await client.get("/api/v1/characters/nonexistent-id")
    assert resp.status_code == 404


# ── Patch ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_patch_character(client) -> None:
    universe_id = await _create_universe(client)
    create_resp = await client.post(
        "/api/v1/characters",
        json={"universe_id": universe_id, "name": "Patchable"},
    )
    char_id = create_resp.json()["data"]["id"]
    resp = await client.patch(
        f"/api/v1/characters/{char_id}",
        json={"role": "Villain", "status": "deceased"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["role"] == "Villain"
    assert data["status"] == "deceased"


@pytest.mark.asyncio
async def test_patch_character_not_found(client) -> None:
    resp = await client.patch(
        "/api/v1/characters/ghost-id", json={"role": "Ghost"}
    )
    assert resp.status_code == 404


# ── Delete ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_character(client) -> None:
    universe_id = await _create_universe(client)
    create_resp = await client.post(
        "/api/v1/characters",
        json={"universe_id": universe_id, "name": "Delete Me"},
    )
    char_id = create_resp.json()["data"]["id"]

    del_resp = await client.delete(f"/api/v1/characters/{char_id}")
    assert del_resp.status_code == 200

    get_resp = await client.get(f"/api/v1/characters/{char_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_character_not_found(client) -> None:
    resp = await client.delete("/api/v1/characters/ghost-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_deleted_character_excluded_from_list(client) -> None:
    universe_id = await _create_universe(client)
    create_resp = await client.post(
        "/api/v1/characters",
        json={"universe_id": universe_id, "name": "Ephemeral"},
    )
    char_id = create_resp.json()["data"]["id"]
    await client.delete(f"/api/v1/characters/{char_id}")

    resp = await client.get(f"/api/v1/characters?universe_id={universe_id}")
    assert resp.json()["data"]["total"] == 0
