/**
 * AI TypeScript types — mirrors backend AI schemas.
 */

// ── Universe Context ──────────────────────────────────────────────────────────

export interface UniverseSnippet {
  id: string;
  name: string;
  genre: string;
  description: string | null;
  tone: string | null;
  status: string;
}

export interface CharacterSnippet {
  id: string;
  name: string;
  role: string | null;
  biography: string | null;
  personality: string | null;
  goals: string | null;
  motivations: string | null;
  strengths: string | null;
  weaknesses: string | null;
}

export interface LocationSnippet {
  id: string;
  name: string;
  type: string | null;
  description: string | null;
  climate: string | null;
  culture: string | null;
}

export interface OrganizationSnippet {
  id: string;
  name: string;
  type: string | null;
  description: string | null;
  leader: string | null;
  purpose: string | null;
}

export interface WorldObjectSnippet {
  id: string;
  name: string;
  category: string | null;
  description: string | null;
  origin: string | null;
  abilities: string | null;
}

export interface WorldRuleSnippet {
  id: string;
  title: string;
  category: string | null;
  description: string | null;
  limitations: string | null;
  exceptions: string | null;
}

export interface RelationshipSnippet {
  id: string;
  source: string;
  source_type: string;
  relationship: string;
  target: string;
  target_type: string;
  strength: number | null;
  direction: string;
  description: string | null;
}

export interface ContextMetadata {
  generated_at: string;
  counts: {
    characters: number;
    locations: number;
    organizations: number;
    objects: number;
    world_rules: number;
  };
  version: string;
}

export interface UniverseContext {
  universe: UniverseSnippet;
  characters: CharacterSnippet[];
  locations: LocationSnippet[];
  organizations: OrganizationSnippet[];
  objects: WorldObjectSnippet[];
  world_rules: WorldRuleSnippet[];
  relationships: RelationshipSnippet[];
  metadata: ContextMetadata;
}

// ── Provider health ────────────────────────────────────────────────────────────

export interface ProviderHealth {
  provider_name: string;
  model: string;
  healthy: boolean;
  message: string;
  version: string | null;
}

// ── Request payloads ───────────────────────────────────────────────────────────

export interface ContextRequest {
  universe_id: string;
}
