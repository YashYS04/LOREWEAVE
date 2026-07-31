/**
 * WorldRule TypeScript types — mirrors backend WorldRuleResponse schema.
 */

export interface WorldRule {
  id: string;
  universe_id: string;
  title: string;
  category: string | null;
  description: string | null;
  limitations: string | null;
  exceptions: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface WorldRuleCreatePayload {
  universe_id: string;
  title: string;
  category?: string;
  description?: string;
  limitations?: string;
  exceptions?: string;
  notes?: string;
}

export interface WorldRuleUpdatePayload {
  title?: string;
  category?: string;
  description?: string;
  limitations?: string;
  exceptions?: string;
  notes?: string;
}

export interface WorldRuleListResponse {
  items: WorldRule[];
  total: number;
  limit: number;
  offset: number;
}
