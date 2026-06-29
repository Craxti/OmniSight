"""Native async retry consumer for integration webhook outbox."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import settings
from src.repositories.async_orm.outbox_repository import AsyncOutboxRepository
from src.services.integrations.async_webhook import process_outbox_row_async


async def run_outbox_batch_async(session: AsyncSession) -> int:
    repo = AsyncOutboxRepository(session)
    rows = await repo.fetch_retryable(
        limit=settings.outbox_batch_size,
        max_attempts=settings.outbox_max_attempts,
    )
    processed = 0
    for row in rows:
        ok = await process_outbox_row_async(row)
        if ok:
            row.delivered_at = datetime.now(UTC).replace(tzinfo=None)
        processed += 1
    if rows:
        await session.commit()
    return processed
