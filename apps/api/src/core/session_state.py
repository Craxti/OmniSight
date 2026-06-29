"""Session commit policy helpers for request-scoped transactions."""

from __future__ import annotations

from sqlalchemy.orm import Session

DEFER_COMMIT_KEY = "defer_commit"


def set_defer_commit(session: Session, *, defer: bool = True) -> None:
    """When True, ``commit_or_rollback`` flushes only; caller commits once."""
    session.info[DEFER_COMMIT_KEY] = defer


def is_defer_commit(session: Session) -> bool:
    return bool(session.info.get(DEFER_COMMIT_KEY))
