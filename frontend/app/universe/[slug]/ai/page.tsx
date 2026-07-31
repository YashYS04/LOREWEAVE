"use client";

/**
 * AI World Assistant — full chat interface.
 *
 * Layout:
 *   ┌─────────────────────────────────────────┐
 *   │  Page header (breadcrumb + title)        │
 *   ├──────────────┬──────────────────────────-┤
 *   │  Sidebar     │  Chat panel               │
 *   │  (sessions)  │  (messages + input)       │
 *   └──────────────┴───────────────────────────┘
 */

import { use, useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import { AnimatePresence, motion } from "framer-motion";
import {
  AlertCircle,
  Bot,
  ChevronDown,
  Clock,
  Edit2,
  Loader2,
  MessageSquare,
  Plus,
  Send,
  Share2,
  Sparkles,
  StopCircle,
  Trash2,
  User,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { EntityPageShell } from "@/components/entity";
import { useUniverseBySlug } from "@/hooks/use-universes";
import {
  useChatSessions,
  useCreateSession,
  useDeleteSession,
  useRenameSession,
  useChatStream,
} from "@/hooks/use-chat";
import { chatService } from "@/services/chat.service";
import type { ChatSession, PromptType } from "@/types/chat";
import { useTimelineEvents } from "@/hooks/use-timeline";
import { useRelationships } from "@/hooks/use-relationships";

// ── Constants ──────────────────────────────────────────────────────────────────

const PROMPT_TYPES: { value: PromptType; label: string }[] = [
  { value: "general", label: "General" },
  { value: "universe_summary", label: "Universe Summary" },
  { value: "lore_summary", label: "Lore Summary" },
  { value: "character_analysis", label: "Character Analysis" },
  { value: "conflict_suggestions", label: "Conflict Ideas" },
  { value: "consistency_check", label: "Consistency Check" },
  { value: "relationship_analysis", label: "Relationships" },
  { value: "timeline_summary", label: "Timeline" },
  { value: "story_expansion", label: "Story Expansion" },
];

// ── Sub-components ──────────────────────────────────────────────────────────────

function SessionItem({
  session,
  isActive,
  onSelect,
  onDelete,
  onRename,
}: {
  session: ChatSession;
  isActive: boolean;
  onSelect: () => void;
  onDelete: () => void;
  onRename: (newTitle: string) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(session.title);
  const inputRef = useRef<HTMLInputElement>(null);

  const commitRename = () => {
    const trimmed = draft.trim();
    if (trimmed && trimmed !== session.title) onRename(trimmed);
    setEditing(false);
  };

  useEffect(() => {
    if (editing) inputRef.current?.focus();
  }, [editing]);

  return (
    <div
      className={`group relative flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors ${
        isActive
          ? "bg-accent text-accent-foreground"
          : "text-muted-foreground hover:bg-muted hover:text-foreground"
      }`}
      onClick={editing ? undefined : onSelect}
    >
      <MessageSquare className="h-3.5 w-3.5 shrink-0" />

      {editing ? (
        <input
          ref={inputRef}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onBlur={commitRename}
          onKeyDown={(e) => {
            if (e.key === "Enter") commitRename();
            if (e.key === "Escape") setEditing(false);
          }}
          className="min-w-0 flex-1 truncate bg-transparent outline-none"
          onClick={(e) => e.stopPropagation()}
        />
      ) : (
        <span className="min-w-0 flex-1 truncate">{session.title}</span>
      )}

      {/* Action buttons — shown on hover */}
      {!editing && (
        <div className="absolute right-2 hidden items-center gap-0.5 group-hover:flex">
          <button
            className="rounded p-0.5 hover:bg-background/60"
            onClick={(e) => {
              e.stopPropagation();
              setDraft(session.title);
              setEditing(true);
            }}
            title="Rename"
          >
            <Edit2 className="h-3 w-3" />
          </button>
          <button
            className="rounded p-0.5 hover:bg-background/60 hover:text-destructive"
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
            title="Delete"
          >
            <Trash2 className="h-3 w-3" />
          </button>
        </div>
      )}
    </div>
  );
}

function MessageBubble({
  role,
  content,
  streaming,
}: {
  role: "user" | "assistant";
  content: string;
  streaming?: boolean;
}) {
  const isUser = role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}
    >
      {/* Avatar */}
      <div
        className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full ${
          isUser ? "bg-primary text-primary-foreground" : "bg-muted"
        }`}
      >
        {isUser ? <User className="h-3.5 w-3.5" /> : <Bot className="h-3.5 w-3.5" />}
      </div>

      {/* Bubble */}
      <div
        className={`max-w-[80%] rounded-xl px-4 py-2.5 text-sm leading-relaxed overflow-hidden break-words ${
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted text-foreground shadow-sm"
        }`}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap break-words">{content}</p>
        ) : (
          <div className="prose prose-sm dark:prose-invert max-w-none overflow-x-auto break-words">
            <ReactMarkdown>{content}</ReactMarkdown>
            {streaming && (
              <span className="ml-0.5 inline-block h-4 w-0.5 animate-pulse bg-current" />
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
}

function EmptyChatState({ onStart }: { onStart: () => void }) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-4 px-8 py-16 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-full border border-border bg-muted">
        <Sparkles className="h-7 w-7 text-muted-foreground" />
      </div>
      <div>
        <p className="mb-1 font-medium">Start a conversation</p>
        <p className="max-w-xs text-sm text-muted-foreground">
          Ask the AI anything about your universe — characters, lore, plot ideas,
          consistency checks, and more.
        </p>
      </div>
      <Button size="sm" onClick={onStart}>
        <Plus className="mr-1.5 h-4 w-4" />
        New Chat
      </Button>
    </div>
  );
}

function ActiveSessionEmptyState({ onSuggest }: { onSuggest: (msg: string) => void }) {
  const suggestions = [
    "Summarize the main conflicts in this universe.",
    "Help me brainstorm a new faction.",
    "Are there any timeline inconsistencies?",
    "Suggest a tragic backstory for a hero."
  ];

  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-6 px-8 py-10 text-center h-full">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
        <Bot className="h-6 w-6 text-primary" />
      </div>
      <div>
        <h3 className="mb-1 font-semibold text-foreground">How can I help you build your world?</h3>
        <p className="text-sm text-muted-foreground">Choose a suggestion below or type your own prompt.</p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg mt-4">
        {suggestions.map((s, i) => (
          <button
            key={i}
            onClick={() => onSuggest(s)}
            className="text-left text-sm p-3 rounded-xl border border-border/50 bg-card/50 hover:bg-card hover:border-primary/50 transition-all shadow-sm"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}

// ── Prompt type selector ───────────────────────────────────────────────────────

function PromptTypeSelector({
  value,
  onChange,
}: {
  value: PromptType;
  onChange: (v: PromptType) => void;
}) {
  const [open, setOpen] = useState(false);
  const selected = PROMPT_TYPES.find((p) => p.value === value);

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1 rounded-md border border-border bg-background px-2.5 py-1.5 text-xs text-muted-foreground transition-colors hover:text-foreground"
      >
        {selected?.label ?? "General"}
        <ChevronDown className="h-3 w-3" />
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.12 }}
            className="absolute bottom-full left-0 mb-1 w-44 rounded-lg border border-border bg-popover shadow-md"
          >
            {PROMPT_TYPES.map((pt) => (
              <button
                key={pt.value}
                type="button"
                className={`w-full px-3 py-1.5 text-left text-xs transition-colors hover:bg-muted ${
                  pt.value === value ? "font-semibold text-foreground" : "text-muted-foreground"
                }`}
                onClick={() => {
                  onChange(pt.value);
                  setOpen(false);
                }}
              >
                {pt.label}
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ── Page component ─────────────────────────────────────────────────────────────

interface PageProps {
  params: Promise<{ slug: string }>;
}

export default function AIWorldAssistantPage({ params }: PageProps) {
  const { slug } = use(params);

  const { data: universe, isLoading: uLoading } = useUniverseBySlug(slug);
  const uid = universe?.id ?? "";

  // ── Metrics for context row ────────────────────────────────────────────────────
  const { data: timelineData } = useTimelineEvents({ universe_id: uid, limit: 1 });
  const { data: relData } = useRelationships({ universe_id: uid, limit: 1 });

  // ── Sessions ──────────────────────────────────────────────────────────────────
  const { data: sessionList, isLoading: sessionsLoading } = useChatSessions(uid);
  const createSession = useCreateSession(uid);
  const deleteSession = useDeleteSession(uid);
  const renameSession = useRenameSession(uid);

  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [promptType, setPromptType] = useState<PromptType>("general");
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // ── Streaming ─────────────────────────────────────────────────────────────────
  const handleStreamDone = useCallback(
    async (sessionId: string) => {
      // Re-fetch the session after streaming finishes so we have accurate IDs.
      try {
        const updated = await chatService.getSession(sessionId);
        stream.loadHistory(updated);
      } catch {
        // Non-critical: UI already shows tokens from the stream.
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  );

  const stream = useChatStream(handleStreamDone);

  // Load history whenever the active session changes.
  useEffect(() => {
    if (!activeSessionId) return;
    chatService
      .getSession(activeSessionId)
      .then((s) => stream.loadHistory(s))
      .catch(() => undefined);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeSessionId]);

  // Auto-scroll to newest message.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [stream.messages]);

  // ── Handlers ──────────────────────────────────────────────────────────────────

  const handleNewSession = async () => {
    if (!uid) return;
    const sess = await createSession.mutateAsync({ universe_id: uid });
    setActiveSessionId(sess.id);
    stream.loadHistory(sess);
  };

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || !activeSessionId || stream.isStreaming) return;
    setInput("");
    stream.sendMessage(activeSessionId, trimmed, promptType);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // ── Loading / error guards ─────────────────────────────────────────────────────

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

  const sessions = sessionList?.items ?? [];

  // ── Render ─────────────────────────────────────────────────────────────────────

  return (
    <EntityPageShell
      breadcrumbs={[
        { label: universe.name, href: `/universe/${slug}/world` },
        { label: "AI World Assistant" },
      ]}
    >
      {/* Page header */}
      <motion.div
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6 flex items-center justify-between"
      >
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            <h1 className="text-2xl font-extrabold tracking-tight">AI World Assistant</h1>
          </div>
          <p className="mt-0.5 text-sm text-muted-foreground">
            Powered by IBM Granite 3.3 · {universe.name}
          </p>
        </div>

        <Button size="sm" onClick={handleNewSession} disabled={createSession.isPending}>
          {createSession.isPending ? (
            <Loader2 className="mr-1.5 h-4 w-4 animate-spin" />
          ) : (
            <Plus className="mr-1.5 h-4 w-4" />
          )}
          New Chat
        </Button>
      </motion.div>

      {/* Context metrics row */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="mb-4 flex flex-wrap items-center gap-2"
      >
        <Link
          href={`/universe/${slug}/relationships`}
          className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-card px-3 py-1.5 text-xs text-muted-foreground shadow-sm transition-colors hover:border-primary hover:text-foreground"
        >
          <Share2 className="h-3.5 w-3.5 text-primary" />
          <span className="font-semibold text-foreground">{relData?.total ?? 0}</span>
          Relationships
        </Link>
        <Link
          href={`/universe/${slug}/timeline`}
          className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-card px-3 py-1.5 text-xs text-muted-foreground shadow-sm transition-colors hover:border-primary hover:text-foreground"
        >
          <Clock className="h-3.5 w-3.5 text-primary" />
          <span className="font-semibold text-foreground">{timelineData?.total ?? 0}</span>
          Timeline Events
        </Link>
      </motion.div>

      {/* Main layout */}
      <div className="flex h-[calc(100vh-14rem)] min-h-[520px] gap-4 overflow-hidden rounded-xl border border-border">
        {/* ── Sidebar ── */}
        <aside className="flex w-56 shrink-0 flex-col border-r border-border bg-muted/20">
          <div className="border-b border-border px-3 py-2.5">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Conversations
            </p>
          </div>

          <div className="flex-1 overflow-y-auto py-2 px-1.5 space-y-0.5">
            {sessionsLoading ? (
              <div className="flex justify-center pt-6">
                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
              </div>
            ) : sessions.length === 0 ? (
              <p className="px-3 pt-4 text-center text-xs text-muted-foreground">
                No conversations yet
              </p>
            ) : (
              sessions.map((s) => (
                <SessionItem
                  key={s.id}
                  session={s}
                  isActive={s.id === activeSessionId}
                  onSelect={() => setActiveSessionId(s.id)}
                  onDelete={() => {
                    deleteSession.mutate(s.id);
                    if (s.id === activeSessionId) setActiveSessionId(null);
                  }}
                  onRename={(title) =>
                    renameSession.mutate({ sessionId: s.id, payload: { title } })
                  }
                />
              ))
            )}
          </div>
        </aside>

        {/* ── Chat panel ── */}
        <div className="flex flex-1 flex-col overflow-hidden">
          {!activeSessionId ? (
            <EmptyChatState onStart={handleNewSession} />
          ) : (
            <>
              {/* Messages */}
              <div className="flex-1 overflow-y-auto px-6 py-5 space-y-4">
                {stream.messages.length === 0 && !stream.isStreaming && (
                  <ActiveSessionEmptyState 
                    onSuggest={(msg) => {
                      if (activeSessionId) stream.sendMessage(activeSessionId, msg, promptType);
                    }} 
                  />
                )}

                {stream.messages.map((msg) => (
                  <MessageBubble
                    key={msg.id}
                    role={msg.role}
                    content={msg.content}
                    streaming={msg.streaming}
                  />
                ))}

                {/* Streaming indicator when assistant placeholder is empty */}
                {stream.isStreaming &&
                  stream.messages.at(-1)?.content === "" && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex gap-3"
                    >
                      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-muted">
                        <Bot className="h-3.5 w-3.5" />
                      </div>
                      <div className="rounded-xl bg-muted px-4 py-2.5">
                        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                      </div>
                    </motion.div>
                  )}

                <div ref={bottomRef} />
              </div>

              {/* Error banner */}
              <AnimatePresence>
                {stream.streamError && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mx-4 mb-2 flex items-center gap-2 rounded-lg border border-destructive/40 bg-destructive/10 px-3 py-2 text-xs text-destructive"
                  >
                    <AlertCircle className="h-3.5 w-3.5 shrink-0" />
                    <span className="flex-1">{stream.streamError}</span>
                    <button onClick={stream.clearError}>
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Input bar */}
              <div className="border-t border-border bg-background px-4 py-3">
                <div className="flex items-end gap-2">
                  {/* Prompt type selector */}
                  <PromptTypeSelector value={promptType} onChange={setPromptType} />

                  {/* Textarea */}
                  <div className="relative flex-1">
                    <textarea
                      ref={textareaRef}
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={handleKeyDown}
                      disabled={stream.isStreaming}
                      placeholder={
                        stream.isStreaming
                          ? "Generating response…"
                          : "Ask about your universe… (Enter to send, Shift+Enter for newline)"
                      }
                      rows={1}
                      className="w-full resize-none rounded-lg border border-border bg-muted/50 px-3 py-2 text-sm outline-none placeholder:text-muted-foreground focus:border-primary focus:ring-1 focus:ring-primary disabled:opacity-50"
                      style={{ maxHeight: "140px", overflowY: "auto" }}
                    />
                  </div>

                  {/* Send / Abort */}
                  {stream.isStreaming ? (
                    <Button
                      size="icon"
                      variant="outline"
                      onClick={stream.abort}
                      title="Stop generation"
                      className="h-9 w-9 shrink-0 text-destructive hover:text-destructive"
                    >
                      <StopCircle className="h-4 w-4" />
                    </Button>
                  ) : (
                    <Button
                      size="icon"
                      onClick={handleSend}
                      disabled={!input.trim() || stream.isStreaming}
                      title="Send (Enter)"
                      className="h-9 w-9 shrink-0"
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </EntityPageShell>
  );
}
