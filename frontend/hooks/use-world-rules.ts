/**
 * TanStack Query hooks for the WorldRule resource.
 */
"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { worldRuleService } from "@/services/world-rule.service";
import type { WorldRuleCreatePayload, WorldRuleUpdatePayload } from "@/types/world-rule";

export const worldRuleKeys = {
  all: ["world-rules"] as const,
  lists: (universeId: string) => [...worldRuleKeys.all, "list", universeId] as const,
  detail: (id: string) => [...worldRuleKeys.all, "detail", id] as const,
};

export function useWorldRules(universeId: string, skip = 0, limit = 50) {
  return useQuery({
    queryKey: worldRuleKeys.lists(universeId),
    queryFn: () => worldRuleService.list(universeId, skip, limit),
    enabled: !!universeId,
  });
}

export function useWorldRule(id: string) {
  return useQuery({
    queryKey: worldRuleKeys.detail(id),
    queryFn: () => worldRuleService.getById(id),
    enabled: !!id,
  });
}

export function useCreateWorldRule(universeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: WorldRuleCreatePayload) => worldRuleService.create(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: worldRuleKeys.lists(universeId) }),
  });
}

export function useUpdateWorldRule(id: string, universeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: WorldRuleUpdatePayload) => worldRuleService.update(id, payload),
    onSuccess: (updated) => {
      qc.invalidateQueries({ queryKey: worldRuleKeys.lists(universeId) });
      qc.setQueryData(worldRuleKeys.detail(id), updated);
    },
  });
}

export function useDeleteWorldRule(universeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => worldRuleService.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: worldRuleKeys.lists(universeId) }),
  });
}
