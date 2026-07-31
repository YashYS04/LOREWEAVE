/**
 * Location API service.
 */
import { apiClient } from "@/lib/api-client";
import type {
  Location,
  LocationCreatePayload,
  LocationListResponse,
  LocationUpdatePayload,
} from "@/types/location";

const BASE = "/api/v1/locations";

interface Envelope<T> {
  success: boolean;
  message: string;
  data: T;
}

const unwrap = <T>(e: Envelope<T>): T => e.data;

export const locationService = {
  list: (universeId: string, skip = 0, limit = 50): Promise<LocationListResponse> =>
    apiClient
      .get<Envelope<LocationListResponse>>(
        `${BASE}?universe_id=${universeId}&skip=${skip}&limit=${limit}`
      )
      .then(unwrap),

  getById: (id: string): Promise<Location> =>
    apiClient.get<Envelope<Location>>(`${BASE}/${id}`).then(unwrap),

  create: (payload: LocationCreatePayload): Promise<Location> =>
    apiClient.post<Envelope<Location>>(BASE, payload).then(unwrap),

  update: (id: string, payload: LocationUpdatePayload): Promise<Location> =>
    apiClient.patch<Envelope<Location>>(`${BASE}/${id}`, payload).then(unwrap),

  delete: (id: string): Promise<void> =>
    apiClient.delete<Envelope<void>>(`${BASE}/${id}`).then(() => undefined),
};
