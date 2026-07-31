/**
 * Character TypeScript types — mirrors backend CharacterResponse schema.
 */

export type CharacterStatus = "active" | "deceased" | "unknown" | "archived";

export interface Character {
  id: string;
  universe_id: string;
  name: string;
  role: string | null;
  age: string | null;
  gender: string | null;
  occupation: string | null;
  biography: string | null;
  personality: string | null;
  goals: string | null;
  motivations: string | null;
  strengths: string | null;
  weaknesses: string | null;
  notes: string | null;
  status: CharacterStatus;
  created_at: string;
  updated_at: string;
}

export interface CharacterCreatePayload {
  universe_id: string;
  name: string;
  role?: string;
  age?: string;
  gender?: string;
  occupation?: string;
  biography?: string;
  personality?: string;
  goals?: string;
  motivations?: string;
  strengths?: string;
  weaknesses?: string;
  notes?: string;
  status?: CharacterStatus;
}

export interface CharacterUpdatePayload {
  name?: string;
  role?: string;
  age?: string;
  gender?: string;
  occupation?: string;
  biography?: string;
  personality?: string;
  goals?: string;
  motivations?: string;
  strengths?: string;
  weaknesses?: string;
  notes?: string;
  status?: CharacterStatus;
}

export interface CharacterListResponse {
  items: Character[];
  total: number;
  limit: number;
  offset: number;
}

export const CHARACTER_STATUS_LABELS: Record<CharacterStatus, string> = {
  active: "Active",
  deceased: "Deceased",
  unknown: "Unknown",
  archived: "Archived",
};

export const CHARACTER_STATUS_STYLES: Record<CharacterStatus, string> = {
  active: "bg-green-100 text-green-800 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800",
  deceased:
    "bg-gray-100 text-gray-600 border-gray-200 dark:bg-gray-800/50 dark:text-gray-400 dark:border-gray-700",
  unknown:
    "bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-800",
  archived:
    "bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-800/50 dark:text-slate-400 dark:border-slate-700",
};
