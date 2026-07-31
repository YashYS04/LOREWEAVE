/**
 * Relationship TypeScript types — mirrors backend relationship schemas.
 */

// ── Enums ──────────────────────────────────────────────────────────────────────

export type EntityType =
  | "character"
  | "location"
  | "organization"
  | "object"
  | "world_rule";

export type RelationshipDirection = "unidirectional" | "bidirectional";

export type RelationshipType =
  | "ally_of"
  | "enemy_of"
  | "friend_of"
  | "parent_of"
  | "child_of"
  | "sibling_of"
  | "mentor_of"
  | "student_of"
  | "member_of"
  | "leader_of"
  | "owns"
  | "created"
  | "created_by"
  | "located_in"
  | "lives_in"
  | "protects"
  | "rules"
  | "loves"
  | "hates"
  | "rival_of"
  | "custom";

// ── Model ──────────────────────────────────────────────────────────────────────

export interface Relationship {
  id: string;
  universe_id: string;
  source_entity_type: EntityType;
  source_entity_id: string;
  target_entity_type: EntityType;
  target_entity_id: string;
  relationship_type: RelationshipType;
  title: string | null;
  description: string | null;
  strength: number | null;
  direction: RelationshipDirection;
  metadata: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface RelationshipList {
  items: Relationship[];
  total: number;
  limit: number;
  offset: number;
}

// ── Request payloads ───────────────────────────────────────────────────────────

export interface CreateRelationshipRequest {
  universe_id: string;
  source_entity_type: EntityType;
  source_entity_id: string;
  target_entity_type: EntityType;
  target_entity_id: string;
  relationship_type: RelationshipType;
  title?: string;
  description?: string;
  strength?: number;
  direction?: RelationshipDirection;
  metadata?: Record<string, unknown>;
}

export interface UpdateRelationshipRequest {
  relationship_type?: RelationshipType;
  title?: string;
  description?: string;
  strength?: number;
  direction?: RelationshipDirection;
  metadata?: Record<string, unknown>;
}

// ── Display helpers ────────────────────────────────────────────────────────────

export const RELATIONSHIP_TYPE_LABELS: Record<RelationshipType, string> = {
  ally_of: "Ally Of",
  enemy_of: "Enemy Of",
  friend_of: "Friend Of",
  parent_of: "Parent Of",
  child_of: "Child Of",
  sibling_of: "Sibling Of",
  mentor_of: "Mentor Of",
  student_of: "Student Of",
  member_of: "Member Of",
  leader_of: "Leader Of",
  owns: "Owns",
  created: "Created",
  created_by: "Created By",
  located_in: "Located In",
  lives_in: "Lives In",
  protects: "Protects",
  rules: "Rules",
  loves: "Loves",
  hates: "Hates",
  rival_of: "Rival Of",
  custom: "Custom",
};

export const ENTITY_TYPE_LABELS: Record<EntityType, string> = {
  character: "Character",
  location: "Location",
  organization: "Organization",
  object: "Object",
  world_rule: "World Rule",
};

export const DIRECTION_LABELS: Record<RelationshipDirection, string> = {
  unidirectional: "One-way →",
  bidirectional: "Two-way ↔",
};
