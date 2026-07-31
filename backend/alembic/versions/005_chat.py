"""create chat_sessions and chat_messages tables

Revision ID: 005_chat
Revises: 004_world_building
Create Date: 2025-01-01 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "005_chat"
down_revision: str | None = "004_world_building"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column(
            "universe_id",
            sa.String(36),
            sa.ForeignKey("universes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "title", sa.String(300), nullable=False, server_default="New Conversation"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_chat_sessions_universe_id", "chat_sessions", ["universe_id"])

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column(
            "session_id",
            sa.String(36),
            sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("prompt_type", sa.String(50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
    )
    op.create_index("ix_chat_messages_session_id", "chat_messages", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_chat_messages_session_id", table_name="chat_messages")
    op.drop_table("chat_messages")
    op.drop_index("ix_chat_sessions_universe_id", table_name="chat_sessions")
    op.drop_table("chat_sessions")
