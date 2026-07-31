/**
 * WorldRule API service.
 */
import { apiClient } from "@/lib/api-client";
import type {
  WorldRule,
  WorldRuleCreatePayload,
  WorldRuleListResponse,
  WorldRuleUpdatePayload,
} from "@/types/world-rule";

const BASE = "/api/v1/rules";

interface Envelope<T> {
  success: boolean;
  message: string;
  data: T;
}

const unwrap = <T>(e: Envelope<T>): T => e.data;

export const worldRuleService = {
  list: (universeId: string, skip = 0, limit = 50): Promise<WorldRuleListResponse> =>
    apiClient
      .get<Envelope<WorldRuleListResponse>>(
        `${BASE}?universe_id=${universeId}&skip=${skip}&limit=${limit}`
      )
      .then(unwrap),

  getById: (id: string): Promise<WorldRule> =>
    apiClient.get<Envelope<WorldRule>>(`${BASE}/${id}`).then(unwrap),

  create: (payload: WorldRuleCreatePayload): Promise<WorldRule> =>
    apiClient.post<Envelope<WorldRule>>(BASE, payload).then(unwrap),

  update: (id: string, payload: WorldRuleUpdatePayload): Promise<WorldRule> =>
    apiClient.patch<Envelope<WorldRule>>(`${BASE}/${id}`, payload).then(unwrap),

  delete: (id: string): Promise<void> =>
    apiClient.delete<Envelope<void>>(`${BASE}/${id}`).then(() => undefined),
};
