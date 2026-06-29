"""Async SQLAlchemy engines for API database access.

When ``DATABASE_ASYNC_ENABLED=true`` (default), reads and mutations use native async ORM
on dedicated read/write pools.
"""

from __future__ import annotations

from collections.abc import Callable
from contextlib import asynccontextmanager
from typing import TypeVar

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session
from src.core.config import settings
from src.core.session_state import set_defer_commit

T = TypeVar("T")

_read_async_engine: AsyncEngine | None = None
_write_async_engine: AsyncEngine | None = None
_AsyncReadSessionLocal: async_sessionmaker[AsyncSession] | None = None
_AsyncWriteSessionLocal: async_sessionmaker[AsyncSession] | None = None


_pg_connect_args = {
    "server_settings": {
        "lock_timeout": "3000",
        "statement_timeout": "15000",
    }
}


def _to_async_url(url: str) -> str:
    if url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def async_engine_enabled() -> bool:
    return settings.database_async_enabled


def get_async_read_engine() -> AsyncEngine:
    global _read_async_engine, _AsyncReadSessionLocal
    if _read_async_engine is None:
        read_url = settings.database_read_url.strip() or settings.database_url
        _read_async_engine = create_async_engine(
            _to_async_url(read_url),
            pool_pre_ping=True,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            connect_args=_pg_connect_args,
        )
        _AsyncReadSessionLocal = async_sessionmaker(_read_async_engine, expire_on_commit=False)
    return _read_async_engine


def get_async_write_engine() -> AsyncEngine:
    global _write_async_engine, _AsyncWriteSessionLocal
    if _write_async_engine is None:
        _write_async_engine = create_async_engine(
            _to_async_url(settings.database_url),
            pool_pre_ping=True,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            connect_args=_pg_connect_args,
        )
        _AsyncWriteSessionLocal = async_sessionmaker(_write_async_engine, expire_on_commit=False)
    return _write_async_engine


@asynccontextmanager
async def async_read_session():
    """Dedicated async read session for native ``await session.execute`` paths."""
    get_async_read_engine()
    assert _AsyncReadSessionLocal is not None
    async with _AsyncReadSessionLocal() as session:
        yield session


@asynccontextmanager
async def async_write_session():
    """Dedicated async write session (mutations via ``run_sync`` on write pool)."""
    get_async_write_engine()
    assert _AsyncWriteSessionLocal is not None
    async with _AsyncWriteSessionLocal() as session:
        yield session


@asynccontextmanager
async def async_transactional_write_session():
    """Async write session with deferred commit (mapped import / autodiscover apply)."""
    get_async_write_engine()
    assert _AsyncWriteSessionLocal is not None
    async with _AsyncWriteSessionLocal() as session:

        def _enable_defer(sync_session: Session) -> None:
            set_defer_commit(sync_session, defer=True)

        await session.run_sync(_enable_defer)
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:

            def _disable_defer(sync_session: Session) -> None:
                set_defer_commit(sync_session, defer=False)

            await session.run_sync(_disable_defer)


async def run_sync_on_write_session(work: Callable[[Session], T]) -> T:
    """Run blocking ORM code on the async write pool (legacy scripts / defer_commit hooks)."""
    get_async_write_engine()
    assert _AsyncWriteSessionLocal is not None
    async with _AsyncWriteSessionLocal() as async_session:
        return await async_session.run_sync(work)


async def database_ready_async() -> bool:
    if not async_engine_enabled():
        return False
    try:
        engine = get_async_write_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def dispose_async_engines() -> None:
    global _read_async_engine, _write_async_engine, _AsyncReadSessionLocal, _AsyncWriteSessionLocal
    if _read_async_engine is not None:
        await _read_async_engine.dispose()
    if _write_async_engine is not None:
        await _write_async_engine.dispose()
    _read_async_engine = None
    _write_async_engine = None
    _AsyncReadSessionLocal = None
    _AsyncWriteSessionLocal = None
