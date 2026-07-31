/**
 * WorldObject TypeScript types — mirrors backend WorldObjectResponse schema.
 */

export interface WorldObject {
  id: string;
  universe_id: string;
  name: string;
  category: string | null;
  description: string | null;
  origin: string | null;
  owner: string | null;
  abilities: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface WorldObjectCreatePayload {
  universe_id: string;
  name: string;
  category?: string;
  description?: string;
  origin?: string;
  owner?: string;
  abilities?: string;
  notes?: string;
}

export interface WorldObjectUpdatePayload {
  name?: string;
  category?: string;
  description?: string;
  origin?: string;
  owner?: string;
  abilities?: string;
  notes?: string;
}

export interface WorldObjectListResponse {
  items: WorldObject[];
  total: number;
  limit: number;
  offset: number;
}
