/**
 * TanStack Query hooks for the Timeline module.
 */
"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { timelineService, type ListTimelineEventsParams } from "@/services/timeline.service";
import type { CreateTimelineEventRequest, UpdateTimelineEventRequest } from "@/types/timeline";

// ── Query keys ──────────────────────────────────────────────────────────────

export const timelineKeys = {
  list: (params: ListTimelineEventsParams) => ["timeline", "list", params] as const,
  detail: (id: string) => ["timeline", "detail", id] as const,
  byUniverse: (universeId: string) => ["timeline", "universe", universeId] as const,
};

// ── Queries ─────────────────────────────────────────────────────────────────

export function useTimelineEvents(params: ListTimelineEventsParams) {
  return useQuery({
    queryKey: timelineKeys.list(params),
    queryFn: () => timelineService.list(params),
    enabled: !!params.universe_id,
    staleTime: 15_000,
  });
}

export function useTimelineEvent(id: string) {
  return useQuery({
    queryKey: timelineKeys.detail(id),
    queryFn: () => timelineService.getById(id),
    enabled: !!id,
    staleTime: 30_000,
  });
}

// ── Mutations ────────────────────────────────────────────────────────────────

export function useCreateTimelineEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateTimelineEventRequest) => timelineService.create(payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["timeline"] });
    },
  });
}

export function useUpdateTimelineEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: UpdateTimelineEventRequest }) =>
      timelineService.update(id, payload),
    onSuccess: (updated) => {
      qc.setQueryData(timelineKeys.detail(updated.id), updated);
      void qc.invalidateQueries({ queryKey: ["timeline"] });
    },
  });
}

export function useDeleteTimelineEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => timelineService.delete(id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["timeline"] });
    },
  });
}
