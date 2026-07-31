/**
 * Location TypeScript types — mirrors backend LocationResponse schema.
 */

export interface Location {
  id: string;
  universe_id: string;
  name: string;
  type: string | null;
  description: string | null;
  climate: string | null;
  culture: string | null;
  population: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface LocationCreatePayload {
  universe_id: string;
  name: string;
  type?: string;
  description?: string;
  climate?: string;
  culture?: string;
  population?: string;
  notes?: string;
}

export interface LocationUpdatePayload {
  name?: string;
  type?: string;
  description?: string;
  climate?: string;
  culture?: string;
  population?: string;
  notes?: string;
}

export interface LocationListResponse {
  items: Location[];
  total: number;
  limit: number;
  offset: number;
}
