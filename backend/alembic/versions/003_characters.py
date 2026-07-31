"""create characters table

Revision ID: 003_characters
Revises: 002_soft_delete
Create Date: 2025-01-01 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "003_characters"
down_revision: str | None = "002_soft_delete"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "characters",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column(
            "universe_id",
            sa.String(36),
            sa.ForeignKey("universes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("role", sa.String(200), nullable=True),
        sa.Column("age", sa.String(50), nullable=True),
        sa.Column("gender", sa.String(100), nullable=True),
        sa.Column("occupation", sa.String(200), nullable=True),
        sa.Column("biography", sa.Text, nullable=True),
        sa.Column("personality", sa.Text, nullable=True),
        sa.Column("goals", sa.Text, nullable=True),
        sa.Column("motivations", sa.Text, nullable=True),
        sa.Column("strengths", sa.Text, nullable=True),
        sa.Column("weaknesses", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
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
    op.create_index("ix_characters_universe_id", "characters", ["universe_id"])


def downgrade() -> None:
    op.drop_index("ix_characters_universe_id", table_name="characters")
    op.drop_table("characters")
