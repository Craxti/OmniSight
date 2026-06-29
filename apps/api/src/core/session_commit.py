"""SQLAlchemy sync session commit helpers (scripts and test seed)."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import TypeVar

from sqlalchemy.orm import Session
from src.core.session_state import is_defer_commit

T = TypeVar("T")


def commit_session(db: Session) -> None:
    commit_or_rollback(db)


def commit_and_refresh(db: Session, entity: T) -> T:
    commit_or_rollback(db)
    db.refresh(entity)
    return entity


@contextmanager
def transaction(db: Session, *, commit: bool = True) -> Iterator[Session]:
    try:
        yield db
        if commit:
            db.commit()
    except Exception:
        db.rollback()
        raise


def commit_or_rollback(db: Session) -> None:
    try:
        if is_defer_commit(db):
            db.flush()
            return
        db.commit()
    except Exception:
        db.rollback()
        raise
