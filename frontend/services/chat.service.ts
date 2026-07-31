/**
 * Chat API service — session management and SSE streaming.
 *
 * Streaming uses the Fetch API + ReadableStream so it works in both the
 * browser and Next.js server components (no EventSource needed).
 */
import { apiClient } from "@/lib/api-client";
import type {
  ChatSession,
  ChatSessionList,
  CreateSessionRequest,
  RenameSessionRequest,
  SendMessageRequest,
} from "@/types/chat";

const BASE = "/api/v1/ai/chat";
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface Envelope<T> {
  success: boolean;
  message: string;
  data: T;
}

const unwrap = <T>(e: Envelope<T>): T => e.data;

export const chatService = {
  /** Create a new chat session for a universe. */
  createSession: (payload: CreateSessionRequest): Promise<ChatSession> =>
    apiClient.post<Envelope<ChatSession>>(BASE, payload).then(unwrap),

  /** List all chat sessions for a universe, most recent first. */
  listSessions: (universeId: string, skip = 0, limit = 50): Promise<ChatSessionList> =>
    apiClient
      .get<Envelope<ChatSessionList>>(
        `${BASE}?universe_id=${encodeURIComponent(universeId)}&skip=${skip}&limit=${limit}`
      )
      .then(unwrap),

  /** Get a single session with its full message history. */
  getSession: (sessionId: string): Promise<ChatSession> =>
    apiClient.get<Envelope<ChatSession>>(`${BASE}/${sessionId}`).then(unwrap),

  /** Rename a session. */
  renameSession: (sessionId: string, payload: RenameSessionRequest): Promise<ChatSession> =>
    apiClient.patch<Envelope<ChatSession>>(`${BASE}/${sessionId}`, payload).then(unwrap),

  /** Soft-delete a session. */
  deleteSession: (sessionId: string): Promise<void> =>
    apiClient.delete<Envelope<null>>(`${BASE}/${sessionId}`).then(() => undefined),

  /**
   * Send a message and stream the AI response over SSE.
   *
   * @param sessionId   The target chat session.
   * @param payload     The message payload.
   * @param onToken     Called for each text token received.
   * @param onDone      Called once the `[DONE]` sentinel arrives.
   * @param onError     Called if the stream errors.
   * @returns           An AbortController so the caller can cancel mid-stream.
   */
  streamMessage: (
    sessionId: string,
    payload: SendMessageRequest,
    onToken: (token: string) => void,
    onDone: () => void,
    onError: (message: string) => void
  ): AbortController => {
    const controller = new AbortController();

    (async () => {
      try {
        const response = await fetch(`${API_BASE_URL}${BASE}/${sessionId}/message`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
          signal: controller.signal,
        });

        if (!response.ok || !response.body) {
          onError(`Request failed: ${response.status} ${response.statusText}`);
          return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          // Keep the last (possibly incomplete) line in the buffer.
          buffer = lines.pop() ?? "";

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            const data = line.slice("data: ".length).replace(/\r$/, "");

            if (data === "[DONE]") {
              onDone();
              return;
            }

            // Check for error event sent by the backend.
            if (data.startsWith("{")) {
              try {
                const parsed = JSON.parse(data) as { error?: string };
                if (parsed.error) {
                  onError(parsed.error);
                  return;
                }
              } catch {
                // Not JSON — treat as a normal token.
              }
            }

            // Unescape newlines encoded by the backend.
            onToken(data.replace(/\\n/g, "\n"));
          }
        }
      } catch (err) {
        if ((err as { name?: string }).name === "AbortError") return;
        onError(err instanceof Error ? err.message : "Streaming failed.");
      }
    })();

    return controller;
  },
};
