/**
 * TanStack Query hook for the Knowledge Graph.
 */
"use client";

import { useQuery } from "@tanstack/react-query";
import { graphService } from "@/services/graph.service";

export const graphKeys = {
  graph: (universeId: string) => ["graph", universeId] as const,
};

export function useGraph(universeId: string) {
  return useQuery({
    queryKey: graphKeys.graph(universeId),
    queryFn: () => graphService.getGraph(universeId),
    enabled: !!universeId,
    staleTime: 30_000,
  });
}
