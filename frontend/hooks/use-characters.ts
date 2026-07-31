/**
 * TanStack Query hooks for the Character resource.
 */
"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { characterService } from "@/services/character.service";
import type { CharacterCreatePayload, CharacterUpdatePayload } from "@/types/character";

export const characterKeys = {
  all: ["characters"] as const,
  lists: (universeId: string) => [...characterKeys.all, "list", universeId] as const,
  detail: (id: string) => [...characterKeys.all, "detail", id] as const,
};

export function useCharacters(universeId: string, skip = 0, limit = 50) {
  return useQuery({
    queryKey: characterKeys.lists(universeId),
    queryFn: () => characterService.list(universeId, skip, limit),
    enabled: !!universeId,
  });
}

export function useCharacter(id: string) {
  return useQuery({
    queryKey: characterKeys.detail(id),
    queryFn: () => characterService.getById(id),
    enabled: !!id,
  });
}

export function useCreateCharacter(universeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: CharacterCreatePayload) => characterService.create(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: characterKeys.lists(universeId) });
    },
  });
}

export function useUpdateCharacter(id: string, universeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: CharacterUpdatePayload) => characterService.update(id, payload),
    onSuccess: (updated) => {
      qc.invalidateQueries({ queryKey: characterKeys.lists(universeId) });
      qc.setQueryData(characterKeys.detail(id), updated);
    },
  });
}

export function useDeleteCharacter(universeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => characterService.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: characterKeys.lists(universeId) });
    },
  });
}
