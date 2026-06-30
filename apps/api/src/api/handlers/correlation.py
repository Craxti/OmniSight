"""Correlation HTTP handlers (v1 envelopes)."""

from __future__ import annotations

from typing import Any

from src.api.handlers.v1_envelopes import (
    correlation_context_v1_envelope,
    correlation_ingest_log_detail_v1_envelope,
    correlation_ingest_log_list_v1_envelope,
    correlation_ingest_v1_envelope,
)
from src.services.async_read.correlation import AsyncCorrelationReadService
from src.services.async_write.correlation import AsyncCorrelationWriteService


async def handle_correlation_context(service: AsyncCorrelationReadService, resource_ids: list[int], depth: int):

    ctx = await service.build_context(resource_ids, depth=depth)

    return correlation_context_v1_envelope(ctx)


async def handle_correlation_ingest(
    service: AsyncCorrelationWriteService,
    alerts: list[dict[str, Any]],
    *,
    source: str | None = None,
    depth: int = 3,
    page: int = 1,
    page_size: int | None = None,
    webhook_url: str | None = None,
    dispatch_webhook: bool = False,
):

    result = await service.ingest(
        alerts,
        source=source,
        depth=depth,
        page=page,
        page_size=page_size,
        webhook_url=webhook_url,
        dispatch_webhook=dispatch_webhook,
    )

    return correlation_ingest_v1_envelope(result)


async def handle_correlation_ingest_log_list(
    service: AsyncCorrelationReadService,
    *,
    page: int = 1,
    page_size: int = 50,
    source: str | None = None,
):
    skip = (page - 1) * page_size
    result = await service.list_ingest_logs(source=source, skip=skip, limit=page_size)
    return correlation_ingest_log_list_v1_envelope(result, page=page, page_size=page_size)


async def handle_correlation_ingest_log_detail(service: AsyncCorrelationReadService, log_id: int):
    detail = await service.get_ingest_log(log_id)
    return correlation_ingest_log_detail_v1_envelope(detail)
