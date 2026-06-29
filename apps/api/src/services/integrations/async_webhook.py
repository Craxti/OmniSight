"""Native async webhook outbox helpers."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import settings
from src.models import IntegrationOutbox
from src.services.integrations.webhook_delivery import deliver_webhook


async def enqueue_outbox_async(
    session: AsyncSession,
    event_type: str,
    payload: dict[str, Any],
    target_url: str,
) -> IntegrationOutbox:
    row = IntegrationOutbox(
        event_type=event_type,
        target_url=target_url,
        payload=payload,
        status="pending",
    )
    session.add(row)
    await session.flush()
    return row


async def process_outbox_row_async(row: IntegrationOutbox) -> bool:
    ok = await asyncio.to_thread(
        deliver_webhook,
        row.target_url,
        row.payload,
        settings.webhook_secret,
    )
    row.status = "delivered" if ok else "failed"
    row.attempts += 1
    return ok


async def dispatch_correlation_webhook_async(
    session: AsyncSession,
    payload: dict[str, Any],
    webhook_url: str | None = None,
) -> dict[str, Any]:
    url = webhook_url or settings.webhook_url
    if not url:
        return {"queued": False, "delivered": False}
    row = await enqueue_outbox_async(session, "correlation.ingest", payload, url)
    delivered = False
    if settings.webhook_sync_delivery:
        delivered = await process_outbox_row_async(row)
        if delivered:
            row.delivered_at = datetime.now(UTC).replace(tzinfo=None)
    await session.commit()
    return {"queued": True, "delivered": delivered, "outbox_id": row.id}
