"use client";

/**
 * Knowledge Graph page — interactive visualization of universe entities and
 * their relationships, powered by @xyflow/react (React Flow v12).
 *
 * Architecture:
 *   - Data fetched once via useGraph hook (TanStack Query).
 *   - Nodes and edges are transformed from GraphData → React Flow format.
 *   - Custom node components per entity type.
 *   - Custom edge with label + variable stroke width (strength).
 *   - Client-side search highlights matching nodes.
 *   - Client-side filters hide non-matching nodes and their edges.
 *   - Auto-layout uses a simple force-like grid spread; no external layout lib.
 */

import { use, useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  ReactFlow,
  ReactFlowProvider,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  useReactFlow,
  Handle,
  Position,
  MarkerType,
  Panel,
  type Node,
  type Edge,
  type NodeTypes,
  type EdgeTypes,
  type NodeProps,
  type EdgeProps,
  getStraightPath,
  BaseEdge,
  EdgeLabelRenderer,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { motion } from "framer-motion";
import {
  AlertCircle,
  BookOpen,
  ChevronDown,
  GitFork,
  Loader2,
  MapPin,
  Network,
  Package,
  Search,
  Share2,
  User,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { EntityPageShell } from "@/components/entity";
import { useUniverseBySlug } from "@/hooks/use-universes";
import { useGraph } from "@/hooks/use-graph";
import type { GraphData, GraphFilters, GraphNode, GraphEdge } from "@/types/graph";
import { RELATIONSHIP_TYPE_LABELS, type RelationshipType } from "@/types/relationship";

// ── Entity type config ─────────────────────────────────────────────────────────

const ENTITY_CONFIG: Record<
  string,
  { icon: React.ElementType; color: string; bg: string; border: string }
> = {
  character: { icon: User, color: "text-blue-600", bg: "bg-blue-50", border: "border-blue-200" },
  location: { icon: MapPin, color: "text-green-600", bg: "bg-green-50", border: "border-green-200" },
  organization: { icon: Network, color: "text-purple-600", bg: "bg-purple-50", border: "border-purple-200" },
  object: { icon: Package, color: "text-orange-600", bg: "bg-orange-50", border: "border-orange-200" },
  world_rule: { icon: BookOpen, color: "text-rose-600", bg: "bg-rose-50", border: "border-rose-200" },
};

const DEFAULT_CONFIG = {
  icon: GitFork,
  color: "text-muted-foreground",
  bg: "bg-muted",
  border: "border-border",
};

// ── Custom node component ──────────────────────────────────────────────────────

function EntityNode({ data }: NodeProps) {
  const cfg = ENTITY_CONFIG[data.entityType as string] ?? DEFAULT_CONFIG;
  const Icon = cfg.icon;
  const isHighlighted = data.highlighted as boolean | undefined;
  const isDimmed = data.dimmed as boolean | undefined;

  return (
    <div
      className={`
        flex min-w-[110px] max-w-[160px] flex-col items-center gap-1 rounded-xl border-2 p-2.5 text-center
        shadow-sm transition-all
        ${cfg.bg} ${cfg.border}
        ${isHighlighted ? "ring-2 ring-yellow-400 ring-offset-1 scale-110" : ""}
        ${isDimmed ? "opacity-30" : "opacity-100"}
      `}
    >
      <Handle type="target" position={Position.Top} className="!bg-transparent !border-0 !w-0 !h-0" />
      <div className={`flex h-8 w-8 items-center justify-center rounded-full border ${cfg.border} ${cfg.bg}`}>
        <Icon className={`h-4 w-4 ${cfg.color}`} />
      </div>
      <div className="min-w-0 w-full">
        <p className="truncate text-[11px] font-semibold leading-tight text-foreground">
          {data.label as string}
        </p>
        {(data.subtitle as string | null | undefined) && (
          <p className="truncate text-[10px] text-muted-foreground">{data.subtitle as string}</p>
        )}
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-transparent !border-0 !w-0 !h-0" />
    </div>
  );
}

// ── Custom edge component ──────────────────────────────────────────────────────

function RelationshipEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  data,
  markerEnd,
  markerStart,
  style,
}: EdgeProps) {
  const [edgePath, labelX, labelY] = getStraightPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
  });

  const strength = (data?.strength as number | null) ?? null;
  const strokeWidth = strength != null ? 1 + (strength / 10) * 3 : 1.5;
  const label = data?.label as string | undefined;
  const isDimmed = data?.dimmed as boolean | undefined;

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        markerEnd={markerEnd}
        markerStart={markerStart}
        style={{
          ...style,
          strokeWidth,
          opacity: isDimmed ? 0.15 : 0.7,
        }}
      />
      {label && (
        <EdgeLabelRenderer>
          <div
            style={{
              position: "absolute",
              transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
              pointerEvents: "none",
              opacity: isDimmed ? 0.15 : 1,
            }}
            className="rounded-full border border-border bg-background/90 px-1.5 py-0.5 text-[9px] font-medium text-muted-foreground shadow-sm"
          >
            {label}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
}

const nodeTypes: NodeTypes = { entity: EntityNode };
const edgeTypes: EdgeTypes = { relationship: RelationshipEdge };

// ── Layout ─────────────────────────────────────────────────────────────────────

const COL_WIDTH = 200;
const ROW_HEIGHT = 150;

function computeLayout(nodes: GraphNode[]): Map<string, { x: number; y: number }> {
  const positions = new Map<string, { x: number; y: number }>();

  // Group by entity type, place each group in its own column.
  const groups: Record<string, GraphNode[]> = {};
  for (const node of nodes) {
    (groups[node.entity_type] ??= []).push(node);
  }

  const typeOrder = ["character", "organization", "location", "object", "world_rule"];
  let col = 0;

  for (const entityType of typeOrder) {
    const group = groups[entityType];
    if (!group?.length) continue;
    group.forEach((node, row) => {
      // Stagger odd rows by half a column to spread overlapping nodes.
      const xOffset = row % 2 === 0 ? 0 : COL_WIDTH * 0.4;
      positions.set(node.id, {
        x: col * COL_WIDTH + xOffset,
        y: row * ROW_HEIGHT,
      });
    });
    col++;
  }

  // Any leftover types not in typeOrder
  for (const [entityType, group] of Object.entries(groups)) {
    if (typeOrder.includes(entityType)) continue;
    group.forEach((node, row) => {
      positions.set(node.id, { x: col * COL_WIDTH, y: row * ROW_HEIGHT });
    });
    col++;
  }

  return positions;
}

// ── Data transformation ────────────────────────────────────────────────────────

function buildFlowData(
  graphData: GraphData,
  filters: GraphFilters,
  search: string,
): { nodes: Node[]; edges: Edge[] } {
  const searchLower = search.trim().toLowerCase();
  const hasSearch = searchLower.length > 0;

  // Determine which nodes pass the entity-type filter
  const passesEntityFilter = (entityType: string) =>
    filters.entityTypes.size === 0 || filters.entityTypes.has(entityType);

  // Determine which edges pass the relationship-type filter + strength filter
  const passesEdgeFilter = (edge: GraphEdge) => {
    if (filters.relationshipTypes.size > 0 && !filters.relationshipTypes.has(edge.relationship_type)) {
      return false;
    }
    if (filters.minStrength > 1 && (edge.strength ?? 0) < filters.minStrength) {
      return false;
    }
    return true;
  };

  // Visible nodes (entity type filter)
  const visibleNodeIds = new Set(
    graphData.nodes
      .filter((n) => passesEntityFilter(n.entity_type))
      .map((n) => n.id),
  );

  // Visible edges (both endpoints visible + edge filter)
  const visibleEdges = graphData.edges.filter(
    (e) =>
      visibleNodeIds.has(e.source) &&
      visibleNodeIds.has(e.target) &&
      passesEdgeFilter(e),
  );

  // Connected node ids (only nodes that have at least one visible edge, OR all if no edges)
  // We keep all visible nodes — edges may just not be rendered.

  // Search: find matching nodes
  const matchingNodeIds = new Set<string>();
  if (hasSearch) {
    for (const node of graphData.nodes) {
      if (
        node.label.toLowerCase().includes(searchLower) ||
        (node.subtitle?.toLowerCase().includes(searchLower) ?? false)
      ) {
        matchingNodeIds.add(node.id);
      }
    }
  }

  const positions = computeLayout(graphData.nodes);

  const nodes: Node[] = graphData.nodes
    .filter((n) => visibleNodeIds.has(n.id))
    .map((n) => {
      const pos = positions.get(n.id) ?? { x: 0, y: 0 };
      const isHighlighted = hasSearch && matchingNodeIds.has(n.id);
      const isDimmed = hasSearch && !matchingNodeIds.has(n.id);
      return {
        id: n.id,
        type: "entity",
        position: pos,
        data: {
          label: n.label,
          subtitle: n.subtitle,
          entityType: n.entity_type,
          entityId: n.metadata.entity_id as string,
          highlighted: isHighlighted,
          dimmed: isDimmed,
        },
      };
    });

  const edges: Edge[] = visibleEdges.map((e) => {
    const isBidi = e.direction === "bidirectional";
    const label = RELATIONSHIP_TYPE_LABELS[e.relationship_type as RelationshipType] ?? e.label;
    return {
      id: e.id,
      source: e.source,
      target: e.target,
      type: "relationship",
      markerEnd: { type: MarkerType.ArrowClosed, width: 14, height: 14, color: "#94a3b8" },
      markerStart: isBidi
        ? { type: MarkerType.ArrowClosed, width: 14, height: 14, color: "#94a3b8" }
        : undefined,
      data: { label, strength: e.strength, dimmed: false },
      style: { stroke: "#94a3b8" },
    };
  });

  return { nodes, edges };
}

// ── Filter sidebar ─────────────────────────────────────────────────────────────

const ALL_ENTITY_TYPES = ["character", "location", "organization", "object", "world_rule"];
const ENTITY_LABELS: Record<string, string> = {
  character: "Characters",
  location: "Locations",
  organization: "Organizations",
  object: "Objects",
  world_rule: "World Rules",
};

function FilterPanel({
  graphData,
  filters,
  onChange,
}: {
  graphData: GraphData;
  filters: GraphFilters;
  onChange: (f: GraphFilters) => void;
}) {
  const [open, setOpen] = useState(false);

  // Collect unique relationship types present in this graph
  const relTypes = useMemo(
    () => [...new Set(graphData.edges.map((e) => e.relationship_type))].sort(),
    [graphData.edges],
  );

  const toggleEntityType = (type: string) => {
    const next = new Set(filters.entityTypes);
    if (next.has(type)) { next.delete(type); } else { next.add(type); }
    onChange({ ...filters, entityTypes: next });
  };

  const toggleRelType = (type: string) => {
    const next = new Set(filters.relationshipTypes);
    if (next.has(type)) { next.delete(type); } else { next.add(type); }
    onChange({ ...filters, relationshipTypes: next });
  };

  const hasActiveFilters =
    filters.entityTypes.size > 0 ||
    filters.relationshipTypes.size > 0 ||
    filters.minStrength > 1;

  return (
    <div className="absolute left-3 top-3 z-10">
      <button
        onClick={() => setOpen((o) => !o)}
        className={`flex items-center gap-1.5 rounded-lg border bg-background px-3 py-1.5 text-sm shadow-sm transition-colors hover:bg-muted ${
          hasActiveFilters ? "border-primary text-primary" : "border-border text-foreground"
        }`}
      >
        <Share2 className="h-3.5 w-3.5" />
        Filters
        {hasActiveFilters && (
          <span className="ml-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground">
            {filters.entityTypes.size + filters.relationshipTypes.size + (filters.minStrength > 1 ? 1 : 0)}
          </span>
        )}
        <ChevronDown className={`h-3 w-3 transition-transform ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <motion.div
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-1.5 w-56 rounded-xl border border-border bg-background p-3 shadow-lg"
        >
          {/* Entity types */}
          <p className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
            Entity Types
          </p>
          <div className="mb-3 space-y-1">
            {ALL_ENTITY_TYPES.map((type) => {
              const cfg = ENTITY_CONFIG[type] ?? DEFAULT_CONFIG;
              const Icon = cfg.icon;
              return (
                <label key={type} className="flex cursor-pointer items-center gap-2 rounded px-1 py-0.5 hover:bg-muted">
                  <input
                    type="checkbox"
                    checked={filters.entityTypes.has(type)}
                    onChange={() => toggleEntityType(type)}
                    className="h-3.5 w-3.5 rounded"
                  />
                  <Icon className={`h-3.5 w-3.5 ${cfg.color}`} />
                  <span className="text-xs">{ENTITY_LABELS[type]}</span>
                </label>
              );
            })}
          </div>

          {/* Relationship types */}
          {relTypes.length > 0 && (
            <>
              <p className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
                Relationship Types
              </p>
              <div className="mb-3 max-h-32 space-y-1 overflow-y-auto">
                {relTypes.map((type) => (
                  <label key={type} className="flex cursor-pointer items-center gap-2 rounded px-1 py-0.5 hover:bg-muted">
                    <input
                      type="checkbox"
                      checked={filters.relationshipTypes.has(type)}
                      onChange={() => toggleRelType(type)}
                      className="h-3.5 w-3.5 rounded"
                    />
                    <span className="text-xs capitalize">{type.replace(/_/g, " ")}</span>
                  </label>
                ))}
              </div>
            </>
          )}

          {/* Min strength */}
          <p className="mb-1 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
            Min Strength: {filters.minStrength === 1 ? "Any" : filters.minStrength}
          </p>
          <input
            type="range"
            min={1}
            max={10}
            value={filters.minStrength}
            onChange={(e) => onChange({ ...filters, minStrength: Number(e.target.value) })}
            className="w-full"
          />

          {hasActiveFilters && (
            <button
              onClick={() =>
                onChange({ entityTypes: new Set(), relationshipTypes: new Set(), minStrength: 1 })
              }
              className="mt-2 flex w-full items-center justify-center gap-1 rounded-lg bg-muted py-1 text-xs text-muted-foreground hover:text-foreground"
            >
              <X className="h-3 w-3" />
              Clear all filters
            </button>
          )}
        </motion.div>
      )}
    </div>
  );
}

// ── Statistics panel ───────────────────────────────────────────────────────────

function StatsPanel({ stats }: { stats: GraphData["statistics"] }) {
  const items = [
    { label: "Nodes", value: stats.node_count },
    { label: "Edges", value: stats.edge_count },
    { label: "Components", value: stats.connected_components },
    { label: "Avg Degree", value: stats.average_degree },
  ];
  return (
    <div className="flex items-center gap-3 rounded-xl border border-border bg-background/90 px-3 py-2 text-xs shadow-sm backdrop-blur-sm">
      {items.map((item) => (
        <div key={item.label} className="text-center">
          <p className="font-bold tabular-nums">{item.value}</p>
          <p className="text-muted-foreground">{item.label}</p>
        </div>
      ))}
    </div>
  );
}

// ── Inner graph component (needs ReactFlowProvider context) ────────────────────

function GraphCanvas({
  graphData,
  slug,
}: {
  graphData: GraphData;
  slug: string;
}) {
  const { fitView } = useReactFlow();
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState<GraphFilters>({
    entityTypes: new Set(),
    relationshipTypes: new Set(),
    minStrength: 1,
  });

  const { nodes: flowNodes, edges: flowEdges } = useMemo(
    () => buildFlowData(graphData, filters, search),
    [graphData, filters, search],
  );

  const [rfNodes, setRfNodes, onRfNodesChange] = useNodesState<Node>(flowNodes);
  const [rfEdges, setRfEdges, onRfEdgesChange] = useEdgesState<Edge>(flowEdges);

  // Sync derived data into RF state whenever graphData / filters / search changes
  useEffect(() => {
    const { nodes: n, edges: e } = buildFlowData(graphData, filters, search);
    setRfNodes(n);
    setRfEdges(e);
  }, [graphData, filters, search, setRfNodes, setRfEdges]);

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      const entityType = node.data.entityType as string;
      const entityId = node.data.entityId as string;
      const pathMap: Record<string, string> = {
        character: `characters/${entityId}`,
        location: `locations/${entityId}`,
        organization: `organizations/${entityId}`,
        object: `objects/${entityId}`,
        world_rule: `rules/${entityId}`,
      };
      const sub = pathMap[entityType];
      if (sub) {
        window.location.href = `/universe/${slug}/${sub}`;
      }
    },
    [slug],
  );

  return (
    <div className="relative h-full w-full">
      {/* Search bar */}
      <div className="absolute right-3 top-3 z-10 flex items-center gap-2">
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search nodes…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="h-8 rounded-lg border border-border bg-background/90 pl-8 pr-8 text-xs shadow-sm backdrop-blur-sm focus:outline-none focus:ring-1 focus:ring-primary"
            style={{ width: 180 }}
          />
          {search && (
            <button
              onClick={() => setSearch("")}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              <X className="h-3 w-3" />
            </button>
          )}
        </div>
        <Button size="sm" variant="outline" className="h-8 text-xs" onClick={() => fitView({ padding: 0.15, duration: 400 })}>
          Fit View
        </Button>
      </div>

      {/* Filter panel */}
      <FilterPanel graphData={graphData} filters={filters} onChange={setFilters} />

      <ReactFlow
        nodes={rfNodes}
        edges={rfEdges}
        onNodesChange={onRfNodesChange}
        onEdgesChange={onRfEdgesChange}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        fitViewOptions={{ padding: 0.15 }}
        minZoom={0.1}
        maxZoom={2}
        proOptions={{ hideAttribution: true }}
      >
        <Background gap={24} size={1} color="#e5e7eb" />
        <MiniMap
          nodeColor={(node) => {
            const type = node.data?.entityType as string | undefined;
            const colors: Record<string, string> = {
              character: "#3b82f6",
              location: "#22c55e",
              organization: "#a855f7",
              object: "#f97316",
              world_rule: "#ef4444",
            };
            return colors[type ?? ""] ?? "#94a3b8";
          }}
          maskColor="rgba(0,0,0,0.04)"
          className="rounded-xl border border-border shadow-sm"
        />
        <Controls className="rounded-xl border border-border shadow-sm" />

        {/* Statistics panel */}
        <Panel position="bottom-center">
          <StatsPanel stats={graphData.statistics} />
        </Panel>
      </ReactFlow>
    </div>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────────

interface PageProps {
  params: Promise<{ slug: string }>;
}

export default function GraphPage({ params }: PageProps) {
  const { slug } = use(params);

  const { data: universe, isLoading: uLoading } = useUniverseBySlug(slug);
  const uid = universe?.id ?? "";

  const { data: graphData, isLoading: gLoading, error } = useGraph(uid);

  if (uLoading || gLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          <p className="text-sm text-muted-foreground">Building knowledge graph…</p>
        </div>
      </div>
    );
  }

  if (!universe) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 text-center">
        <AlertCircle className="h-10 w-10 text-destructive" />
        <h1 className="text-2xl font-bold">Universe not found</h1>
        <Button asChild>
          <Link href="/">Go Home</Link>
        </Button>
      </div>
    );
  }

  if (error || !graphData) {
    return (
      <EntityPageShell
        breadcrumbs={[
          { label: universe.name, href: `/universe/${slug}/world` },
          { label: "Knowledge Graph" },
        ]}
      >
        <div className="flex flex-col items-center gap-3 py-20 text-center">
          <AlertCircle className="h-10 w-10 text-destructive" />
          <p className="font-medium">Failed to load graph data.</p>
          <p className="text-sm text-muted-foreground">Check that the backend is running.</p>
        </div>
      </EntityPageShell>
    );
  }

  // Empty state
  if (graphData.nodes.length === 0) {
    return (
      <EntityPageShell
        breadcrumbs={[
          { label: universe.name, href: `/universe/${slug}/world` },
          { label: "Knowledge Graph" },
        ]}
      >
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col items-center gap-4 py-24 text-center"
        >
          <div className="flex h-16 w-16 items-center justify-center rounded-full border border-border bg-muted">
            <GitFork className="h-7 w-7 text-muted-foreground" />
          </div>
          <h2 className="text-xl font-bold">No entities yet</h2>
          <p className="max-w-sm text-sm text-muted-foreground">
            Create characters, locations, organizations, objects, and world rules to start
            exploring your universe as a knowledge graph.
          </p>
          <Button asChild>
            <Link href={`/universe/${slug}/world`}>Go to World Building</Link>
          </Button>
        </motion.div>
      </EntityPageShell>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Minimal header */}
      <header className="sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur-sm">
        <div className="mx-auto flex h-14 max-w-full items-center gap-2 px-6">
          <Link
            href={`/universe/${slug}/world`}
            className="flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            ← {universe.name}
          </Link>
          <span className="text-muted-foreground">/</span>
          <span className="text-sm font-medium">Knowledge Graph</span>
          <div className="ml-auto flex items-center gap-3 text-xs text-muted-foreground">
            <span>{graphData.statistics.node_count} nodes</span>
            <span>·</span>
            <span>{graphData.statistics.edge_count} edges</span>
          </div>
        </div>
      </header>

      {/* Full-screen graph canvas — ReactFlowProvider supplies the RF context that
          GraphCanvas needs for useReactFlow() / fitView() */}
      <div style={{ height: "calc(100vh - 56px)", width: "100%" }}>
        <ReactFlowProvider>
          <GraphCanvas graphData={graphData} slug={slug} />
        </ReactFlowProvider>
      </div>
    </div>
  );
}
