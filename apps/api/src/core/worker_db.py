"""Database helpers for the background worker (async write pool)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TypeVar

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import engine
from src.core.database_async import async_write_session, database_ready_async, dispose_async_engines

T = TypeVar("T")


def database_ready_sync() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def database_ready_for_worker() -> bool:
    return await database_ready_async()


async def run_worker_async(work: Callable[[AsyncSession], Awaitable[T]]) -> T:
    """Execute native async ORM batch work on the async write pool."""
    async with async_write_session() as session:
        return await work(session)


async def shutdown_worker_db() -> None:
    await dispose_async_engines()
