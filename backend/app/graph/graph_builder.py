"""GraphBuilder — converts world entities + relationships into graph nodes and edges.

Design principles:
- Read-only: never writes to the database.
- Reuses existing repositories; does NOT duplicate Relationship data.
- Nodes are keyed by  "<entity_type>:<entity_id>"  so the same entity
  appearing as both source and target collapses into one node.
- Statistics are computed entirely in Python (no extra SQL queries).
"""

import logging
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from app.graph.schemas import GraphEdge, GraphNode, GraphResponse, GraphStatistics
from app.models.relationship import RelationshipType
from app.repositories.character import CharacterRepository
from app.repositories.location import LocationRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.relationship import RelationshipRepository
from app.repositories.universe import UniverseRepository
from app.repositories.world_object import WorldObjectRepository
from app.repositories.world_rule import WorldRuleRepository

logger = logging.getLogger(__name__)

# Maximum entities / relationships fetched per universe to stay performant.
_ENTITY_LIMIT = 1000
_RELATIONSHIP_LIMIT = 3000

# Map entity_type → lucide icon name (frontend resolves these).
_ICON_MAP: dict[str, str] = {
    "character": "User",
    "location": "MapPin",
    "organization": "Network",
    "object": "Package",
    "world_rule": "BookOpen",
}

# Human-readable labels for relationship types.
_REL_LABELS: dict[str, str] = {
    t.value: t.value.replace("_", " ").title() for t in RelationshipType
}


def _node_id(entity_type: str, entity_id: str) -> str:
    return f"{entity_type}:{entity_id}"


class GraphBuilder:
    """Assembles a ``GraphResponse`` for a given universe from the database."""

    def __init__(self, session: AsyncSession) -> None:
        self._universes = UniverseRepository(session)
        self._characters = CharacterRepository(session)
        self._locations = LocationRepository(session)
        self._organizations = OrganizationRepository(session)
        self._objects = WorldObjectRepository(session)
        self._rules = WorldRuleRepository(session)
        self._relationships = RelationshipRepository(session)

    async def build(self, universe_id: str) -> GraphResponse | None:
        """Fetch all entities and relationships, return the graph.

        Returns ``None`` if the universe does not exist.
        """
        universe = await self._universes.get_by_id(universe_id)
        if not universe:
            logger.warning("Graph requested for unknown universe_id=%s", universe_id)
            return None

        # Fetch all entity collections in parallel-ish (sequential awaits;
        # adding asyncio.gather would be an optimisation for a later sprint).
        characters = await self._characters.list_by_universe(
            universe_id, limit=_ENTITY_LIMIT
        )
        locations = await self._locations.list_by_universe(
            universe_id, limit=_ENTITY_LIMIT
        )
        organizations = await self._organizations.list_by_universe(
            universe_id, limit=_ENTITY_LIMIT
        )
        objects = await self._objects.list_by_universe(universe_id, limit=_ENTITY_LIMIT)
        rules = await self._rules.list_by_universe(universe_id, limit=_ENTITY_LIMIT)
        relationships = await self._relationships.list_for_context(
            universe_id, limit=_RELATIONSHIP_LIMIT
        )

        # ── Build entity lookup maps (id → display name) ───────────────────────
        entity_names: dict[str, str] = {}
        entity_subtitles: dict[str, str | None] = {}

        for c in characters:
            entity_names[_node_id("character", c.id)] = c.name
            entity_subtitles[_node_id("character", c.id)] = c.role

        for loc in locations:
            entity_names[_node_id("location", loc.id)] = loc.name
            entity_subtitles[_node_id("location", loc.id)] = loc.type

        for org in organizations:
            entity_names[_node_id("organization", org.id)] = org.name
            entity_subtitles[_node_id("organization", org.id)] = org.type

        for obj in objects:
            entity_names[_node_id("object", obj.id)] = obj.name
            entity_subtitles[_node_id("object", obj.id)] = obj.category

        for rule in rules:
            entity_names[_node_id("world_rule", rule.id)] = rule.title
            entity_subtitles[_node_id("world_rule", rule.id)] = rule.category

        # ── Build node set from entities ───────────────────────────────────────
        nodes: dict[str, GraphNode] = {}

        def _add_nodes_from_entities(entity_type: str, items: list) -> None:  # noqa: ANN001
            for item in items:
                nid = _node_id(entity_type, item.id)
                label_attr = "title" if entity_type == "world_rule" else "name"
                nodes[nid] = GraphNode(
                    id=nid,
                    entity_type=entity_type,
                    label=getattr(item, label_attr, item.id),
                    subtitle=entity_subtitles.get(nid),
                    icon=_ICON_MAP.get(entity_type, "Circle"),
                    metadata={"entity_id": item.id},
                )

        _add_nodes_from_entities("character", characters)
        _add_nodes_from_entities("location", locations)
        _add_nodes_from_entities("organization", organizations)
        _add_nodes_from_entities("object", objects)
        _add_nodes_from_entities("world_rule", rules)

        # For any entity referenced by a relationship but not in the entity
        # collections (e.g., over the limit), create a stub node so edges
        # always have valid source/target.
        for rel in relationships:
            src_nid = _node_id(rel.source_entity_type, rel.source_entity_id)
            tgt_nid = _node_id(rel.target_entity_type, rel.target_entity_id)
            if src_nid not in nodes:
                nodes[src_nid] = GraphNode(
                    id=src_nid,
                    entity_type=rel.source_entity_type,
                    label=entity_names.get(src_nid, rel.source_entity_id),
                    icon=_ICON_MAP.get(rel.source_entity_type, "Circle"),
                    metadata={"entity_id": rel.source_entity_id},
                )
            if tgt_nid not in nodes:
                nodes[tgt_nid] = GraphNode(
                    id=tgt_nid,
                    entity_type=rel.target_entity_type,
                    label=entity_names.get(tgt_nid, rel.target_entity_id),
                    icon=_ICON_MAP.get(rel.target_entity_type, "Circle"),
                    metadata={"entity_id": rel.target_entity_id},
                )

        # ── Build edges ────────────────────────────────────────────────────────
        edges: list[GraphEdge] = []
        for rel in relationships:
            edges.append(
                GraphEdge(
                    id=rel.id,
                    source=_node_id(rel.source_entity_type, rel.source_entity_id),
                    target=_node_id(rel.target_entity_type, rel.target_entity_id),
                    relationship_type=rel.relationship_type,
                    direction=rel.direction,
                    strength=rel.strength,
                    label=_REL_LABELS.get(rel.relationship_type, rel.relationship_type),
                )
            )

        # ── Statistics ─────────────────────────────────────────────────────────
        stats = _compute_statistics(
            nodes=list(nodes.values()),
            edges=edges,
            characters=len(characters),
            locations=len(locations),
            organizations=len(organizations),
            objects=len(objects),
            rules=len(rules),
            relationships=len(relationships),
        )

        logger.info(
            "Graph built for universe_id=%s: nodes=%d edges=%d components=%d",
            universe_id,
            stats.node_count,
            stats.edge_count,
            stats.connected_components,
        )

        return GraphResponse(
            universe_id=universe_id,
            nodes=list(nodes.values()),
            edges=edges,
            statistics=stats,
        )


