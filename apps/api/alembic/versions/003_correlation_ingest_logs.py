"""Add correlation_ingest_logs journal table."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "003_correlation_ingest_logs"
down_revision = "002_relation_types"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("correlation_ingest_logs"):
        return
    op.create_table(
        "correlation_ingest_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(length=128), nullable=True),
        sa.Column("alerts", sa.JSON(), nullable=False),
        sa.Column("result", sa.JSON(), nullable=False),
        sa.Column("alert_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("resolved_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unresolved_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("chain_related", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_correlation_ingest_source", "correlation_ingest_logs", ["source"])
    op.create_index("ix_correlation_ingest_created", "correlation_ingest_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_correlation_ingest_created", table_name="correlation_ingest_logs")
    op.drop_index("ix_correlation_ingest_source", table_name="correlation_ingest_logs")
    op.drop_table("correlation_ingest_logs")
