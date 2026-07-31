"use client";

/**
 * Relationship Explorer — list, search, filter, and manage all relationships in a universe.
 */

import { use, useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  AlertCircle,
  ArrowLeft,
  ArrowRight,
  ArrowLeftRight,
  ChevronDown,
  Loader2,
  Plus,
  Search,
  Share2,
  Trash2,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { EntityPageShell } from "@/components/entity";
import { useUniverseBySlug } from "@/hooks/use-universes";
import {
  useRelationships,
  useCreateRelationship,
  useDeleteRelationship,
} from "@/hooks/use-relationships";
import type {
  EntityType,
  RelationshipType,
  CreateRelationshipRequest,
} from "@/types/relationship";
import {
  RELATIONSHIP_TYPE_LABELS,
  ENTITY_TYPE_LABELS,
} from "@/types/relationship";
import { CreateRelationshipDialog } from "./_components/create-relationship-dialog";

interface PageProps {
  params: Promise<{ slug: string }>;
}

// ── Relationship card ──────────────────────────────────────────────────────────

function RelationshipCard({
  rel,
  onDelete,
  index,
}: {
  rel: {
    id: string;
    source_entity_type: string;
    source_entity_id: string;
    target_entity_type: string;
    target_entity_id: string;
    relationship_type: string;
    title: string | null;
    description: string | null;
    strength: number | null;
    direction: string;
  };
  onDelete: (id: string) => void;
  index: number;
}) {
  const [showDelete, setShowDelete] = useState(false);
  const label =
    RELATIONSHIP_TYPE_LABELS[rel.relationship_type as RelationshipType] ??
    rel.relationship_type.replace(/_/g, " ");
  const isBidi = rel.direction === "bidirectional";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04, duration: 0.25 }}
      className="rounded-xl border border-border bg-card p-5"
    >
      {/* Visual preview */}
      <div className="mb-4 flex items-center gap-2 text-sm">
        {/* Source */}
        <div className="flex min-w-0 flex-1 flex-col rounded-lg border border-border bg-muted/40 px-3 py-2">
          <span className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
            {ENTITY_TYPE_LABELS[rel.source_entity_type as EntityType] ?? rel.source_entity_type}
          </span>
          <span className="truncate font-medium">{rel.source_entity_id}</span>
        </div>

        {/* Arrow + type badge */}
        <div className="flex shrink-0 flex-col items-center gap-0.5">
          {isBidi ? (
            <ArrowLeftRight className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ArrowRight className="h-4 w-4 text-primary" />
          )}
          <span className="rounded-full border border-border bg-muted px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
            {label}
          </span>
        </div>

        {/* Target */}
        <div className="flex min-w-0 flex-1 flex-col rounded-lg border border-border bg-muted/40 px-3 py-2">
          <span className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
            {ENTITY_TYPE_LABELS[rel.target_entity_type as EntityType] ?? rel.target_entity_type}
          </span>
          <span className="truncate font-medium">{rel.target_entity_id}</span>
        </div>
      </div>

      {/* Meta row */}
      <div className="flex items-center justify-between">
        <div className="space-y-0.5">
          {rel.title && (
            <p className="text-sm font-medium">{rel.title}</p>
          )}
          {rel.description && (
            <p className="line-clamp-2 text-xs text-muted-foreground">{rel.description}</p>
          )}
          {rel.strength !== null && (
            <div className="flex items-center gap-1.5 pt-1">
              <span className="text-xs text-muted-foreground">Strength:</span>
              <div className="flex gap-0.5">
                {Array.from({ length: 10 }).map((_, i) => (
                  <div
                    key={i}
                    className={`h-1.5 w-2 rounded-sm ${
                      i < (rel.strength ?? 0) ? "bg-primary" : "bg-muted"
                    }`}
                  />
                ))}
              </div>
              <span className="text-xs font-medium tabular-nums">{rel.strength}/10</span>
            </div>
          )}
        </div>

        <button
          className="ml-3 shrink-0 rounded p-1.5 text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive"
          onClick={() => setShowDelete(true)}
          title="Delete relationship"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>

      {/* Delete confirm */}
      <AnimatePresence>
        {showDelete && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-3 overflow-hidden"
          >
            <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-3">
              <p className="mb-2 text-xs text-destructive">
                Delete this relationship? This cannot be undone.
              </p>
              <div className="flex gap-2">
                <Button
                  variant="destructive"
                  size="sm"
                  className="h-7 text-xs"
                  onClick={() => onDelete(rel.id)}
                >
                  Delete
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 text-xs"
                  onClick={() => setShowDelete(false)}
                >
                  Cancel
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// ── Filter controls ────────────────────────────────────────────────────────────

const REL_TYPES = Object.entries(RELATIONSHIP_TYPE_LABELS) as [RelationshipType, string][];
const ENTITY_TYPES = Object.entries(ENTITY_TYPE_LABELS) as [EntityType, string][];

function FilterSelect({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: [string, string][];
}) {
  return (
    <div className="relative">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="appearance-none rounded-lg border border-border bg-background py-1.5 pl-3 pr-7 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
      >
        <option value="">{label}</option>
        {options.map(([v, l]) => (
          <option key={v} value={v}>{l}</option>
        ))}
      </select>
      <ChevronDown className="pointer-events-none absolute right-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
    </div>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────────

export default function RelationshipsPage({ params }: PageProps) {
  const { slug } = use(params);

  const { data: universe, isLoading: uLoading } = useUniverseBySlug(slug);
  const uid = universe?.id ?? "";

  const [search, setSearch] = useState("");
  const [filterType, setFilterType] = useState("");
  const [filterEntityType, setFilterEntityType] = useState("");
  const [skip, setSkip] = useState(0);
  const [showCreate, setShowCreate] = useState(false);
  const LIMIT = 20;

  const { data: relData, isLoading: relsLoading } = useRelationships({
    universe_id: uid,
    skip,
    limit: LIMIT,
    relationship_type: filterType || undefined,
    entity_type: filterEntityType || undefined,
    search: search.trim() || undefined,
  });

  const createRel = useCreateRelationship(uid);
  const deleteRel = useDeleteRelationship(uid);

  const rels = relData?.items ?? [];
  const total = relData?.total ?? 0;
  const totalPages = Math.ceil(total / LIMIT);
  const currentPage = Math.floor(skip / LIMIT) + 1;

  if (uLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
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

  const handleCreate = async (payload: CreateRelationshipRequest) => {
    await createRel.mutateAsync(payload);
    setShowCreate(false);
  };

  return (
    <EntityPageShell
      breadcrumbs={[
        { label: universe.name, href: `/universe/${slug}/world` },
        { label: "Relationships" },
      ]}
    >
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8 flex items-start justify-between"
      >
        <div>
          <div className="flex items-center gap-2">
            <Share2 className="h-6 w-6 text-primary" />
            <h1 className="text-3xl font-extrabold tracking-tight">Relationships</h1>
          </div>
          <p className="mt-1 text-muted-foreground">
            {total} relationship{total !== 1 ? "s" : ""} in{" "}
            <span className="font-medium text-foreground">{universe.name}</span>
          </p>
        </div>
        <Button size="sm" onClick={() => setShowCreate(true)}>
          <Plus className="mr-1.5 h-4 w-4" />
          New Relationship
        </Button>
      </motion.div>

      {/* Search + Filters */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="mb-6 flex flex-wrap items-center gap-3"
      >
        <div className="relative flex-1 min-w-52">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search title or description…"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setSkip(0); }}
            className="w-full rounded-lg border border-border bg-background py-2 pl-9 pr-4 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
          {search && (
            <button
              onClick={() => setSearch("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>

        <FilterSelect
          label="All Types"
          value={filterType}
          onChange={(v) => { setFilterType(v); setSkip(0); }}
          options={REL_TYPES}
        />

        <FilterSelect
          label="All Entity Types"
          value={filterEntityType}
          onChange={(v) => { setFilterEntityType(v); setSkip(0); }}
          options={ENTITY_TYPES}
        />

        {(filterType || filterEntityType || search) && (
          <Button
            variant="ghost"
            size="sm"
            className="h-8 text-xs"
            onClick={() => { setSearch(""); setFilterType(""); setFilterEntityType(""); setSkip(0); }}
          >
            <X className="mr-1 h-3 w-3" />
            Clear
          </Button>
        )}
      </motion.div>

      {/* Content */}
      {relsLoading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : rels.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-20 text-center"
        >
          <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-muted">
            <Share2 className="h-7 w-7 text-muted-foreground" />
          </div>
          <p className="mb-1 font-medium">
            {search || filterType || filterEntityType
              ? "No relationships match your filters"
              : "No relationships yet"}
          </p>
          <p className="mb-6 max-w-xs text-sm text-muted-foreground">
            Connect characters, locations, organizations, objects and world rules.
          </p>
          <Button size="sm" onClick={() => setShowCreate(true)}>
            <Plus className="mr-1.5 h-4 w-4" />
            Create First Relationship
          </Button>
        </motion.div>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-2">
            {rels.map((rel, i) => (
              <RelationshipCard
                key={rel.id}
                rel={rel}
                index={i}
                onDelete={(id) => deleteRel.mutate(id)}
              />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-8 flex items-center justify-center gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={currentPage === 1}
                onClick={() => setSkip(skip - LIMIT)}
              >
                <ArrowLeft className="mr-1.5 h-3.5 w-3.5" />
                Previous
              </Button>
              <span className="text-sm text-muted-foreground">
                Page {currentPage} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={currentPage === totalPages}
                onClick={() => setSkip(skip + LIMIT)}
              >
                Next
                <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
              </Button>
            </div>
          )}
        </>
      )}

      {/* Create dialog */}
      <AnimatePresence>
        {showCreate && (
          <CreateRelationshipDialog
            universeId={uid}
            onSubmit={handleCreate}
            onClose={() => setShowCreate(false)}
            isPending={createRel.isPending}
            error={createRel.error?.message}
          />
        )}
      </AnimatePresence>
    </EntityPageShell>
  );
}
