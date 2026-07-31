/**
 * Universe API service — all backend calls for the Universe resource.
 *
 * The backend wraps all responses in {"success": true, "data": {...}}.
 * These helpers unwrap the envelope so callers receive domain objects directly.
 */
import { apiClient } from "@/lib/api-client";
import type {
  Universe,
  UniverseCreatePayload,
  UniverseListResponse,
  UniverseUpdatePayload,
} from "@/types/universe";

const BASE = "/api/v1/universes";

interface ApiEnvelope<T> {
  success: boolean;
  message: string;
  data: T;
}

function unwrap<T>(envelope: ApiEnvelope<T>): T {
  return envelope.data;
}

export const universeService = {
  list: (skip = 0, limit = 50): Promise<UniverseListResponse> =>
    apiClient
      .get<ApiEnvelope<UniverseListResponse>>(`${BASE}?skip=${skip}&limit=${limit}`)
      .then(unwrap),

  getById: (id: string): Promise<Universe> =>
    apiClient.get<ApiEnvelope<Universe>>(`${BASE}/${id}`).then(unwrap),

  create: (payload: UniverseCreatePayload): Promise<Universe> =>
    apiClient.post<ApiEnvelope<Universe>>(BASE, payload).then(unwrap),

  update: (id: string, payload: UniverseUpdatePayload): Promise<Universe> =>
    apiClient.patch<ApiEnvelope<Universe>>(`${BASE}/${id}`, payload).then(unwrap),

  delete: (id: string): Promise<void> =>
    apiClient.delete<ApiEnvelope<void>>(`${BASE}/${id}`).then(() => undefined),
};
