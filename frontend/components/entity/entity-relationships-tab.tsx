"use client";

/**
 * EntityRelationshipsTab — reusable Relationships tab for any entity detail page.
 *
 * Shows incoming + outgoing relationships for the given entity, with delete support.
 * Used by Characters, Locations, Organizations, Objects, and World Rules detail pages.
 */

import Link from "next/link";
import { ArrowLeft, ArrowLeftRight, ArrowRight, Loader2, Plus, Share2, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useEntityRelationships, useDeleteRelationship } from "@/hooks/use-relationships";
import {
  RELATIONSHIP_TYPE_LABELS,
  ENTITY_TYPE_LABELS,
  type RelationshipType,
  type EntityType,
} from "@/types/relationship";

interface Props {
  /** Universe this entity belongs to */
  universeId: string;
  /** The entity's own ID */
  entityId: string;
  /** The entity type string (character, location, etc.) */
  entityType: string;
  /** Display name of the entity (used in outgoing labels) */
  entityName: string;
  /** Slug for deep-linking back to relationship management */
  slug: string;
}

export function EntityRelationshipsTab({
  universeId,
  entityId,
  entityType,
  entityName,
  slug,
}: Props) {
  const deleteRel = useDeleteRelationship(universeId);
  const { data: relData, isLoading: relsLoading } = useEntityRelationships(
    universeId,
    entityId,
    entityType,
  );

  const rels = relData?.items ?? [];
  const outgoingRels = rels.filter((r) => r.source_entity_id === entityId);
  const incomingRels = rels.filter((r) => r.target_entity_id === entityId);

  if (relsLoading) {
    return (
      <div className="flex justify-center py-10">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (rels.length === 0) {
    return (
      <div className="flex flex-col items-center gap-3 py-12 text-center">
        <Share2 className="h-10 w-10 text-muted-foreground/40" />
        <p className="font-medium text-foreground">No relationships yet</p>
        <p className="text-sm text-muted-foreground">
          Create a relationship from the Relationship Explorer to connect this entity to others.
        </p>
        <Button size="sm" asChild variant="outline">
          <Link href={`/universe/${slug}/relationships`}>
            <Plus className="mr-1.5 h-3.5 w-3.5" />
            Manage Relationships
          </Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 py-2">
      {outgoingRels.length > 0 && (
        <div>
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Outgoing ({outgoingRels.length})
          </h3>
          <div className="space-y-2">
            {outgoingRels.map((r) => {
              const label =
                RELATIONSHIP_TYPE_LABELS[r.relationship_type as RelationshipType] ??
                r.relationship_type;
              const isBidi = r.direction === "bidirectional";
              const targetTypeLabel =
                ENTITY_TYPE_LABELS[r.target_entity_type as EntityType] ?? r.target_entity_type;
              return (
                <div
                  key={r.id}
                  className="flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 text-sm"
                >
                  <span className="font-medium">{entityName}</span>
                  <span className="shrink-0 rounded-full border border-border bg-muted px-2 py-0.5 text-[10px] font-semibold text-muted-foreground">
                    {isBidi ? (
                      <ArrowLeftRight className="inline h-3 w-3" />
                    ) : (
                      <ArrowRight className="inline h-3 w-3" />
                    )}{" "}
                    {label}
                  </span>
                  <span className="min-w-0 flex-1 truncate text-muted-foreground">
                    {targetTypeLabel}: {r.target_entity_id}
                  </span>
                  <button
                    className="ml-1 shrink-0 rounded p-0.5 text-muted-foreground hover:text-destructive"
                    onClick={() => deleteRel.mutate(r.id)}
                    aria-label="Delete relationship"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {incomingRels.length > 0 && (
        <div>
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Incoming ({incomingRels.length})
          </h3>
          <div className="space-y-2">
            {incomingRels.map((r) => {
              const label =
                RELATIONSHIP_TYPE_LABELS[r.relationship_type as RelationshipType] ??
                r.relationship_type;
              const sourceTypeLabel =
                ENTITY_TYPE_LABELS[r.source_entity_type as EntityType] ?? r.source_entity_type;
              return (
                <div
                  key={r.id}
                  className="flex items-center gap-2 rounded-lg border border-border bg-muted/30 px-3 py-2 text-sm"
                >
                  <span className="min-w-0 flex-1 truncate text-muted-foreground">
                    {sourceTypeLabel}: {r.source_entity_id}
                  </span>
                  <span className="shrink-0 rounded-full border border-border bg-muted px-2 py-0.5 text-[10px] font-semibold text-muted-foreground">
                    <ArrowLeft className="inline h-3 w-3" /> {label}
                  </span>
                  <span className="font-medium">{entityName}</span>
                  <button
                    className="ml-1 shrink-0 rounded p-0.5 text-muted-foreground hover:text-destructive"
                    onClick={() => deleteRel.mutate(r.id)}
                    aria-label="Delete relationship"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="pt-2">
        <Button size="sm" variant="outline" asChild>
          <Link href={`/universe/${slug}/relationships`}>
            <Share2 className="mr-1.5 h-3.5 w-3.5" />
            Manage All Relationships
          </Link>
        </Button>
      </div>
    </div>
  );
}
