"""Audit HTTP handlers (v1 envelopes)."""

from __future__ import annotations

from typing import Any

from src.api.handlers.v1_envelopes import audit_items_v1_envelope, audit_list_v1_envelope
from src.services.async_read.audit import AsyncAuditReadService


async def handle_audit_list(
    service: AsyncAuditReadService,
    *,
    page: int = 1,
    page_size: int = 50,
    **filters: Any,
):
    effective_skip = (page - 1) * page_size
    effective_limit = page_size
    result = await service.list_logs(skip=effective_skip, limit=effective_limit, **filters)
    return audit_list_v1_envelope(result, page=page, page_size=page_size)


async def handle_entity_audit(service: AsyncAuditReadService, entity_type: str, entity_id: int):
    items = await service.entity_history(entity_type, entity_id)
    return audit_items_v1_envelope(items)
