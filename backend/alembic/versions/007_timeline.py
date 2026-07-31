"""create timeline_events and timeline_participants tables

Revision ID: 007_timeline
Revises: 006_relationships
Create Date: 2025-01-01 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "007_timeline"
down_revision: str | None = "006_relationships"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "timeline_events",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column(
            "universe_id",
            sa.String(36),
            sa.ForeignKey("universes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("event_type", sa.String(50), nullable=False, server_default="custom"),
        sa.Column("status", sa.String(20), nullable=False, server_default="completed"),
        sa.Column("start_date", sa.String(100), nullable=True),
        sa.Column("end_date", sa.String(100), nullable=True),
        sa.Column("importance", sa.Integer, nullable=True),
        sa.Column("metadata_json", sa.Text, nullable=True),
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
    op.create_index(
        "ix_timeline_events_universe_id", "timeline_events", ["universe_id"]
    )
    op.create_index("ix_timeline_events_event_type", "timeline_events", ["event_type"])
    op.create_index("ix_timeline_events_start_date", "timeline_events", ["start_date"])

    op.create_table(
        "timeline_participants",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column(
            "event_id",
            sa.String(36),
            sa.ForeignKey("timeline_events.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("role", sa.String(200), nullable=True),
    )
    op.create_index(
        "ix_timeline_participants_event_id", "timeline_participants", ["event_id"]
    )
    op.create_index(
        "ix_timeline_participants_entity_id", "timeline_participants", ["entity_id"]
    )


def downgrade() -> None:
    op.drop_index(
        "ix_timeline_participants_entity_id", table_name="timeline_participants"
    )
    op.drop_index(
        "ix_timeline_participants_event_id", table_name="timeline_participants"
    )
    op.drop_table("timeline_participants")
    op.drop_index("ix_timeline_events_start_date", table_name="timeline_events")
    op.drop_index("ix_timeline_events_event_type", table_name="timeline_events")
    op.drop_index("ix_timeline_events_universe_id", table_name="timeline_events")
    op.drop_table("timeline_events")
