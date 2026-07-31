"""Pydantic v2 schemas for the graph API."""

from pydantic import BaseModel

# ── Node ──────────────────────────────────────────────────────────────────────


class GraphNode(BaseModel):
    """A single node in the knowledge graph."""

    id: str
    entity_type: str   # character | location | organization | object | world_rule
    label: str         # primary display name
    subtitle: str | None = None   # role, type, category, etc.
    icon: str          # lucide icon name hint for the frontend
    metadata: dict[str, object] = {}


# ── Edge ──────────────────────────────────────────────────────────────────────


class GraphEdge(BaseModel):
    """A directed edge between two nodes."""

    id: str
    source: str            # node id
    target: str            # node id
    relationship_type: str
    direction: str         # unidirectional | bidirectional
    strength: int | None   # 1–10 or None
    label: str             # human-readable relationship type


# ── Statistics ─────────────────────────────────────────────────────────────────


class GraphStatistics(BaseModel):
    character_count: int
    location_count: int
    organization_count: int
    object_count: int
    rule_count: int
    relationship_count: int
    node_count: int
    edge_count: int
    connected_components: int
    average_degree: float


# ── Response ───────────────────────────────────────────────────────────────────


class GraphResponse(BaseModel):
    universe_id: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    statistics: GraphStatistics
