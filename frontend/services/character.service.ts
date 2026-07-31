/**
 * Character API service — all backend calls for the Character resource.
 */
import { apiClient } from "@/lib/api-client";
import type {
  Character,
  CharacterCreatePayload,
  CharacterListResponse,
  CharacterUpdatePayload,
} from "@/types/character";

const BASE = "/api/v1/characters";

interface ApiEnvelope<T> {
  success: boolean;
  message: string;
  data: T;
}

function unwrap<T>(envelope: ApiEnvelope<T>): T {
  return envelope.data;
}

export const characterService = {
  list: (universeId: string, skip = 0, limit = 50): Promise<CharacterListResponse> =>
    apiClient
      .get<ApiEnvelope<CharacterListResponse>>(
        `${BASE}?universe_id=${universeId}&skip=${skip}&limit=${limit}`
      )
      .then(unwrap),

  getById: (id: string): Promise<Character> =>
    apiClient.get<ApiEnvelope<Character>>(`${BASE}/${id}`).then(unwrap),

  create: (payload: CharacterCreatePayload): Promise<Character> =>
    apiClient.post<ApiEnvelope<Character>>(BASE, payload).then(unwrap),

  update: (id: string, payload: CharacterUpdatePayload): Promise<Character> =>
    apiClient.patch<ApiEnvelope<Character>>(`${BASE}/${id}`, payload).then(unwrap),

  delete: (id: string): Promise<void> =>
    apiClient.delete<ApiEnvelope<void>>(`${BASE}/${id}`).then(() => undefined),
};
