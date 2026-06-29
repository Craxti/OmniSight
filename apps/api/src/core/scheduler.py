"""Background auto-sync scheduler for autodiscover connectors."""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import settings
from src.core.database_async import async_write_session, get_async_write_engine
from src.core.worker_db import database_ready_for_worker
from src.repositories.async_orm.user_repository import AsyncUserRepository

logger = logging.getLogger("omnisight.api")

# Stable advisory lock id for single-leader auto-sync across workers.
_AUTO_SYNC_LOCK_KEY = 0x4F4D4E49  # "OMNI"


def _postgres_scheduler_locks() -> bool:
    return get_async_write_engine().dialect.name == "postgresql"


async def _try_acquire_scheduler_lock(session: AsyncSession) -> bool:
    if not _postgres_scheduler_locks():
        return True
    result = await session.execute(
        text("SELECT pg_try_advisory_lock(:lock_key)"),
        {"lock_key": _AUTO_SYNC_LOCK_KEY},
    )
    return bool(result.scalar())


async def _release_scheduler_lock(session: AsyncSession) -> None:
    if not _postgres_scheduler_locks():
        return
    await session.execute(
        text("SELECT pg_advisory_unlock(:lock_key)"),
        {"lock_key": _AUTO_SYNC_LOCK_KEY},
    )


async def _run_auto_sync_batch() -> None:
    from src.services.autodiscover.runtime.auto_sync import run_scheduled_auto_sync_async

    async with async_write_session() as session:
        if not await _try_acquire_scheduler_lock(session):
            logger.debug("auto_sync skipped: another worker holds the scheduler lock")
            return
        try:
            user = await AsyncUserRepository(session).get_by_email(settings.integration_user_email)
            if not user:
                logger.warning("auto_sync skipped: integration user not found")
                return
        finally:
            await _release_scheduler_lock(session)

    # Network-heavy sync runs outside the lock and without holding a pooled connection.
    await run_scheduled_auto_sync_async(user_email=settings.integration_user_email)


async def auto_sync_scheduler() -> None:
    if not settings.background_tasks_enabled:
        return
    interval = max(60, settings.auto_sync_interval_seconds)
    while True:
        await asyncio.sleep(interval)
        if not settings.auto_sync_scheduler_enabled:
            continue
        if not await database_ready_for_worker():
            continue
        try:
            await _run_auto_sync_batch()
        except Exception:
            logger.exception("auto_sync batch failed")


def start_auto_sync_scheduler() -> asyncio.Task | None:
    if not settings.auto_sync_scheduler_enabled or not settings.background_tasks_enabled:
        return None
    return asyncio.create_task(auto_sync_scheduler())


async def stop_auto_sync_scheduler(task: asyncio.Task | None) -> None:
    if not task:
        return
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
