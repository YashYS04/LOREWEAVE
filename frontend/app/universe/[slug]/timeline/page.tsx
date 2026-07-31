"use client";

/**
 * Timeline Intelligence Engine — vertical timeline visualization.
 *
 * Layout:
 *   - Header with search + sort + filters
 *   - Vertical timeline (chronological, sorted by start_date)
 *   - Event cards with type badge, importance, date range, participants
 *   - Inline add/edit via dialog
 *   - Empty state
 */

import { use, useState, useMemo } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  AlertCircle,
  Calendar,
  ChevronDown,
  Clock,
  Loader2,
  MapPin,
  Network,
  Package,
  Plus,
  Search,
  Swords,
  Users,
  X,
  BookOpen,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { EntityPageShell } from "@/components/entity";
import { useUniverseBySlug } from "@/hooks/use-universes";
import {
  useTimelineEvents,
  useCreateTimelineEvent,
  useDeleteTimelineEvent,
} from "@/hooks/use-timeline";
import type {
  EventStatus,
  EventType,
  TimelineEvent,
  TimelineParticipant,
} from "@/types/timeline";
import {
  EVENT_TYPE_LABELS,
  EVENT_TYPE_COLORS,
  EVENT_STATUS_COLORS,
  EVENT_STATUS_LABELS,
} from "@/types/timeline";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

// ── Constants ──────────────────────────────────────────────────────────────────

const ALL_EVENT_TYPES: EventType[] = [
  "battle", "discovery", "coronation", "death", "birth",
  "treaty", "rebellion", "disaster", "magic", "political",
  "economic", "religious", "custom",
];

const ALL_STATUSES: EventStatus[] = ["planned", "ongoing", "completed", "cancelled"];

const ENTITY_PATH_MAP: Record<string, string> = {
  character: "characters",
  location: "locations",
  organization: "organizations",
  object: "objects",
  world_rule: "rules",
};

const ENTITY_ICON_MAP: Record<string, React.ElementType> = {
  character: Users,
  location: MapPin,
  organization: Network,
  object: Package,
  world_rule: BookOpen,
};

// ── Create event schema ─────────────────────────────────────────────────────────

const createEventSchema = z.object({
  title: z.string().min(1, "Title is required").max(300),
  description: z.string().max(10000).optional(),
  event_type: z.enum([
    "battle", "discovery", "coronation", "death", "birth",
    "treaty", "rebellion", "disaster", "magic", "political",
    "economic", "religious", "custom",
  ] as const),
  status: z.enum(["planned", "ongoing", "completed", "cancelled"] as const),
  start_date: z.string().max(100).optional(),
  end_date: z.string().max(100).optional(),
  importance: z.number().min(1).max(10).optional(),
});

type CreateEventForm = z.infer<typeof createEventSchema>;

// ── Sub-components ─────────────────────────────────────────────────────────────

function ImportanceBadge({ importance }: { importance: number | null }) {
  if (importance == null) return null;
  const color =
    importance >= 8 ? "bg-red-100 text-red-700 border-red-200"
    : importance >= 5 ? "bg-amber-100 text-amber-700 border-amber-200"
    : "bg-slate-100 text-slate-600 border-slate-200";
  return (
    <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold ${color}`}>
      ★ {importance}/10
    </span>
  );
}

function ParticipantChip({
  participant,
  slug,
}: {
  participant: TimelineParticipant;
  slug: string;
}) {
  const Icon = ENTITY_ICON_MAP[participant.entity_type] ?? Users;
  const path = ENTITY_PATH_MAP[participant.entity_type];
  const content = (
    <span className="inline-flex items-center gap-1 rounded-full border border-border bg-muted px-2 py-0.5 text-[10px] text-muted-foreground hover:text-foreground transition-colors">
      <Icon className="h-2.5 w-2.5" />
      {participant.role ?? participant.entity_type}
    </span>
  );
  if (path) {
    return (
      <Link href={`/universe/${slug}/${path}/${participant.entity_id}`}>
        {content}
      </Link>
    );
  }
  return content;
}

function EventTypeTag({ type }: { type: EventType }) {
  const colors = EVENT_TYPE_COLORS[type];
  return (
    <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold ${colors.bg} ${colors.text} ${colors.border}`}>
      {EVENT_TYPE_LABELS[type]}
    </span>
  );
}

