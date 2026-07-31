/**
 * Graph TypeScript types — mirrors backend graph schemas.
 */

// ── Node ──────────────────────────────────────────────────────────────────────

export interface GraphNode {
  id: string;
  entity_type: "character" | "location" | "organization" | "object" | "world_rule";
  label: string;
  subtitle: string | null;
  icon: string;
  metadata: Record<string, unknown>;
}

// ── Edge ──────────────────────────────────────────────────────────────────────

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relationship_type: string;
  direction: "unidirectional" | "bidirectional";
  strength: number | null;
  label: string;
}

// ── Statistics ─────────────────────────────────────────────────────────────────

export interface GraphStatistics {
  character_count: number;
  location_count: number;
  organization_count: number;
  object_count: number;
  rule_count: number;
  relationship_count: number;
  node_count: number;
  edge_count: number;
  connected_components: number;
  average_degree: number;
}

// ── Response ───────────────────────────────────────────────────────────────────

export interface GraphData {
  universe_id: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  statistics: GraphStatistics;
}

// ── Filter state ───────────────────────────────────────────────────────────────

export interface GraphFilters {
  entityTypes: Set<string>;
  relationshipTypes: Set<string>;
  minStrength: number;
}
