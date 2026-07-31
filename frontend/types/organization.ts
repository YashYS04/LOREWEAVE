/**
 * Organization TypeScript types — mirrors backend OrganizationResponse schema.
 */

export interface Organization {
  id: string;
  universe_id: string;
  name: string;
  type: string | null;
  description: string | null;
  leader: string | null;
  purpose: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface OrganizationCreatePayload {
  universe_id: string;
  name: string;
  type?: string;
  description?: string;
  leader?: string;
  purpose?: string;
  notes?: string;
}

export interface OrganizationUpdatePayload {
  name?: string;
  type?: string;
  description?: string;
  leader?: string;
  purpose?: string;
  notes?: string;
}

export interface OrganizationListResponse {
  items: Organization[];
  total: number;
  limit: number;
  offset: number;
}
