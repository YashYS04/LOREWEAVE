"""Tests for soft-delete, pagination, error handling, and health enhancements."""

import pytest

# ── Soft Delete ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_returns_200_with_envelope(client) -> None:
    """DELETE now returns 200 with success envelope, not 204."""
    create = await client.post(
        "/api/v1/universes",
        json={"name": "Soft Delete Me", "genre": "fantasy"},
    )
    assert create.status_code == 201
    uid = create.json()["data"]["id"]

    resp = await client.delete(f"/api/v1/universes/{uid}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["message"] == "Universe deleted successfully."


@pytest.mark.asyncio
async def test_soft_deleted_universe_not_in_list(client) -> None:
    """Soft-deleted universes must not appear in the list."""
    create = await client.post(
        "/api/v1/universes",
        json={"name": "Ghost Universe", "genre": "horror"},
    )
    uid = create.json()["data"]["id"]
    await client.delete(f"/api/v1/universes/{uid}")

    resp = await client.get("/api/v1/universes")
    ids = [u["id"] for u in resp.json()["data"]["items"]]
    assert uid not in ids


@pytest.mark.asyncio
async def test_soft_deleted_universe_not_fetchable_by_id(client) -> None:
    """GET /{id} on a soft-deleted universe returns 404."""
    create = await client.post(
        "/api/v1/universes",
        json={"name": "Phantom Universe", "genre": "mystery"},
    )
    uid = create.json()["data"]["id"]
    await client.delete(f"/api/v1/universes/{uid}")

    resp = await client.get(f"/api/v1/universes/{uid}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_double_delete_returns_404(client) -> None:
    """Deleting an already soft-deleted universe returns 404."""
    create = await client.post(
        "/api/v1/universes",
        json={"name": "Delete Twice", "genre": "thriller"},
    )
    uid = create.json()["data"]["id"]
    await client.delete(f"/api/v1/universes/{uid}")

    resp = await client.delete(f"/api/v1/universes/{uid}")
    assert resp.status_code == 404


# ── Pagination ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_response_includes_pagination_fields(client) -> None:
    """List response must include total, limit, and offset."""
    resp = await client.get("/api/v1/universes?skip=0&limit=10")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert data["limit"] == 10
    assert data["offset"] == 0


@pytest.mark.asyncio
async def test_pagination_limit(client) -> None:
    """limit parameter must cap the returned items."""
    for i in range(5):
        await client.post(
            "/api/v1/universes",
            json={"name": f"Paginate Universe {i}", "genre": "adventure"},
        )
    resp = await client.get("/api/v1/universes?skip=0&limit=3")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data["items"]) == 3
    assert data["total"] == 5
    assert data["limit"] == 3


@pytest.mark.asyncio
async def test_pagination_offset(client) -> None:
    """offset parameter must skip the correct number of rows."""
    for i in range(4):
        await client.post(
            "/api/v1/universes",
            json={"name": f"Offset Universe {i}", "genre": "romance"},
        )
    # Fetch second page (offset=2, limit=2)
    resp = await client.get("/api/v1/universes?skip=2&limit=2")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data["items"]) == 2
    assert data["offset"] == 2


@pytest.mark.asyncio
async def test_pagination_soft_deleted_excluded_from_total(client) -> None:
    """total must not count soft-deleted rows."""
    await client.post(
        "/api/v1/universes",
        json={"name": "Count Me", "genre": "fantasy"},
    )
    r2 = await client.post(
        "/api/v1/universes",
        json={"name": "Dont Count Me", "genre": "fantasy"},
    )
    uid2 = r2.json()["data"]["id"]
    await client.delete(f"/api/v1/universes/{uid2}")

    resp = await client.get("/api/v1/universes")
    assert resp.json()["data"]["total"] == 1


# ── Standard Response Envelopes ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_returns_success_envelope(client) -> None:
    resp = await client.post(
        "/api/v1/universes",
        json={"name": "Envelope Test", "genre": "steampunk"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert "data" in body
    assert body["data"]["slug"] == "envelope-test"


@pytest.mark.asyncio
async def test_get_returns_success_envelope(client) -> None:
    create = await client.post(
        "/api/v1/universes",
        json={"name": "Fetch Envelope", "genre": "cyberpunk"},
    )
    uid = create.json()["data"]["id"]
    resp = await client.get(f"/api/v1/universes/{uid}")
    assert resp.status_code == 200
    assert resp.json()["success"] is True


# ── Error Handler ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_404_returns_error_envelope(client) -> None:
    resp = await client.get("/api/v1/universes/does-not-exist-abc")
    assert resp.status_code == 404
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "NOT_FOUND"
    assert "message" in body["error"]


@pytest.mark.asyncio
async def test_422_returns_error_envelope(client) -> None:
    resp = await client.post(
        "/api/v1/universes",
        json={"name": "", "genre": "fantasy"},
    )
    assert resp.status_code == 422
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_invalid_genre_returns_422_envelope(client) -> None:
    resp = await client.post(
        "/api/v1/universes",
        json={"name": "Bad Genre", "genre": "not_valid"},
    )
    assert resp.status_code == 422
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


# ── Health ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_health_includes_version(client) -> None:
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "version" in data
    assert "database" in data


@pytest.mark.asyncio
async def test_health_database_ok(client) -> None:
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["data"]["database"] == "ok"
    assert resp.json()["data"]["status"] == "healthy"
