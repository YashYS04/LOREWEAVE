"""Tests for the Knowledge Graph module.

Covers:
  - GraphBuilder       (empty universe, nodes, edges, statistics)
  - Graph API          (GET /graph/{universe_id})
  - Statistics         (components, average_degree)
  - _count_components  (unit)
"""

import pytest

# ── Helpers ────────────────────────────────────────────────────────────────────


async def _create_universe(client, name: str = "Graph Universe") -> str:
    resp = await client.post(
        "/api/v1/universes",
        json={"name": name, "genre": "fantasy"},
    )
    assert resp.status_code == 201
    return resp.json()["data"]["id"]


async def _create_character(client, uid: str, name: str) -> str:
    resp = await client.post(
        "/api/v1/characters",
        json={"universe_id": uid, "name": name},
    )
    assert resp.status_code == 201
    return resp.json()["data"]["id"]


async def _create_location(client, uid: str, name: str) -> str:
    resp = await client.post(
        "/api/v1/locations",
        json={"universe_id": uid, "name": name},
    )
    assert resp.status_code == 201
    return resp.json()["data"]["id"]


async def _create_org(client, uid: str, name: str) -> str:
    resp = await client.post(
        "/api/v1/organizations",
        json={"universe_id": uid, "name": name},
    )
    assert resp.status_code == 201
    return resp.json()["data"]["id"]


async def _create_relationship(
    client,
    uid: str,
    src_type: str,
    src_id: str,
    tgt_type: str,
    tgt_id: str,
    rel_type: str = "ally_of",
) -> str:
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
    assert resp.status_code == 201
    return resp.json()["data"]["id"]


# ── GraphBuilder unit tests (via test_session) ────────────────────────────────


@pytest.mark.asyncio
async def test_graph_builder_returns_none_for_unknown_universe(test_session) -> None:
    from app.graph.graph_builder import GraphBuilder

    builder = GraphBuilder(test_session)
    result = await builder.build("nonexistent-uuid")
    assert result is None


@pytest.mark.asyncio
async def test_graph_builder_empty_universe(client) -> None:
    """A universe with no entities should return an empty graph."""
    uid = await _create_universe(client)

    # Use the API instead of test_session because client overrides get_db.
    resp = await client.get(f"/api/v1/graph/{uid}")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["nodes"] == []
    assert data["edges"] == []
    stats = data["statistics"]
    assert stats["node_count"] == 0
    assert stats["edge_count"] == 0
    assert stats["connected_components"] == 0
    assert stats["average_degree"] == 0.0


@pytest.mark.asyncio
async def test_graph_builder_nodes_from_entities(client) -> None:
    uid = await _create_universe(client)
    cid = await _create_character(client, uid, "Aria")
    lid = await _create_location(client, uid, "Iron Citadel")

    resp = await client.get(f"/api/v1/graph/{uid}")
    assert resp.status_code == 200
    data = resp.json()["data"]

    node_ids = {n["id"] for n in data["nodes"]}
    assert f"character:{cid}" in node_ids
    assert f"location:{lid}" in node_ids

    char_node = next(n for n in data["nodes"] if n["id"] == f"character:{cid}")
    assert char_node["label"] == "Aria"
    assert char_node["entity_type"] == "character"
    assert char_node["icon"] == "User"

    loc_node = next(n for n in data["nodes"] if n["id"] == f"location:{lid}")
    assert loc_node["label"] == "Iron Citadel"
    assert loc_node["icon"] == "MapPin"


@pytest.mark.asyncio
async def test_graph_builder_edges_from_relationships(client) -> None:
    uid = await _create_universe(client)
    cid = await _create_character(client, uid, "Kael")
    lid = await _create_location(client, uid, "Dark Forest")
    rid = await _create_relationship(
        client, uid, "character", cid, "location", lid, "lives_in"
    )

    resp = await client.get(f"/api/v1/graph/{uid}")
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert len(data["edges"]) == 1
    edge = data["edges"][0]
    assert edge["id"] == rid
    assert edge["source"] == f"character:{cid}"
    assert edge["target"] == f"location:{lid}"
    assert edge["relationship_type"] == "lives_in"
    assert edge["label"] == "Lives In"


@pytest.mark.asyncio
async def test_graph_edge_strength_and_direction(client) -> None:
    uid = await _create_universe(client)
    cid1 = await _create_character(client, uid, "Alpha")
    cid2 = await _create_character(client, uid, "Beta")
    resp = await client.post(
        "/api/v1/relationships",
        json={
            "universe_id": uid,
            "source_entity_type": "character",
            "source_entity_id": cid1,
            "target_entity_type": "character",
            "target_entity_id": cid2,
            "relationship_type": "ally_of",
            "strength": 8,
            "direction": "bidirectional",
        },
    )
    assert resp.status_code == 201

    resp = await client.get(f"/api/v1/graph/{uid}")
    edge = resp.json()["data"]["edges"][0]
    assert edge["strength"] == 8
    assert edge["direction"] == "bidirectional"


# ── Statistics tests ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_statistics_counts(client) -> None:
    uid = await _create_universe(client)
    cid1 = await _create_character(client, uid, "C1")
    cid2 = await _create_character(client, uid, "C2")
    lid = await _create_location(client, uid, "L1")
    await _create_org(client, uid, "O1")

    await _create_relationship(client, uid, "character", cid1, "character", cid2)
    await _create_relationship(
        client, uid, "character", cid1, "location", lid, "lives_in"
    )

    resp = await client.get(f"/api/v1/graph/{uid}")
    stats = resp.json()["data"]["statistics"]
    assert stats["character_count"] == 2
    assert stats["location_count"] == 1
    assert stats["organization_count"] == 1
    assert stats["relationship_count"] == 2
    assert stats["node_count"] == 4
    assert stats["edge_count"] == 2


