"""Dashboard HTTP handlers (v1 envelopes)."""

from __future__ import annotations

from src.api.handlers.v1_envelopes import dashboard_v1_envelope
from src.services.async_read.dashboard import AsyncDashboardService


async def handle_dashboard_overview(service: AsyncDashboardService):
    result = await service.overview()
    return dashboard_v1_envelope(result)
