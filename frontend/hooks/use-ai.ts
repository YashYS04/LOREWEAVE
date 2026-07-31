/**
 * TanStack Query hooks for the AI module.
 */
"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { aiService } from "@/services/ai.service";

export const aiKeys = {
  health: ["ai", "health"] as const,
  context: (universeId: string) => ["ai", "context", universeId] as const,
};

/** Probe the AI provider health. Runs once on mount, refetches on demand. */
export function useAIHealth() {
  return useQuery({
    queryKey: aiKeys.health,
    queryFn: () => aiService.checkHealth(),
    retry: false,
    staleTime: 30_000,
  });
}

/** Build the universe context on demand (mutation so it can be triggered by a button). */
export function useGenerateContext(universeId: string) {
  return useMutation({
    mutationKey: aiKeys.context(universeId),
    mutationFn: () => aiService.getContext({ universe_id: universeId }),
  });
}
