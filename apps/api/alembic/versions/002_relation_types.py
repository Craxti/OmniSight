"""Add relation_types catalog table."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "002_relation_types"
down_revision = "001_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("relation_types"):
        return
    op.create_table(
        "relation_types",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_official", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_relation_types_name", "relation_types", ["name"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_relation_types_name", table_name="relation_types")
    op.drop_table("relation_types")
