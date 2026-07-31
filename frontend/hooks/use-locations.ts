/**
 * TanStack Query hooks for the Location resource.
 */
"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { locationService } from "@/services/location.service";
import type { LocationCreatePayload, LocationUpdatePayload } from "@/types/location";

export const locationKeys = {
  all: ["locations"] as const,
  lists: (universeId: string) => [...locationKeys.all, "list", universeId] as const,
  detail: (id: string) => [...locationKeys.all, "detail", id] as const,
};

export function useLocations(universeId: string, skip = 0, limit = 50) {
  return useQuery({
    queryKey: locationKeys.lists(universeId),
    queryFn: () => locationService.list(universeId, skip, limit),
    enabled: !!universeId,
  });
}

export function useLocation(id: string) {
  return useQuery({
    queryKey: locationKeys.detail(id),
    queryFn: () => locationService.getById(id),
    enabled: !!id,
  });
}

export function useCreateLocation(universeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: LocationCreatePayload) => locationService.create(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: locationKeys.lists(universeId) }),
  });
}

export function useUpdateLocation(id: string, universeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: LocationUpdatePayload) => locationService.update(id, payload),
    onSuccess: (updated) => {
      qc.invalidateQueries({ queryKey: locationKeys.lists(universeId) });
      qc.setQueryData(locationKeys.detail(id), updated);
    },
  });
}

export function useDeleteLocation(universeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => locationService.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: locationKeys.lists(universeId) }),
  });
}
