"""Global search HTTP handlers (v1 envelopes)."""

from __future__ import annotations

from typing import Any

from src.api.handlers.v1_envelopes import resource_search_v1_envelope
from src.services.async_read.search import AsyncSearchService


async def handle_resource_search(service: AsyncSearchService, **filters: Any):
    result = await service.resource_search(**filters)
    return resource_search_v1_envelope(result)
