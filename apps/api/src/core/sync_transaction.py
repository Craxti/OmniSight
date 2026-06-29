"""Legacy sync transactional session helper (tests and bridged import paths only)."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.core.session_state import set_defer_commit


def get_transactional_db() -> Generator[Session, None, None]:
    """Defer per-mutation commits; commit once when the request handler succeeds."""
    db = SessionLocal()
    set_defer_commit(db, defer=True)
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        set_defer_commit(db, defer=False)
        db.close()
