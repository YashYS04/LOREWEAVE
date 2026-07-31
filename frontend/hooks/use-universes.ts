/**
 * TanStack Query hooks for the Universe resource.
 */
"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { universeService } from "@/services/universe.service";
import type { UniverseCreatePayload, UniverseUpdatePayload } from "@/types/universe";

export const universeKeys = {
  all: ["universes"] as const,
  lists: () => [...universeKeys.all, "list"] as const,
  detail: (id: string) => [...universeKeys.all, "detail", id] as const,
  slug: (slug: string) => [...universeKeys.all, "slug", slug] as const,
};

export function useUniverses(skip = 0, limit = 50) {
  return useQuery({
    queryKey: universeKeys.lists(),
    queryFn: () => universeService.list(skip, limit),
  });
}

export function useUniverse(id: string) {
  return useQuery({
    queryKey: universeKeys.detail(id),
    queryFn: () => universeService.getById(id),
    enabled: !!id,
  });
}

export function useUniverseBySlug(slug: string) {
  return useQuery({
    queryKey: universeKeys.slug(slug),
    queryFn: async () => {
      const data = await universeService.list(0, 100);
      const found = data.items.find((u) => u.slug === slug);
      if (!found) throw new Error("Universe not found");
      return found;
    },
    enabled: !!slug,
  });
}

export function useCreateUniverse() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: UniverseCreatePayload) => universeService.create(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: universeKeys.lists() });
    },
  });
}

export function useUpdateUniverse(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: UniverseUpdatePayload) => universeService.update(id, payload),
    onSuccess: (updated) => {
      qc.invalidateQueries({ queryKey: universeKeys.lists() });
      qc.setQueryData(universeKeys.detail(id), updated);
    },
  });
}

export function useDeleteUniverse() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => universeService.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: universeKeys.lists() });
    },
  });
}
