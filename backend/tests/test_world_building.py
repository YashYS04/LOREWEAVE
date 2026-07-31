"""Tests for Location, Organization, WorldObject, WorldRule CRUD endpoints."""

import pytest

# ── Shared helper ──────────────────────────────────────────────────────────────


async def _create_universe(client, name: str = "Test Universe") -> str:
    resp = await client.post(
        "/api/v1/universes",
        json={"name": name, "genre": "fantasy"},
    )
    assert resp.status_code == 201
    return resp.json()["data"]["id"]


# ==============================================================================
# LOCATIONS
# ==============================================================================


@pytest.mark.asyncio
async def test_create_location_minimal(client) -> None:
    uid = await _create_universe(client)
    resp = await client.post(
        "/api/v1/locations",
        json={"universe_id": uid, "name": "Ember Falls"},
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["name"] == "Ember Falls"
    assert data["universe_id"] == uid
    assert "id" in data


@pytest.mark.asyncio
async def test_create_location_full(client) -> None:
    uid = await _create_universe(client, "Full Location Universe")
    resp = await client.post(
        "/api/v1/locations",
        json={
            "universe_id": uid,
            "name": "The Iron Citadel",
            "type": "Fortress",
            "description": "A massive iron fortress atop a volcanic ridge.",
            "climate": "Arid, volcanic",
            "culture": "Militaristic society governed by an Iron Council.",
            "population": "~12,000",
            "notes": "Contains the Vault of Echoes.",
        },
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["type"] == "Fortress"
    assert data["climate"] == "Arid, volcanic"


@pytest.mark.asyncio
async def test_create_location_blank_name(client) -> None:
    uid = await _create_universe(client)
    resp = await client.post(
        "/api/v1/locations", json={"universe_id": uid, "name": "   "}
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_locations_empty(client) -> None:
    uid = await _create_universe(client)
    resp = await client.get(f"/api/v1/locations?universe_id={uid}")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_locations_after_create(client) -> None:
    uid = await _create_universe(client)
    await client.post("/api/v1/locations", json={"universe_id": uid, "name": "Loc A"})
    await client.post("/api/v1/locations", json={"universe_id": uid, "name": "Loc B"})
    resp = await client.get(f"/api/v1/locations?universe_id={uid}")
    assert resp.json()["data"]["total"] == 2


@pytest.mark.asyncio
async def test_list_locations_requires_universe_id(client) -> None:
    resp = await client.get("/api/v1/locations")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_location_by_id(client) -> None:
    uid = await _create_universe(client)
    create = await client.post(
        "/api/v1/locations", json={"universe_id": uid, "name": "Fetch Me"}
    )
    loc_id = create.json()["data"]["id"]
    resp = await client.get(f"/api/v1/locations/{loc_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["id"] == loc_id


@pytest.mark.asyncio
async def test_get_location_not_found(client) -> None:
    resp = await client.get("/api/v1/locations/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_patch_location(client) -> None:
    uid = await _create_universe(client)
    create = await client.post(
        "/api/v1/locations", json={"universe_id": uid, "name": "Patchable"}
    )
    loc_id = create.json()["data"]["id"]
    resp = await client.patch(
        f"/api/v1/locations/{loc_id}", json={"climate": "Tropical", "type": "Island"}
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["climate"] == "Tropical"


@pytest.mark.asyncio
async def test_delete_location(client) -> None:
    uid = await _create_universe(client)
    create = await client.post(
        "/api/v1/locations", json={"universe_id": uid, "name": "Delete Me"}
    )
    loc_id = create.json()["data"]["id"]
    assert (await client.delete(f"/api/v1/locations/{loc_id}")).status_code == 200
    assert (await client.get(f"/api/v1/locations/{loc_id}")).status_code == 404


@pytest.mark.asyncio
async def test_deleted_location_excluded_from_list(client) -> None:
    uid = await _create_universe(client)
    create = await client.post(
        "/api/v1/locations", json={"universe_id": uid, "name": "Ephemeral Place"}
    )
    loc_id = create.json()["data"]["id"]
    await client.delete(f"/api/v1/locations/{loc_id}")
    assert (await client.get(f"/api/v1/locations?universe_id={uid}")).json()["data"][
        "total"
    ] == 0


@pytest.mark.asyncio
async def test_locations_isolated_by_universe(client) -> None:
    u1 = await _create_universe(client, "Loc Universe A")
    u2 = await _create_universe(client, "Loc Universe B")
    await client.post("/api/v1/locations", json={"universe_id": u1, "name": "Place A"})
    assert (await client.get(f"/api/v1/locations?universe_id={u2}")).json()["data"][
        "total"
    ] == 0


# ==============================================================================
# ORGANIZATIONS
# ==============================================================================


@pytest.mark.asyncio
async def test_create_organization_minimal(client) -> None:
    uid = await _create_universe(client)
    resp = await client.post(
        "/api/v1/organizations",
        json={"universe_id": uid, "name": "Order of the Flame"},
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["name"] == "Order of the Flame"
    assert data["universe_id"] == uid


@pytest.mark.asyncio
async def test_create_organization_full(client) -> None:
    uid = await _create_universe(client, "Org Full Universe")
    resp = await client.post(
        "/api/v1/organizations",
        json={
            "universe_id": uid,
            "name": "The Shadow Conclave",
            "type": "Secret Society",
            "description": "Operates from the undercity.",
            "leader": "The Masked One",
            "purpose": "Preserve the old magic at any cost.",
            "notes": "Known only to a handful of outsiders.",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["type"] == "Secret Society"


@pytest.mark.asyncio
async def test_create_organization_blank_name(client) -> None:
    uid = await _create_universe(client)
    resp = await client.post(
        "/api/v1/organizations", json={"universe_id": uid, "name": " "}
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_organizations_empty(client) -> None:
    uid = await _create_universe(client)
    resp = await client.get(f"/api/v1/organizations?universe_id={uid}")
    assert resp.json()["data"]["total"] == 0


@pytest.mark.asyncio
async def test_list_organizations_after_create(client) -> None:
    uid = await _create_universe(client)
    await client.post(
        "/api/v1/organizations", json={"universe_id": uid, "name": "Org A"}
    )
    await client.post(
        "/api/v1/organizations", json={"universe_id": uid, "name": "Org B"}
    )
    assert (await client.get(f"/api/v1/organizations?universe_id={uid}")).json()[
        "data"
    ]["total"] == 2


@pytest.mark.asyncio
async def test_get_organization_by_id(client) -> None:
    uid = await _create_universe(client)
    create = await client.post(
        "/api/v1/organizations", json={"universe_id": uid, "name": "Fetch Org"}
    )
    oid = create.json()["data"]["id"]
    assert (await client.get(f"/api/v1/organizations/{oid}")).status_code == 200


@pytest.mark.asyncio
async def test_get_organization_not_found(client) -> None:
    assert (await client.get("/api/v1/organizations/no-such-id")).status_code == 404


@pytest.mark.asyncio
async def test_patch_organization(client) -> None:
    uid = await _create_universe(client)
    create = await client.post(
        "/api/v1/organizations", json={"universe_id": uid, "name": "Patch Org"}
    )
    oid = create.json()["data"]["id"]
    resp = await client.patch(
        f"/api/v1/organizations/{oid}", json={"leader": "Grand Master"}
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["leader"] == "Grand Master"


@pytest.mark.asyncio
async def test_delete_organization(client) -> None:
    uid = await _create_universe(client)
    create = await client.post(
        "/api/v1/organizations", json={"universe_id": uid, "name": "Delete Org"}
    )
    oid = create.json()["data"]["id"]
    assert (await client.delete(f"/api/v1/organizations/{oid}")).status_code == 200
    assert (await client.get(f"/api/v1/organizations/{oid}")).status_code == 404


# ==============================================================================
# OBJECTS
# ==============================================================================


@pytest.mark.asyncio
async def test_create_object_minimal(client) -> None:
    uid = await _create_universe(client)
    resp = await client.post(
        "/api/v1/objects",
        json={"universe_id": uid, "name": "The Shard of Dawn"},
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["name"] == "The Shard of Dawn"
    assert data["universe_id"] == uid


@pytest.mark.asyncio
async def test_create_object_full(client) -> None:
    uid = await _create_universe(client, "Obj Full Universe")
    resp = await client.post(
        "/api/v1/objects",
        json={
            "universe_id": uid,
            "name": "Voidbane Blade",
            "category": "Weapon",
            "description": "A sword forged from a collapsed star.",
            "origin": "Created by the First Artificer in the Age of Silence.",
            "owner": "Kael Dorn",
            "abilities": "Cuts through wards and magical barriers.",
            "notes": "Cannot be wielded by those with fear in their heart.",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["category"] == "Weapon"


@pytest.mark.asyncio
async def test_create_object_blank_name(client) -> None:
    uid = await _create_universe(client)
    resp = await client.post("/api/v1/objects", json={"universe_id": uid, "name": "  "})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_objects_empty(client) -> None:
    uid = await _create_universe(client)
    resp = await client.get(f"/api/v1/objects?universe_id={uid}")
    assert resp.json()["data"]["total"] == 0


@pytest.mark.asyncio
async def test_list_objects_after_create(client) -> None:
    uid = await _create_universe(client)
    await client.post("/api/v1/objects", json={"universe_id": uid, "name": "Obj A"})
    await client.post("/api/v1/objects", json={"universe_id": uid, "name": "Obj B"})
    assert (await client.get(f"/api/v1/objects?universe_id={uid}")).json()["data"][
        "total"
    ] == 2


@pytest.mark.asyncio
async def test_get_object_by_id(client) -> None:
    uid = await _create_universe(client)
    create = await client.post(
        "/api/v1/objects", json={"universe_id": uid, "name": "Fetch Obj"}
    )
    oid = create.json()["data"]["id"]
    assert (await client.get(f"/api/v1/objects/{oid}")).status_code == 200


@pytest.mark.asyncio
async def test_get_object_not_found(client) -> None:
    assert (await client.get("/api/v1/objects/no-such-id")).status_code == 404


@pytest.mark.asyncio
async def test_patch_object(client) -> None:
    uid = await _create_universe(client)
    create = await client.post(
        "/api/v1/objects", json={"universe_id": uid, "name": "Patch Obj"}
    )
    oid = create.json()["data"]["id"]
    resp = await client.patch(f"/api/v1/objects/{oid}", json={"owner": "New Owner"})
    assert resp.status_code == 200
    assert resp.json()["data"]["owner"] == "New Owner"


@pytest.mark.asyncio
async def test_delete_object(client) -> None:
    uid = await _create_universe(client)
    create = await client.post(
        "/api/v1/objects", json={"universe_id": uid, "name": "Delete Obj"}
    )
    oid = create.json()["data"]["id"]
    assert (await client.delete(f"/api/v1/objects/{oid}")).status_code == 200
    assert (await client.get(f"/api/v1/objects/{oid}")).status_code == 404


# ==============================================================================
# WORLD RULES
# ==============================================================================


@pytest.mark.asyncio
async def test_create_rule_minimal(client) -> None:
    uid = await _create_universe(client)
    resp = await client.post(
        "/api/v1/rules",
        json={"universe_id": uid, "title": "Law of Conservation of Magic"},
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["title"] == "Law of Conservation of Magic"
    assert data["universe_id"] == uid


@pytest.mark.asyncio
async def test_create_rule_full(client) -> None:
    uid = await _create_universe(client, "Rule Full Universe")
    resp = await client.post(
        "/api/v1/rules",
        json={
            "universe_id": uid,
            "title": "Principle of Sympathetic Resonance",
            "category": "Magic System",
            "description": "Objects that were once connected retain a link forever.",
            "limitations": "Connection weakens over time and distance.",
            "exceptions": "Blood bonds never weaken.",
            "notes": "Central to the curse subplot.",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["category"] == "Magic System"


@pytest.mark.asyncio
async def test_create_rule_blank_title(client) -> None:
    uid = await _create_universe(client)
    resp = await client.post("/api/v1/rules", json={"universe_id": uid, "title": "  "})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_rules_empty(client) -> None:
    uid = await _create_universe(client)
    resp = await client.get(f"/api/v1/rules?universe_id={uid}")
    assert resp.json()["data"]["total"] == 0


@pytest.mark.asyncio
async def test_list_rules_after_create(client) -> None:
    uid = await _create_universe(client)
    await client.post("/api/v1/rules", json={"universe_id": uid, "title": "Rule A"})
    await client.post("/api/v1/rules", json={"universe_id": uid, "title": "Rule B"})
    assert (await client.get(f"/api/v1/rules?universe_id={uid}")).json()["data"][
        "total"
    ] == 2


@pytest.mark.asyncio
async def test_list_rules_requires_universe_id(client) -> None:
    assert (await client.get("/api/v1/rules")).status_code == 422


@pytest.mark.asyncio
async def test_get_rule_by_id(client) -> None:
    uid = await _create_universe(client)
    create = await client.post(
        "/api/v1/rules", json={"universe_id": uid, "title": "Fetch Rule"}
    )
    rid = create.json()["data"]["id"]
    assert (await client.get(f"/api/v1/rules/{rid}")).status_code == 200


@pytest.mark.asyncio
async def test_get_rule_not_found(client) -> None:
    assert (await client.get("/api/v1/rules/no-such-id")).status_code == 404


@pytest.mark.asyncio
async def test_patch_rule(client) -> None:
    uid = await _create_universe(client)
    create = await client.post(
        "/api/v1/rules", json={"universe_id": uid, "title": "Patch Rule"}
    )
    rid = create.json()["data"]["id"]
    resp = await client.patch(
        f"/api/v1/rules/{rid}",
        json={"category": "Physics", "limitations": "Only applies above ground."},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["category"] == "Physics"


@pytest.mark.asyncio
async def test_delete_rule(client) -> None:
    uid = await _create_universe(client)
    create = await client.post(
        "/api/v1/rules", json={"universe_id": uid, "title": "Delete Rule"}
    )
    rid = create.json()["data"]["id"]
    assert (await client.delete(f"/api/v1/rules/{rid}")).status_code == 200
    assert (await client.get(f"/api/v1/rules/{rid}")).status_code == 404


@pytest.mark.asyncio
async def test_deleted_rule_excluded_from_list(client) -> None:
    uid = await _create_universe(client)
    create = await client.post(
        "/api/v1/rules", json={"universe_id": uid, "title": "Ephemeral Rule"}
    )
    rid = create.json()["data"]["id"]
    await client.delete(f"/api/v1/rules/{rid}")
    assert (await client.get(f"/api/v1/rules?universe_id={uid}")).json()["data"][
        "total"
    ] == 0


@pytest.mark.asyncio
async def test_rules_isolated_by_universe(client) -> None:
    u1 = await _create_universe(client, "Rule Universe A")
    u2 = await _create_universe(client, "Rule Universe B")
    await client.post(
        "/api/v1/rules", json={"universe_id": u1, "title": "Rule Only in A"}
    )
    assert (await client.get(f"/api/v1/rules?universe_id={u2}")).json()["data"][
        "total"
    ] == 0
