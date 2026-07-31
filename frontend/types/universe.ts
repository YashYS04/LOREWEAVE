/**
 * Universe TypeScript types — mirrors backend UniverseResponse schema.
 */

export type UniverseStatus = "draft" | "active" | "archived";

export type UniverseGenre =
  | "fantasy"
  | "science_fiction"
  | "mystery"
  | "horror"
  | "romance"
  | "adventure"
  | "historical"
  | "thriller"
  | "cyberpunk"
  | "steampunk"
  | "slice_of_life"
  | "other";

export interface Universe {
  id: string;
  name: string;
  slug: string;
  genre: UniverseGenre;
  description: string | null;
  tone: string | null;
  target_audience: string | null;
  status: UniverseStatus;
  cover_image: string | null;
  created_at: string;
  updated_at: string;
}

export interface UniverseCreatePayload {
  name: string;
  genre: UniverseGenre;
  description?: string;
  tone?: string;
  target_audience?: string;
}

export interface UniverseUpdatePayload {
  name?: string;
  genre?: UniverseGenre;
  description?: string;
  tone?: string;
  target_audience?: string;
  status?: UniverseStatus;
}

export interface UniverseListResponse {
  items: Universe[];
  total: number;
}

export const GENRE_LABELS: Record<UniverseGenre, string> = {
  fantasy: "Fantasy",
  science_fiction: "Science Fiction",
  mystery: "Mystery",
  horror: "Horror",
  romance: "Romance",
  adventure: "Adventure",
  historical: "Historical",
  thriller: "Thriller",
  cyberpunk: "Cyberpunk",
  steampunk: "Steampunk",
  slice_of_life: "Slice of Life",
  other: "Other",
};
