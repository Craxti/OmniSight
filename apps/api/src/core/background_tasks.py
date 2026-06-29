"""Background task orchestration: outbox consumer, auto-sync scheduler."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from src.core.config import settings
from src.core.scheduler import auto_sync_scheduler
from src.core.worker_db import database_ready_for_worker, run_worker_async, shutdown_worker_db
from src.services.integrations.async_outbox_consumer import run_outbox_batch_async

logger = logging.getLogger("omnisight.worker")


async def outbox_consumer_loop() -> None:
    interval = max(5, settings.outbox_poll_interval_seconds)
    while True:
        await asyncio.sleep(interval)
        if not await database_ready_for_worker():
            continue
        try:
            processed = await run_worker_async(run_outbox_batch_async)
            if processed:
                logger.info("outbox_batch_processed", extra={"count": processed})
        except Exception:
            logger.exception("outbox_batch_failed")


def start_outbox_consumer() -> asyncio.Task:
    return asyncio.create_task(outbox_consumer_loop())


async def stop_outbox_consumer(task: asyncio.Task | None) -> None:
    if not task:
        return
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


async def run_background_loops() -> None:
    """Run until cancelled — used by dedicated worker process."""
    tasks: list[asyncio.Task[Any]] = []
    if settings.auto_sync_scheduler_enabled:
        tasks.append(asyncio.create_task(auto_sync_scheduler()))
    tasks.append(start_outbox_consumer())
    try:
        await asyncio.gather(*tasks)
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await shutdown_worker_db()


def start_api_background_tasks() -> list[asyncio.Task[Any]]:
    """Start in-process loops when API owns background work."""
    if not settings.background_tasks_enabled:
        return []
    tasks: list[asyncio.Task[Any]] = []
    if settings.auto_sync_scheduler_enabled:
        tasks.append(asyncio.create_task(auto_sync_scheduler()))
    tasks.append(start_outbox_consumer())
    return tasks


async def stop_api_background_tasks(tasks: list[asyncio.Task[Any]]) -> None:
    for task in tasks:
        task.cancel()
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
    await shutdown_worker_db()
