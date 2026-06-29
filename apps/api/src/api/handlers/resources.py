"""Correlation resolve HTTP handlers (v1 envelopes)."""

from __future__ import annotations

from typing import Any

from src.api.handlers.v1_envelopes import resolve_v1_envelope
from src.services.async_read.correlation import AsyncCorrelationReadService


async def handle_resolve_batch(
    service: AsyncCorrelationReadService,
    alerts: list[dict[str, Any]],
    *,
    page: int = 1,
    page_size: int | None = None,
):
    payload = await service.resolve_batch(alerts, page=page, page_size=page_size)
    return resolve_v1_envelope(payload)