# ── Statistics helpers ─────────────────────────────────────────────────────────


def _compute_statistics(
    *,
    nodes: list[GraphNode],
    edges: list[GraphEdge],
    characters: int,
    locations: int,
    organizations: int,
    objects: int,
    rules: int,
    relationships: int,
) -> GraphStatistics:
    node_ids = {n.id for n in nodes}
    n = len(node_ids)
    e = len(edges)

    # Degree map (undirected for avg-degree calculation)
    degree: dict[str, int] = defaultdict(int)
    adj: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        degree[edge.source] += 1
        degree[edge.target] += 1
        adj[edge.source].add(edge.target)
        adj[edge.target].add(edge.source)

    avg_degree = (sum(degree.values()) / n) if n > 0 else 0.0

    # Connected components via union-find
    components = _count_components(node_ids, adj)

    return GraphStatistics(
        character_count=characters,
        location_count=locations,
        organization_count=organizations,
        object_count=objects,
        rule_count=rules,
        relationship_count=relationships,
        node_count=n,
        edge_count=e,
        connected_components=components,
        average_degree=round(avg_degree, 2),
    )


def _count_components(node_ids: set[str], adj: dict[str, set[str]]) -> int:
    """Count connected components using iterative BFS."""
    visited: set[str] = set()
    count = 0
    for start in node_ids:
        if start in visited:
            continue
        count += 1
        queue = [start]
        while queue:
            node = queue.pop()
            if node in visited:
                continue
            visited.add(node)
            for neighbour in adj.get(node, set()):
                if neighbour not in visited:
                    queue.append(neighbour)
    return count
