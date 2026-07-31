/**
 * Relationship API service.
 */
import { apiClient } from "@/lib/api-client";
import type {
  CreateRelationshipRequest,
  Relationship,
  RelationshipList,
  UpdateRelationshipRequest,
} from "@/types/relationship";

const BASE = "/api/v1/relationships";

interface Envelope<T> {
  success: boolean;
  message: string;
  data: T;
}

const unwrap = <T>(e: Envelope<T>): T => e.data;

export interface ListRelationshipsParams {
  universe_id: string;
  skip?: number;
  limit?: number;
  entity_id?: string;
  entity_type?: string;
  relationship_type?: string;
  search?: string;
}

export const relationshipService = {
  create: (payload: CreateRelationshipRequest): Promise<Relationship> =>
    apiClient.post<Envelope<Relationship>>(BASE, payload).then(unwrap),

  list: (params: ListRelationshipsParams): Promise<RelationshipList> => {
    const qs = new URLSearchParams();
    qs.set("universe_id", params.universe_id);
    if (params.skip !== undefined) qs.set("skip", String(params.skip));
    if (params.limit !== undefined) qs.set("limit", String(params.limit));
    if (params.entity_id) qs.set("entity_id", params.entity_id);
    if (params.entity_type) qs.set("entity_type", params.entity_type);
    if (params.relationship_type) qs.set("relationship_type", params.relationship_type);
    if (params.search) qs.set("search", params.search);
    return apiClient.get<Envelope<RelationshipList>>(`${BASE}?${qs.toString()}`).then(unwrap);
  },

  getById: (id: string): Promise<Relationship> =>
    apiClient.get<Envelope<Relationship>>(`${BASE}/${id}`).then(unwrap),

  update: (id: string, payload: UpdateRelationshipRequest): Promise<Relationship> =>
    apiClient.patch<Envelope<Relationship>>(`${BASE}/${id}`, payload).then(unwrap),

  delete: (id: string): Promise<void> =>
    apiClient.delete<Envelope<null>>(`${BASE}/${id}`).then(() => undefined),
};
