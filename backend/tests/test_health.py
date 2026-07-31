"""Tests for the health endpoint."""

import pytest


@pytest.mark.asyncio
async def test_health_returns_200(client) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_response_body(client) -> None:
    body = (await client.get("/api/v1/health")).json()
    assert body["success"] is True
    assert body["data"]["status"] == "healthy"
    assert body["data"]["database"] == "ok"
    assert "version" in body["data"]
