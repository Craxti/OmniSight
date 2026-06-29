"""Baseline schema from current SQLAlchemy models."""

from __future__ import annotations

from alembic import op

import src.models  # noqa: F401 — register metadata
from src.models.base import Base

revision = "001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind)
