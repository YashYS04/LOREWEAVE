/**
 * TypeScript types for the Timeline Intelligence Engine.
 */

// ── Enums ───────────────────────────────────────────────────────────────────

export type EventType =
  | "battle"
  | "discovery"
  | "coronation"
  | "death"
  | "birth"
  | "treaty"
  | "rebellion"
  | "disaster"
  | "magic"
  | "political"
  | "economic"
  | "religious"
  | "custom";

export type EventStatus = "planned" | "ongoing" | "completed" | "cancelled";

export type ParticipantEntityType =
  | "character"
  | "location"
  | "organization"
  | "object"
  | "world_rule";

// ── Event participant ────────────────────────────────────────────────────────

export interface TimelineParticipant {
  id: string;
  event_id: string;
  entity_type: ParticipantEntityType;
  entity_id: string;
  role: string | null;
}

export interface ParticipantInput {
  entity_type: ParticipantEntityType;
  entity_id: string;
  role?: string;
}

// ── Timeline event ───────────────────────────────────────────────────────────

export interface TimelineEvent {
  id: string;
  universe_id: string;
  title: string;
  description: string | null;
  event_type: EventType;
  status: EventStatus;
  start_date: string | null;
  end_date: string | null;
  importance: number | null;
  metadata: Record<string, unknown> | null;
  participants: TimelineParticipant[];
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface TimelineEventList {
  items: TimelineEvent[];
  total: number;
  limit: number;
  offset: number;
}

// ── Request types ────────────────────────────────────────────────────────────

export interface CreateTimelineEventRequest {
  universe_id: string;
  title: string;
  description?: string;
  event_type?: EventType;
  status?: EventStatus;
  start_date?: string;
  end_date?: string;
  importance?: number;
  metadata?: Record<string, unknown>;
  participants?: ParticipantInput[];
}

export interface UpdateTimelineEventRequest {
  title?: string;
  description?: string;
  event_type?: EventType;
  status?: EventStatus;
  start_date?: string;
  end_date?: string;
  importance?: number;
  metadata?: Record<string, unknown>;
  participants?: ParticipantInput[];
}

// ── Display helpers ──────────────────────────────────────────────────────────

export const EVENT_TYPE_LABELS: Record<EventType, string> = {
  battle: "Battle",
  discovery: "Discovery",
  coronation: "Coronation",
  death: "Death",
  birth: "Birth",
  treaty: "Treaty",
  rebellion: "Rebellion",
  disaster: "Disaster",
  magic: "Magic",
  political: "Political",
  economic: "Economic",
  religious: "Religious",
  custom: "Custom",
};

export const EVENT_STATUS_LABELS: Record<EventStatus, string> = {
  planned: "Planned",
  ongoing: "Ongoing",
  completed: "Completed",
  cancelled: "Cancelled",
};

export const EVENT_TYPE_COLORS: Record<EventType, { bg: string; text: string; border: string }> = {
  battle:     { bg: "bg-red-50",    text: "text-red-700",    border: "border-red-200" },
  discovery:  { bg: "bg-blue-50",   text: "text-blue-700",   border: "border-blue-200" },
  coronation: { bg: "bg-yellow-50", text: "text-yellow-700", border: "border-yellow-200" },
  death:      { bg: "bg-slate-50",  text: "text-slate-700",  border: "border-slate-200" },
  birth:      { bg: "bg-green-50",  text: "text-green-700",  border: "border-green-200" },
  treaty:     { bg: "bg-teal-50",   text: "text-teal-700",   border: "border-teal-200" },
  rebellion:  { bg: "bg-orange-50", text: "text-orange-700", border: "border-orange-200" },
  disaster:   { bg: "bg-rose-50",   text: "text-rose-700",   border: "border-rose-200" },
  magic:      { bg: "bg-purple-50", text: "text-purple-700", border: "border-purple-200" },
  political:  { bg: "bg-indigo-50", text: "text-indigo-700", border: "border-indigo-200" },
  economic:   { bg: "bg-amber-50",  text: "text-amber-700",  border: "border-amber-200" },
  religious:  { bg: "bg-pink-50",   text: "text-pink-700",   border: "border-pink-200" },
  custom:     { bg: "bg-gray-50",   text: "text-gray-700",   border: "border-gray-200" },
};

export const EVENT_STATUS_COLORS: Record<EventStatus, { bg: string; text: string }> = {
  planned:   { bg: "bg-blue-100",   text: "text-blue-700" },
  ongoing:   { bg: "bg-amber-100",  text: "text-amber-700" },
  completed: { bg: "bg-green-100",  text: "text-green-700" },
  cancelled: { bg: "bg-slate-100",  text: "text-slate-500" },
};
