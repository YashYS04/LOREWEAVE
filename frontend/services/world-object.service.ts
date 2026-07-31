/**
 * WorldObject API service.
 */
import { apiClient } from "@/lib/api-client";
import type {
  WorldObject,
  WorldObjectCreatePayload,
  WorldObjectListResponse,
  WorldObjectUpdatePayload,
} from "@/types/world-object";

const BASE = "/api/v1/objects";

interface Envelope<T> {
  success: boolean;
  message: string;
  data: T;
}

const unwrap = <T>(e: Envelope<T>): T => e.data;

export const worldObjectService = {
  list: (universeId: string, skip = 0, limit = 50): Promise<WorldObjectListResponse> =>
    apiClient
      .get<Envelope<WorldObjectListResponse>>(`${BASE}?universe_id=${universeId}&skip=${skip}&limit=${limit}`)
      .then(unwrap),

  getById: (id: string): Promise<WorldObject> =>
    apiClient.get<Envelope<WorldObject>>(`${BASE}/${id}`).then(unwrap),

  create: (payload: WorldObjectCreatePayload): Promise<WorldObject> =>
    apiClient.post<Envelope<WorldObject>>(BASE, payload).then(unwrap),

  update: (id: string, payload: WorldObjectUpdatePayload): Promise<WorldObject> =>
    apiClient.patch<Envelope<WorldObject>>(`${BASE}/${id}`, payload).then(unwrap),

  delete: (id: string): Promise<void> =>
    apiClient.delete<Envelope<void>>(`${BASE}/${id}`).then(() => undefined),
};
