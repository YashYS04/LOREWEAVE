/**
 * TanStack Query hooks for the Organization resource.
 */
"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { organizationService } from "@/services/organization.service";
import type { OrganizationCreatePayload, OrganizationUpdatePayload } from "@/types/organization";

export const organizationKeys = {
  all: ["organizations"] as const,
  lists: (universeId: string) => [...organizationKeys.all, "list", universeId] as const,
  detail: (id: string) => [...organizationKeys.all, "detail", id] as const,
};

export function useOrganizations(universeId: string, skip = 0, limit = 50) {
  return useQuery({
    queryKey: organizationKeys.lists(universeId),
    queryFn: () => organizationService.list(universeId, skip, limit),
    enabled: !!universeId,
  });
}

export function useOrganization(id: string) {
  return useQuery({
    queryKey: organizationKeys.detail(id),
    queryFn: () => organizationService.getById(id),
    enabled: !!id,
  });
}

export function useCreateOrganization(universeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: OrganizationCreatePayload) => organizationService.create(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: organizationKeys.lists(universeId) }),
  });
}

export function useUpdateOrganization(id: string, universeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: OrganizationUpdatePayload) => organizationService.update(id, payload),
    onSuccess: (updated) => {
      qc.invalidateQueries({ queryKey: organizationKeys.lists(universeId) });
      qc.setQueryData(organizationKeys.detail(id), updated);
    },
  });
}

export function useDeleteOrganization(universeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => organizationService.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: organizationKeys.lists(universeId) }),
  });
}
