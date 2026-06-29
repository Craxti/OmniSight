"""Dedicated background worker entrypoint.

Usage:
    python -m src.worker

Runs auto-sync scheduler and webhook outbox retry consumer outside the API process.
"""

from __future__ import annotations

import asyncio
import logging

from src.core.background_tasks import run_background_loops
from src.core.config import settings
from src.core.logging_config import setup_logging

logger = logging.getLogger("omnisight.worker")


def main() -> None:
    setup_logging(settings)
    logger.info(
        "Starting OmniSight background worker",
        extra={
            "auto_sync": settings.auto_sync_scheduler_enabled,
            "outbox_interval": settings.outbox_poll_interval_seconds,
            "database_async": settings.database_async_enabled,
        },
    )
    asyncio.run(run_background_loops())


if __name__ == "__main__":
    main()
