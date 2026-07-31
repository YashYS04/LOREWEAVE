/**
 * TanStack Query hooks for the WorldObject resource.
 */
"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { worldObjectService } from "@/services/world-object.service";
import type { WorldObjectCreatePayload, WorldObjectUpdatePayload } from "@/types/world-object";

export const worldObjectKeys = {
  all: ["world-objects"] as const,
  lists: (universeId: string) => [...worldObjectKeys.all, "list", universeId] as const,
  detail: (id: string) => [...worldObjectKeys.all, "detail", id] as const,
};

export function useWorldObjects(universeId: string, skip = 0, limit = 50) {
  return useQuery({
    queryKey: worldObjectKeys.lists(universeId),
    queryFn: () => worldObjectService.list(universeId, skip, limit),
    enabled: !!universeId,
  });
}

export function useWorldObject(id: string) {
  return useQuery({
    queryKey: worldObjectKeys.detail(id),
    queryFn: () => worldObjectService.getById(id),
    enabled: !!id,
  });
}

export function useCreateWorldObject(universeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: WorldObjectCreatePayload) => worldObjectService.create(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: worldObjectKeys.lists(universeId) }),
  });
}

export function useUpdateWorldObject(id: string, universeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: WorldObjectUpdatePayload) => worldObjectService.update(id, payload),
    onSuccess: (updated) => {
      qc.invalidateQueries({ queryKey: worldObjectKeys.lists(universeId) });
      qc.setQueryData(worldObjectKeys.detail(id), updated);
    },
  });
}

export function useDeleteWorldObject(universeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => worldObjectService.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: worldObjectKeys.lists(universeId) }),
  });
}
