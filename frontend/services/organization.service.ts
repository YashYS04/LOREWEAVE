/**
 * Organization API service.
 */
import { apiClient } from "@/lib/api-client";
import type {
  Organization,
  OrganizationCreatePayload,
  OrganizationListResponse,
  OrganizationUpdatePayload,
} from "@/types/organization";

const BASE = "/api/v1/organizations";

interface Envelope<T> {
  success: boolean;
  message: string;
  data: T;
}

const unwrap = <T>(e: Envelope<T>): T => e.data;

export const organizationService = {
  list: (universeId: string, skip = 0, limit = 50): Promise<OrganizationListResponse> =>
    apiClient
      .get<Envelope<OrganizationListResponse>>(`${BASE}?universe_id=${universeId}&skip=${skip}&limit=${limit}`)
      .then(unwrap),

  getById: (id: string): Promise<Organization> =>
    apiClient.get<Envelope<Organization>>(`${BASE}/${id}`).then(unwrap),

  create: (payload: OrganizationCreatePayload): Promise<Organization> =>
    apiClient.post<Envelope<Organization>>(BASE, payload).then(unwrap),

  update: (id: string, payload: OrganizationUpdatePayload): Promise<Organization> =>
    apiClient.patch<Envelope<Organization>>(`${BASE}/${id}`, payload).then(unwrap),

  delete: (id: string): Promise<void> =>
    apiClient.delete<Envelope<void>>(`${BASE}/${id}`).then(() => undefined),
};
