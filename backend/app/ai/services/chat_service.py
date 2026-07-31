"""ChatService — conversation memory, context assembly, and streaming.

Pipeline for every user message:

  1. Persist the user message
  2. Build universe context (UniverseContextBuilder)
  3. Load conversation history from this session
  4. Render the prompt template (with context + history + new message)
  5. Call provider.stream_generate()
  6. Accumulate streamed tokens and persist the assistant reply
  7. Yield tokens to the caller so they can be streamed over SSE

The service owns conversation persistence.
AIService owns single-shot generation.
Both share the same provider abstraction.
"""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.context.builder import UniverseContextBuilder
from app.ai.prompts.templates import PROMPT_REGISTRY, get_prompt
from app.ai.providers.base import AIProvider
from app.ai.schemas.ai import UniverseContext
from app.models.chat import ChatMessage, ChatSession
from app.repositories.chat import ChatRepository

logger = logging.getLogger(__name__)

# System preamble injected once at the start of every conversation.
_SYSTEM_PREAMBLE = (
    "You are LOREWEAVE, an expert AI assistant specialised in creative world building. "
    "You help authors develop rich fictional universes, craft compelling characters, "
    "build intricate lore, and explore narrative possibilities. "
    "Be specific, creative, and always ground your answers in the provided universe context."
)

# Maximum history turns to include (each turn = user + assistant).
_MAX_HISTORY_TURNS = 10


def _format_history(messages: list[ChatMessage]) -> str:
    """Format prior conversation turns into a readable transcript."""
    if not messages:
        return ""
    lines = ["\nPREVIOUS CONVERSATION:"]
    for msg in messages[-(2 * _MAX_HISTORY_TURNS) :]:
        prefix = "User" if msg.role == "user" else "Assistant"
        lines.append(f"{prefix}: {msg.content}")
    return "\n".join(lines)


def _build_chat_prompt(
    ctx: UniverseContext,
    history: list[ChatMessage],
    user_message: str,
    prompt_type: str,
) -> str:
    """Compose the full prompt sent to Granite for a chat turn.

    Structure:
        [System preamble]
        [Universe context via template]
        [Conversation history]
        [Current user message]
    """
    if prompt_type == "general":
        # General Q&A: inject context summary without a fixed task description.
        from app.ai.prompts.templates import _context_summary  # noqa: PLC2701

        universe_block = (
            f"UNIVERSE CONTEXT:\n{_context_summary(ctx)}\n\n"
            "Answer the user's question using the universe context above."
        )
    else:
        # Use the matching template, passing the user message as the question.
        universe_block = get_prompt(prompt_type, ctx, user_message)

    history_block = _format_history(history)
    current = f"\nUser: {user_message}\nAssistant:"

    parts = [_SYSTEM_PREAMBLE, "\n\n", universe_block]
    if history_block:
        parts.append(history_block)
    parts.append(current)
    return "".join(parts)


class ChatService:
    def __init__(self, session: AsyncSession, provider: AIProvider) -> None:
        self._repo = ChatRepository(session)
        self._builder = UniverseContextBuilder(session)
        self._provider = provider

    # ── Sessions ───────────────────────────────────────────────────────────────

    async def create_session(
        self, universe_id: str, title: str = "New Conversation"
    ) -> ChatSession:
        return await self._repo.create_session(universe_id, title)

    async def get_session(self, session_id: str) -> ChatSession | None:
        return await self._repo.get_session(session_id)

    async def list_sessions(
        self, universe_id: str, skip: int = 0, limit: int = 50
    ) -> tuple[list[ChatSession], int]:
        return await self._repo.list_sessions(universe_id, skip=skip, limit=limit)

    async def update_title(self, session_id: str, title: str) -> ChatSession | None:
        sess = await self._repo.get_session(session_id)
        if not sess:
            return None
        return await self._repo.update_session_title(sess, title)

    async def delete_session(self, session_id: str) -> bool:
        sess = await self._repo.get_session(session_id)
        if not sess:
            return False
        await self._repo.soft_delete_session(sess)
        return True

    # ── Streaming generation ───────────────────────────────────────────────────

    async def stream_message(
        self,
        session_id: str,
        user_content: str,
        prompt_type: str = "general",
    ) -> AsyncGenerator[str, None]:
        """Persist the user turn, stream the assistant reply, then persist it.

        Yields SSE-formatted token strings.  The final yield is a special
        ``[DONE]`` sentinel so the frontend knows streaming has ended.

        Raises ``ValueError`` if the session or universe is not found.
        """
        # 1. Validate session
        sess = await self._repo.get_session(session_id)
        if not sess:
            raise ValueError(f"Session not found: {session_id}")

        # 2. Validate prompt_type
        if prompt_type != "general" and prompt_type not in PROMPT_REGISTRY:
            raise ValueError(f"Unknown prompt type: {prompt_type}")

        # 3. Persist user message
        await self._repo.add_message(
            session_id=session_id,
            role="user",
            content=user_content,
            prompt_type=prompt_type,
        )

        # 4. Build universe context
        ctx = await self._builder.build(sess.universe_id)
        if ctx is None:
            raise ValueError(f"Universe not found: {sess.universe_id}")

        # 5. Load history (excluding the message we just stored)
        history = await self._repo.get_messages(session_id)
        prior_history = [
            m for m in history if not (m.role == "user" and m.content == user_content)
        ][-(_MAX_HISTORY_TURNS * 2) :]

        # 6. Build full prompt
        prompt = _build_chat_prompt(ctx, prior_history, user_content, prompt_type)
        logger.info(
            "Streaming chat session=%s prompt_type=%s prompt_len=%d",
            session_id,
            prompt_type,
            len(prompt),
        )

        # 7. Stream from provider, accumulate for persistence
        accumulated: list[str] = []
        try:
            async for token in self._provider.stream_generate(prompt):
                accumulated.append(token)
                yield token
        except Exception as exc:
            logger.exception("Streaming error for session=%s", session_id)
            error_msg = f"\n\n[Generation error: {exc}]"
            accumulated.append(error_msg)
            yield error_msg

        # 8. Persist completed assistant reply
        full_reply = "".join(accumulated)
        await self._repo.add_message(
            session_id=session_id,
            role="assistant",
            content=full_reply,
            prompt_type=prompt_type,
        )

        # 9. Auto-title first exchange
        if sess.title == "New Conversation" and len(prior_history) == 0:
            auto_title = user_content[:80].strip()
            if len(user_content) > 80:
                auto_title += "…"
            await self._repo.update_session_title(sess, auto_title)

        yield "[DONE]"
