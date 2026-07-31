/**
 * TanStack Query hooks for the AI chat module.
 */
"use client";

import { useCallback, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { chatService } from "@/services/chat.service";
import type {
  ChatSession,
  CreateSessionRequest,
  PromptType,
  RenameSessionRequest,
  UIMessage,
} from "@/types/chat";

// ── Query keys ──────────────────────────────────────────────────────────────────

export const chatKeys = {
  sessions: (universeId: string) => ["chat", "sessions", universeId] as const,
  session: (sessionId: string) => ["chat", "session", sessionId] as const,
};

// ── Session list ───────────────────────────────────────────────────────────────

/** Fetch all sessions for a given universe. */
export function useChatSessions(universeId: string) {
  return useQuery({
    queryKey: chatKeys.sessions(universeId),
    queryFn: () => chatService.listSessions(universeId),
    enabled: !!universeId,
    staleTime: 10_000,
  });
}

/** Fetch a single session with its full message history. */
export function useChatSession(sessionId: string) {
  return useQuery({
    queryKey: chatKeys.session(sessionId),
    queryFn: () => chatService.getSession(sessionId),
    enabled: !!sessionId,
    staleTime: 0, // Always fresh — messages accumulate.
  });
}

// ── Session CRUD mutations ─────────────────────────────────────────────────────

/** Create a new chat session. */
export function useCreateSession(universeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateSessionRequest) => chatService.createSession(payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: chatKeys.sessions(universeId) });
    },
  });
}

/** Rename a session title. */
export function useRenameSession(universeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ sessionId, payload }: { sessionId: string; payload: RenameSessionRequest }) =>
      chatService.renameSession(sessionId, payload),
    onSuccess: (updated) => {
      qc.setQueryData(chatKeys.session(updated.id), updated);
      void qc.invalidateQueries({ queryKey: chatKeys.sessions(universeId) });
    },
  });
}

/** Soft-delete a session. */
export function useDeleteSession(universeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (sessionId: string) => chatService.deleteSession(sessionId),
    onSuccess: (_data, sessionId) => {
      qc.removeQueries({ queryKey: chatKeys.session(sessionId) });
      void qc.invalidateQueries({ queryKey: chatKeys.sessions(universeId) });
    },
  });
}

// ── Streaming message ──────────────────────────────────────────────────────────

export interface StreamState {
  /** Messages currently displayed in the UI (includes optimistic + streaming). */
  messages: UIMessage[];
  /** True while a stream is active. */
  isStreaming: boolean;
  /** Non-null when the last stream ended with an error. */
  streamError: string | null;
}

export interface UseChatStreamReturn extends StreamState {
  /** Load persisted history into the UI message list. */
  loadHistory: (session: ChatSession) => void;
  /** Send a user message and stream the assistant reply. */
  sendMessage: (sessionId: string, content: string, promptType: PromptType) => void;
  /** Abort an in-progress stream. */
  abort: () => void;
  /** Clear the current error banner. */
  clearError: () => void;
}

/**
 * Manages the real-time streaming state for a single chat session.
 *
 * The hook keeps its own `messages` list rather than reading from the
 * React Query cache so that streaming tokens update the UI immediately
 * without triggering cache invalidation on every token.
 *
 * After the stream completes the caller should refetch the session to
 * sync the persisted history from the server.
 */
export function useChatStream(onStreamDone?: (sessionId: string) => void): UseChatStreamReturn {
  const [messages, setMessages] = useState<UIMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamError, setStreamError] = useState<string | null>(null);

  const abortRef = useRef<AbortController | null>(null);
  // Track the current session so the onStreamDone callback has access.
  const sessionIdRef = useRef<string>("");

  const loadHistory = useCallback((session: ChatSession) => {
    setMessages(
      session.messages.map((m) => ({
        id: m.id,
        role: m.role,
        content: m.content,
      }))
    );
    setStreamError(null);
  }, []);

  const sendMessage = useCallback(
    (sessionId: string, content: string, promptType: PromptType) => {
      if (isStreaming) return;

      sessionIdRef.current = sessionId;

      // Optimistically add the user message.
      const userMsg: UIMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content,
      };

      // Placeholder for the assistant reply (streaming).
      const assistantId = crypto.randomUUID();
      const assistantPlaceholder: UIMessage = {
        id: assistantId,
        role: "assistant",
        content: "",
        streaming: true,
      };

      setMessages((prev) => [...prev, userMsg, assistantPlaceholder]);
      setIsStreaming(true);
      setStreamError(null);

      abortRef.current = chatService.streamMessage(
        sessionId,
        { content, prompt_type: promptType },
        // onToken
        (token) => {
          setMessages((prev) =>
            prev.map((m) => (m.id === assistantId ? { ...m, content: m.content + token } : m))
          );
        },
        // onDone
        () => {
          setMessages((prev) =>
            prev.map((m) => (m.id === assistantId ? { ...m, streaming: false } : m))
          );
          setIsStreaming(false);
          onStreamDone?.(sessionIdRef.current);
        },
        // onError
        (msg) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, content: m.content || `⚠ ${msg}`, streaming: false }
                : m
            )
          );
          setStreamError(msg);
          setIsStreaming(false);
        }
      );
    },
    [isStreaming, onStreamDone]
  );

  const abort = useCallback(() => {
    abortRef.current?.abort();
    setMessages((prev) => prev.map((m) => (m.streaming ? { ...m, streaming: false } : m)));
    setIsStreaming(false);
  }, []);

  const clearError = useCallback(() => setStreamError(null), []);

  return { messages, isStreaming, streamError, loadHistory, sendMessage, abort, clearError };
}
