/**
 * AI API service — context building and provider health.
 */
import { apiClient } from "@/lib/api-client";
import type { ContextRequest, ProviderHealth, UniverseContext } from "@/types/ai";

const BASE = "/api/v1/ai";

interface Envelope<T> {
  success: boolean;
  message: string;
  data: T;
}

const unwrap = <T>(e: Envelope<T>): T => e.data;

export const aiService = {
  /** Build and retrieve the full AI-ready universe context. */
  getContext: (payload: ContextRequest): Promise<UniverseContext> =>
    apiClient.post<Envelope<UniverseContext>>(`${BASE}/context`, payload).then(unwrap),

  /** Check whether the AI provider (Ollama) is reachable. */
  checkHealth: (): Promise<ProviderHealth> =>
    apiClient.get<Envelope<ProviderHealth>>(`${BASE}/health`).then(unwrap),
};
