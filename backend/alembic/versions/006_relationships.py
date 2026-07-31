"""create relationships table

Revision ID: 006_relationships
Revises: 005_chat
Create Date: 2025-01-01 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "006_relationships"
down_revision: str | None = "005_chat"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "relationships",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column(
            "universe_id",
            sa.String(36),
            sa.ForeignKey("universes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Source entity
        sa.Column("source_entity_type", sa.String(50), nullable=False),
        sa.Column("source_entity_id", sa.String(36), nullable=False),
        # Target entity
        sa.Column("target_entity_type", sa.String(50), nullable=False),
        sa.Column("target_entity_id", sa.String(36), nullable=False),
        # Semantics
        sa.Column("relationship_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(300), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("strength", sa.Integer, nullable=True),
        sa.Column(
            "direction",
            sa.String(20),
            nullable=False,
            server_default="unidirectional",
        ),
        sa.Column("metadata_json", sa.Text, nullable=True),
        # Audit timestamps (BaseEntity)
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
    op.create_index("ix_relationships_universe_id", "relationships", ["universe_id"])
    op.create_index(
        "ix_relationships_source_entity_id", "relationships", ["source_entity_id"]
    )
    op.create_index(
        "ix_relationships_target_entity_id", "relationships", ["target_entity_id"]
    )
    op.create_index(
        "ix_relationships_relationship_type", "relationships", ["relationship_type"]
    )


def downgrade() -> None:
    op.drop_index("ix_relationships_relationship_type", table_name="relationships")
    op.drop_index("ix_relationships_target_entity_id", table_name="relationships")
    op.drop_index("ix_relationships_source_entity_id", table_name="relationships")
    op.drop_index("ix_relationships_universe_id", table_name="relationships")
    op.drop_table("relationships")
