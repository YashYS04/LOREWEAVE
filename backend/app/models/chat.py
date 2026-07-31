from sqlalchemy import DateTime, ForeignKey, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import BaseEntity


class ChatSession(BaseEntity, Base):
    __tablename__ = "chat_sessions"
    universe_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("universes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(300), nullable=False, server_default="New Conversation"
    )
    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage", cascade="all, delete-orphan"
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # We define created_at manually because ChatMessage does not inherit BaseEntity in Alembic (only id, session_id, role, content, prompt_type, created_at)
    from datetime import datetime

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("(CURRENT_TIMESTAMP)"),
        nullable=False,
    )