@pytest.mark.asyncio
async def test_statistics_average_degree(client) -> None:
    """3 nodes in a triangle → each degree=2, avg=2.0."""
    uid = await _create_universe(client)
    cids = [await _create_character(client, uid, f"C{i}") for i in range(3)]
    await _create_relationship(client, uid, "character", cids[0], "character", cids[1])
    await _create_relationship(client, uid, "character", cids[1], "character", cids[2])
    await _create_relationship(client, uid, "character", cids[2], "character", cids[0])

    resp = await client.get(f"/api/v1/graph/{uid}")
    stats = resp.json()["data"]["statistics"]
    assert stats["average_degree"] == 2.0


@pytest.mark.asyncio
async def test_statistics_connected_components(client) -> None:
    """Two disconnected pairs → 2 components."""
    uid = await _create_universe(client)
    cids = [await _create_character(client, uid, f"Char{i}") for i in range(4)]
    # Pair A
    await _create_relationship(client, uid, "character", cids[0], "character", cids[1])
    # Pair B — isolated from A
    await _create_relationship(client, uid, "character", cids[2], "character", cids[3])

    resp = await client.get(f"/api/v1/graph/{uid}")
    stats = resp.json()["data"]["statistics"]
    assert stats["connected_components"] == 2


@pytest.mark.asyncio
async def test_statistics_isolated_nodes_are_own_components(client) -> None:
    """3 characters with no edges → 3 components."""
    uid = await _create_universe(client)
    for i in range(3):
        await _create_character(client, uid, f"Iso{i}")

    resp = await client.get(f"/api/v1/graph/{uid}")
    stats = resp.json()["data"]["statistics"]
    assert stats["connected_components"] == 3


# ── _count_components unit test ────────────────────────────────────────────────


def test_count_components_single_node() -> None:
    from collections import defaultdict

    from app.graph.graph_builder import _count_components

    adj: dict[str, set[str]] = defaultdict(set)
    result = _count_components({"a"}, adj)
    assert result == 1


def test_count_components_two_components() -> None:
    from collections import defaultdict

    from app.graph.graph_builder import _count_components

    adj: dict[str, set[str]] = defaultdict(set)
    adj["a"].add("b")
    adj["b"].add("a")
    result = _count_components({"a", "b", "c"}, adj)
    assert result == 2


def test_count_components_fully_connected() -> None:
    from collections import defaultdict

    from app.graph.graph_builder import _count_components

    adj: dict[str, set[str]] = defaultdict(set)
    for x, y in [("a", "b"), ("b", "c"), ("c", "a")]:
        adj[x].add(y)
        adj[y].add(x)
    result = _count_components({"a", "b", "c"}, adj)
    assert result == 1


# ── API tests ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_graph_api_not_found(client) -> None:
    resp = await client.get("/api/v1/graph/nonexistent-universe-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_graph_api_response_envelope(client) -> None:
    uid = await _create_universe(client)
    resp = await client.get(f"/api/v1/graph/{uid}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "data" in body
    data = body["data"]
    assert "nodes" in data
    assert "edges" in data
    assert "statistics" in data
    assert data["universe_id"] == uid


@pytest.mark.asyncio
async def test_graph_isolated_by_universe(client) -> None:
    """Graph for universe B should not include entities from universe A."""
    uid_a = await _create_universe(client, "Universe A")
    uid_b = await _create_universe(client, "Universe B")

    await _create_character(client, uid_a, "Only In A")

    resp = await client.get(f"/api/v1/graph/{uid_b}")
    data = resp.json()["data"]
    assert data["nodes"] == []


@pytest.mark.asyncio
async def test_graph_stub_nodes_for_orphan_relationships(client) -> None:
    """Relationships referencing entity IDs with no matching entity get stub nodes."""
    uid = await _create_universe(client)
    # Create relationship with raw IDs that don't correspond to any entity record.
    resp = await client.post(
        "/api/v1/relationships",
        json={
            "universe_id": uid,
            "source_entity_type": "character",
            "source_entity_id": "orphan-src",
            "target_entity_type": "location",
            "target_entity_id": "orphan-tgt",
            "relationship_type": "lives_in",
        },
    )
    assert resp.status_code == 201

    resp = await client.get(f"/api/v1/graph/{uid}")
    data = resp.json()["data"]
    node_ids = {n["id"] for n in data["nodes"]}
    assert "character:orphan-src" in node_ids
    assert "location:orphan-tgt" in node_ids
    # Stub nodes fall back to entity_id as label
    stub = next(n for n in data["nodes"] if n["id"] == "character:orphan-src")
    assert stub["label"] == "orphan-src"


@pytest.mark.asyncio
async def test_graph_node_deduplication(client) -> None:
    """An entity appearing in multiple relationships is only one node."""
    uid = await _create_universe(client)
    cid = await _create_character(client, uid, "Hub")
    c2 = await _create_character(client, uid, "Spoke1")
    c3 = await _create_character(client, uid, "Spoke2")
    await _create_relationship(client, uid, "character", cid, "character", c2)
    await _create_relationship(client, uid, "character", cid, "character", c3)

    resp = await client.get(f"/api/v1/graph/{uid}")
    data = resp.json()["data"]
    hub_nodes = [n for n in data["nodes"] if n["id"] == f"character:{cid}"]
    assert len(hub_nodes) == 1
