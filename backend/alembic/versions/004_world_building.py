"""create locations, organizations, objects, world_rules tables

Revision ID: 004_world_building
Revises: 003_characters
Create Date: 2025-01-01 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "004_world_building"
down_revision: str | None = "003_characters"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TIMESTAMP_COLS = [
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
]


def _universe_fk() -> sa.Column:
    return sa.Column(
        "universe_id",
        sa.String(36),
        sa.ForeignKey("universes.id", ondelete="CASCADE"),
        nullable=False,
    )


def upgrade() -> None:
    # ── locations ────────────────────────────────────────────────────────────────
    op.create_table(
        "locations",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        _universe_fk(),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("type", sa.String(100), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("climate", sa.String(200), nullable=True),
        sa.Column("culture", sa.Text, nullable=True),
        sa.Column("population", sa.String(200), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        *_TIMESTAMP_COLS,
    )
    op.create_index("ix_locations_universe_id", "locations", ["universe_id"])

    # ── organizations ─────────────────────────────────────────────────────────────
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        _universe_fk(),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("type", sa.String(100), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("leader", sa.String(200), nullable=True),
        sa.Column("purpose", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        *_TIMESTAMP_COLS,
    )
    op.create_index("ix_organizations_universe_id", "organizations", ["universe_id"])

    # ── objects ───────────────────────────────────────────────────────────────────
    op.create_table(
        "objects",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        _universe_fk(),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("origin", sa.Text, nullable=True),
        sa.Column("owner", sa.String(200), nullable=True),
        sa.Column("abilities", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        *_TIMESTAMP_COLS,
    )
    op.create_index("ix_objects_universe_id", "objects", ["universe_id"])

    # ── world_rules ───────────────────────────────────────────────────────────────
    op.create_table(
        "world_rules",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        _universe_fk(),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("limitations", sa.Text, nullable=True),
        sa.Column("exceptions", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        *_TIMESTAMP_COLS,
    )
    op.create_index("ix_world_rules_universe_id", "world_rules", ["universe_id"])


def downgrade() -> None:
    op.drop_index("ix_world_rules_universe_id", table_name="world_rules")
    op.drop_table("world_rules")
    op.drop_index("ix_objects_universe_id", table_name="objects")
    op.drop_table("objects")
    op.drop_index("ix_organizations_universe_id", table_name="organizations")
    op.drop_table("organizations")
    op.drop_index("ix_locations_universe_id", table_name="locations")
    op.drop_table("locations")
