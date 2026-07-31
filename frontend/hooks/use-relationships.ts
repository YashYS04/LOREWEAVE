/**
 * TanStack Query hooks for the Relationship module.
 */
"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { relationshipService, type ListRelationshipsParams } from "@/services/relationship.service";
import type { CreateRelationshipRequest, UpdateRelationshipRequest } from "@/types/relationship";

// ── Query keys ──────────────────────────────────────────────────────────────────

export const relationshipKeys = {
  list: (params: ListRelationshipsParams) => ["relationships", "list", params] as const,
  detail: (id: string) => ["relationships", "detail", id] as const,
  byUniverse: (universeId: string) => ["relationships", "universe", universeId] as const,
  byEntity: (universeId: string, entityId: string) =>
    ["relationships", "entity", universeId, entityId] as const,
};

// ── Queries ────────────────────────────────────────────────────────────────────

export function useRelationships(params: ListRelationshipsParams) {
  return useQuery({
    queryKey: relationshipKeys.list(params),
    queryFn: () => relationshipService.list(params),
    enabled: !!params.universe_id,
    staleTime: 15_000,
  });
}

export function useRelationship(id: string) {
  return useQuery({
    queryKey: relationshipKeys.detail(id),
    queryFn: () => relationshipService.getById(id),
    enabled: !!id,
    staleTime: 30_000,
  });
}

/** Fetch relationships where a specific entity is source or target. */
export function useEntityRelationships(universeId: string, entityId: string, entityType: string) {
  return useQuery({
    queryKey: relationshipKeys.byEntity(universeId, entityId),
    queryFn: () =>
      relationshipService.list({
        universe_id: universeId,
        entity_id: entityId,
        entity_type: entityType,
        limit: 100,
      }),
    enabled: !!universeId && !!entityId,
    staleTime: 15_000,
  });
}

// ── Mutations ──────────────────────────────────────────────────────────────────

export function useCreateRelationship(universeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateRelationshipRequest) => relationshipService.create(payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["relationships"] });
    },
  });
}

export function useUpdateRelationship(universeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: UpdateRelationshipRequest }) =>
      relationshipService.update(id, payload),
    onSuccess: (updated) => {
      qc.setQueryData(relationshipKeys.detail(updated.id), updated);
      void qc.invalidateQueries({ queryKey: ["relationships"] });
    },
  });
}

export function useDeleteRelationship(universeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => relationshipService.delete(id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["relationships"] });
    },
  });
}