function StatusTag({ status }: { status: EventStatus }) {
  const colors = EVENT_STATUS_COLORS[status];
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium ${colors.bg} ${colors.text}`}>
      {EVENT_STATUS_LABELS[status]}
    </span>
  );
}

function TimelineEventCard({
  event,
  slug,
  onDelete,
  index,
}: {
  event: TimelineEvent;
  slug: string;
  onDelete: (id: string) => void;
  index: number;
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.04, duration: 0.25 }}
      className="relative pl-10"
    >
      {/* Timeline dot */}
      <div className="absolute left-0 top-4 flex h-8 w-8 items-center justify-center rounded-full border-2 border-border bg-background shadow-sm">
        <Swords className="h-3.5 w-3.5 text-muted-foreground" />
      </div>

      {/* Card */}
      <div className="rounded-xl border border-border bg-card p-4 shadow-sm">
        {/* Header row */}
        <div className="mb-2 flex flex-wrap items-start gap-2">
          <div className="flex-1 min-w-0">
            <h3 className="truncate font-semibold text-foreground">{event.title}</h3>
          </div>
          <div className="flex flex-wrap items-center gap-1.5 shrink-0">
            <EventTypeTag type={event.event_type as EventType} />
            <StatusTag status={event.status as EventStatus} />
            <ImportanceBadge importance={event.importance} />
          </div>
        </div>

        {/* Date row */}
        {(event.start_date || event.end_date) && (
          <div className="mb-2 flex items-center gap-1 text-xs text-muted-foreground">
            <Calendar className="h-3 w-3" />
            {event.start_date}
            {event.end_date && event.end_date !== event.start_date && (
              <>
                <span className="mx-0.5">→</span>
                {event.end_date}
              </>
            )}
          </div>
        )}

        {/* Description (collapsible) */}
        {event.description && (
          <div className="mb-2">
            <p className={`text-sm text-muted-foreground leading-relaxed ${expanded ? "" : "line-clamp-2"}`}>
              {event.description}
            </p>
            {event.description.length > 120 && (
              <button
                onClick={() => setExpanded((e) => !e)}
                className="mt-0.5 text-[11px] text-primary hover:underline"
              >
                {expanded ? "Show less" : "Show more"}
              </button>
            )}
          </div>
        )}

        {/* Participants */}
        {event.participants.length > 0 && (
          <div className="mb-2 flex flex-wrap gap-1">
            {event.participants.map((p) => (
              <ParticipantChip key={p.id} participant={p} slug={slug} />
            ))}
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end">
          <button
            onClick={() => onDelete(event.id)}
            className="text-[11px] text-muted-foreground hover:text-destructive transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
    </motion.div>
  );
}

// ── Create event dialog ────────────────────────────────────────────────────────

function CreateEventDialog({
  universeId,
  onClose,
}: {
  universeId: string;
  onClose: () => void;
}) {
  const createEvent = useCreateTimelineEvent();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CreateEventForm>({
    resolver: zodResolver(createEventSchema),
    defaultValues: {
      event_type: "custom",
      status: "completed",
    },
  });

  const onSubmit = async (data: CreateEventForm) => {
    await createEvent.mutateAsync({
      universe_id: universeId,
      ...data,
      importance: data.importance ?? undefined,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.96 }}
        className="w-full max-w-lg rounded-2xl border border-border bg-background p-6 shadow-xl"
      >
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold">New Timeline Event</h2>
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground">
            <X className="h-4 w-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Title */}
          <div>
            <label className="mb-1 block text-xs font-medium text-muted-foreground">
              Title *
            </label>
            <input
              {...register("title")}
              className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="The Great Battle…"
            />
            {errors.title && (
              <p className="mt-1 text-xs text-destructive">{errors.title.message}</p>
            )}
          </div>

          {/* Type + Status row */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-muted-foreground">
                Type
              </label>
              <select
                {...register("event_type")}
                className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              >
                {ALL_EVENT_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {EVENT_TYPE_LABELS[t]}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-muted-foreground">
                Status
              </label>
              <select
                {...register("status")}
                className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              >
                {ALL_STATUSES.map((s) => (
                  <option key={s} value={s}>
                    {EVENT_STATUS_LABELS[s]}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Start + End date */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-muted-foreground">
                Start Date
              </label>
              <input
                {...register("start_date")}
                className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Year 1042…"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-muted-foreground">
                End Date
              </label>
              <input
                {...register("end_date")}
                className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Year 1044…"
              />
            </div>
          </div>

          {/* Importance */}
          <div>
            <label className="mb-1 block text-xs font-medium text-muted-foreground">
              Importance (1–10)
            </label>
            <input
              type="number"
              min={1}
              max={10}
              {...register("importance", { valueAsNumber: true })}
              className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="7"
            />
          </div>

          {/* Description */}
          <div>
            <label className="mb-1 block text-xs font-medium text-muted-foreground">
              Description
            </label>
            <textarea
              {...register("description")}
              rows={3}
              className="w-full resize-none rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="What happened…"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" size="sm" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={isSubmitting || createEvent.isPending}>
              {(isSubmitting || createEvent.isPending) && (
                <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" />
              )}
              Create Event
            </Button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}

// ── Filter panel ───────────────────────────────────────────────────────────────

function FilterPanel({
  filterType,
  filterStatus,
  onTypeChange,
  onStatusChange,
  onReset,
}: {
  filterType: string;
  filterStatus: string;
  onTypeChange: (v: string) => void;
  onStatusChange: (v: string) => void;
  onReset: () => void;
}) {
  const [open, setOpen] = useState(false);
  const hasFilters = filterType !== "" || filterStatus !== "";

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm shadow-sm transition-colors hover:bg-muted ${
          hasFilters ? "border-primary text-primary" : "border-border text-foreground bg-background"
        }`}
      >
        <Sparkles className="h-3.5 w-3.5" />
        Filters
        {hasFilters && (
          <span className="flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground">
            {(filterType ? 1 : 0) + (filterStatus ? 1 : 0)}
          </span>
        )}
        <ChevronDown className={`h-3 w-3 transition-transform ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <motion.div
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute right-0 z-20 mt-1.5 w-52 rounded-xl border border-border bg-background p-3 shadow-lg"
        >
          <div className="mb-3">
            <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
              Event Type
            </p>
            <select
              value={filterType}
              onChange={(e) => onTypeChange(e.target.value)}
              className="w-full rounded-lg border border-border bg-background px-2 py-1.5 text-xs focus:outline-none"
            >
              <option value="">All types</option>
              {ALL_EVENT_TYPES.map((t) => (
                <option key={t} value={t}>{EVENT_TYPE_LABELS[t]}</option>
              ))}
            </select>
          </div>

          <div className="mb-3">
            <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
              Status
            </p>
            <select
              value={filterStatus}
              onChange={(e) => onStatusChange(e.target.value)}
              className="w-full rounded-lg border border-border bg-background px-2 py-1.5 text-xs focus:outline-none"
            >
              <option value="">All statuses</option>
              {ALL_STATUSES.map((s) => (
                <option key={s} value={s}>{EVENT_STATUS_LABELS[s]}</option>
              ))}
            </select>
          </div>

          {hasFilters && (
            <button
              onClick={() => { onReset(); setOpen(false); }}
              className="flex w-full items-center justify-center gap-1 rounded-lg bg-muted py-1 text-xs text-muted-foreground hover:text-foreground"
            >
              <X className="h-3 w-3" />
              Clear filters
            </button>
          )}
        </motion.div>
      )}
    </div>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────────

interface PageProps {
  params: Promise<{ slug: string }>;
}

export default function TimelinePage({ params }: PageProps) {
  const { slug } = use(params);

  const { data: universe, isLoading: uLoading } = useUniverseBySlug(slug);
  const uid = universe?.id ?? "";

  const [search, setSearch] = useState("");
  const [filterType, setFilterType] = useState("");
  const [filterStatus, setFilterStatus] = useState("");
  const [showDialog, setShowDialog] = useState(false);

  const { data: timelineData, isLoading: tLoading } = useTimelineEvents({
    universe_id: uid,
    limit: 200,
    event_type: filterType || undefined,
    status: filterStatus || undefined,
    search: search || undefined,
  });

  const deleteEvent = useDeleteTimelineEvent();

  const events = useMemo(() => timelineData?.items ?? [], [timelineData]);

  // ── Guards ─────────────────────────────────────────────────────────────────

  if (uLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!universe) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 text-center">
        <AlertCircle className="h-10 w-10 text-destructive" />
        <h1 className="text-2xl font-bold">Universe not found</h1>
        <Button asChild>
          <Link href="/">Go Home</Link>
        </Button>
      </div>
    );
  }

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <EntityPageShell
      breadcrumbs={[
        { label: universe.name, href: `/universe/${slug}/world` },
        { label: "Timeline" },
      ]}
    >
      {/* Page header */}
      <motion.div
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between"
      >
        <div>
          <div className="mb-1 flex items-center gap-2">
            <Clock className="h-5 w-5 text-primary" />
            <h1 className="text-2xl font-extrabold tracking-tight">Timeline</h1>
          </div>
          <p className="text-sm text-muted-foreground">
            The chronological history of{" "}
            <span className="font-medium text-foreground">{universe.name}</span>.
            {timelineData && (
              <span className="ml-1.5 text-muted-foreground">
                {timelineData.total} event{timelineData.total !== 1 ? "s" : ""}
              </span>
            )}
          </p>
        </div>
        <Button size="sm" onClick={() => setShowDialog(true)}>
          <Plus className="mr-1.5 h-4 w-4" />
          New Event
        </Button>
      </motion.div>

      {/* Search + Filter toolbar */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
      >
        {/* Search */}
        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search events…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="h-9 w-full rounded-lg border border-border bg-background pl-9 pr-9 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
          {search && (
            <button
              onClick={() => setSearch("")}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>

        <FilterPanel
          filterType={filterType}
          filterStatus={filterStatus}
          onTypeChange={setFilterType}
          onStatusChange={setFilterStatus}
          onReset={() => { setFilterType(""); setFilterStatus(""); }}
        />
      </motion.div>

      {/* Timeline content */}
      {tLoading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="h-7 w-7 animate-spin text-muted-foreground" />
        </div>
      ) : events.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="flex flex-col items-center gap-4 py-24 text-center"
        >
          <div className="flex h-16 w-16 items-center justify-center rounded-full border border-border bg-muted">
            <Clock className="h-7 w-7 text-muted-foreground" />
          </div>
          <h2 className="text-xl font-bold">
            {search || filterType || filterStatus ? "No matching events" : "No events yet"}
          </h2>
          <p className="max-w-sm text-sm text-muted-foreground">
            {search || filterType || filterStatus
              ? "Try adjusting your search or filters."
              : "Create your first timeline event to start building your world's history."}
          </p>
          {!search && !filterType && !filterStatus && (
            <Button size="sm" onClick={() => setShowDialog(true)}>
              <Plus className="mr-1.5 h-4 w-4" />
              Create First Event
            </Button>
          )}
        </motion.div>
      ) : (
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-3.5 top-0 bottom-0 w-px bg-border" />

          <div className="space-y-5">
            <AnimatePresence mode="popLayout">
              {events.map((event, i) => (
                <TimelineEventCard
                  key={event.id}
                  event={event}
                  slug={slug}
                  index={i}
                  onDelete={(id) => deleteEvent.mutate(id)}
                />
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}

      {/* Create dialog */}
      <AnimatePresence>
        {showDialog && (
          <CreateEventDialog
            universeId={uid}
            onClose={() => setShowDialog(false)}
          />
        )}
      </AnimatePresence>
    </EntityPageShell>
  );
}
