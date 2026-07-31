"""Chat repository — CRUD for ChatSession and ChatMessage."""

import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat import ChatMessage, ChatSession

logger = logging.getLogger(__name__)

_ACTIVE_SESSION = ChatSession.deleted_at.is_(None)


class ChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── ChatSession ────────────────────────────────────────────────────────────

    async def create_session(self, universe_id: str, title: str) -> ChatSession:
        sess = ChatSession(
            id=str(uuid.uuid4()),
            universe_id=universe_id,
            title=title,
        )
        self._session.add(sess)
        await self._session.commit()
        logger.info("Created chat session id=%s universe=%s", sess.id, universe_id)
        # We query the session again to eager load messages.
        stmt = select(ChatSession).options(selectinload(ChatSession.messages)).where(ChatSession.id == sess.id)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_session(self, session_id: str) -> ChatSession | None:
        result = await self._session.execute(
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .where(ChatSession.id == session_id, _ACTIVE_SESSION)
        )
        return result.scalar_one_or_none()

    async def list_sessions(
        self, universe_id: str, skip: int = 0, limit: int = 50
    ) -> tuple[list[ChatSession], int]:
        rows = await self._session.execute(
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .where(ChatSession.universe_id == universe_id, _ACTIVE_SESSION)
            .order_by(ChatSession.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        sessions = list(rows.scalars().all())
        total_result = await self._session.execute(
            select(func.count(ChatSession.id)).where(
                ChatSession.universe_id == universe_id, _ACTIVE_SESSION
            )
        )
        return sessions, total_result.scalar_one() or 0

    async def update_session_title(self, session: ChatSession, title: str) -> ChatSession:
        session.title = title
        await self._session.commit()
        await self._session.refresh(session, ["updated_at"])
        return session

    async def soft_delete_session(self, session: ChatSession) -> None:
        session.deleted_at = datetime.now(tz=UTC)
        await self._session.commit()
        logger.info("Soft-deleted chat session id=%s", session.id)

    # ── ChatMessage ────────────────────────────────────────────────────────────

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        prompt_type: str | None = None,
    ) -> ChatMessage:
        msg = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=role,
            content=content,
            prompt_type=prompt_type,
        )
        self._session.add(msg)
        await self._session.commit()
        await self._session.refresh(msg)
        return msg

    async def get_messages(self, session_id: str) -> list[ChatMessage]:
        result = await self._session.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
        )
        return list(result.scalars().all())
