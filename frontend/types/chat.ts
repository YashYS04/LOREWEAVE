/**
 * Chat TypeScript types — mirrors backend AI chat schemas.
 */

// ── Message ────────────────────────────────────────────────────────────────────

export type MessageRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  session_id: string;
  role: MessageRole;
  content: string;
  prompt_type: string | null;
  created_at: string;
}

// ── Session ────────────────────────────────────────────────────────────────────

export interface ChatSession {
  id: string;
  universe_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
  messages: ChatMessage[];
}

export interface ChatSessionList {
  items: ChatSession[];
  total: number;
}

// ── Request payloads ───────────────────────────────────────────────────────────

export interface CreateSessionRequest {
  universe_id: string;
  title?: string;
}

export interface RenameSessionRequest {
  title: string;
}

export type PromptType =
  | "general"
  | "universe_summary"
  | "lore_summary"
  | "character_analysis"
  | "conflict_suggestions"
  | "consistency_check"
  | "relationship_analysis"
  | "timeline_summary"
  | "story_expansion";

export interface SendMessageRequest {
  content: string;
  prompt_type: PromptType;
}

// ── UI-layer message (optimistic / stream state) ───────────────────────────────

/** A message as shown in the UI — may be in-flight (streaming). */
export interface UIMessage {
  id: string;
  role: MessageRole;
  content: string;
  /** True while the assistant token stream is still open. */
  streaming?: boolean;
}
