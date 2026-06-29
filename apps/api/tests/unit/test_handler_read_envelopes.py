"""Handler envelope tests for read routes (dashboard + topology)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from src.api.handlers.dashboard import handle_dashboard_overview
from src.api.handlers.topology import handle_resource_graph
from src.schemas.correlation import GraphNodeResponse
from src.schemas.resources import DashboardOverviewResponse, ResourceGraphResponse


@pytest.mark.asyncio
async def test_handle_dashboard_overview_v1_envelope():
    service = MagicMock()
    service.overview = AsyncMock(
        return_value=DashboardOverviewResponse(
            total_ci=2,
            total_relations=1,
            by_status={"active": 2},
            by_type={"Server": 2},
            model_health={"valid": True, "issue_count": 0},
            recent_audit=[],
        )
    )

    body = await handle_dashboard_overview(service)
    assert body["api_version"] == "v1"
    assert body["dashboard"]["total_ci"] == 2


@pytest.mark.asyncio
async def test_handle_resource_graph_v1_envelope():
    service = MagicMock()
    service.graph = AsyncMock(
        return_value=ResourceGraphResponse(
            root_id=1,
            depth=2,
            nodes=[GraphNodeResponse(id=1, name="n1", type_id=1, type="Server", status="active", depth=0)],
            edges=[],
        )
    )

    body = await handle_resource_graph(service, resource_id=1, depth=2)
    assert body["api_version"] == "v1"
    assert body["graph"]["root_id"] == 1
    service.graph.assert_awaited_once_with(1, depth=2)
