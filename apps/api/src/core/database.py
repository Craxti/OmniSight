"""Sync SQLAlchemy engine — scripts and schema bootstrap only.

All HTTP and worker runtime paths use ``core/database_async.py`` (asyncpg).
Use ``sync_session()`` in scripts instead of ``SessionLocal()`` directly.
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from src.core.config import settings

engine_kwargs: dict = {
    "pool_size": settings.database_pool_size,
    "max_overflow": settings.database_max_overflow,
    "pool_pre_ping": True,
    "connect_args": {"connect_timeout": 5},
}

engine = create_engine(settings.database_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def sync_session() -> Generator[Session, None, None]:
    """One-shot sync session for scripts and schema bootstrap."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
