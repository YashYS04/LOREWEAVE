/**
 * Graph API service — fetches the knowledge graph for a universe.
 */
import { apiClient } from "@/lib/api-client";
import type { GraphData } from "@/types/graph";

const BASE = "/api/v1/graph";

interface Envelope<T> {
  success: boolean;
  message: string;
  data: T;
}

const unwrap = <T>(e: Envelope<T>): T => e.data;

export const graphService = {
  /** Fetch the full knowledge graph (nodes, edges, statistics) for a universe. */
  getGraph: (universeId: string): Promise<GraphData> =>
    apiClient.get<Envelope<GraphData>>(`${BASE}/${universeId}`).then(unwrap),
};
