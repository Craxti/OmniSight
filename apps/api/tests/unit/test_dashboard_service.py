"""Unit tests for DashboardService."""

import pytest
from src.models import CI, CIType
from src.services.async_read.dashboard import AsyncDashboardService


@pytest.mark.asyncio
async def test_dashboard_overview_returns_counts(db_session, async_bundle):
    server_type = db_session.query(CIType).filter(CIType.name == "Server").first()
    db_session.add(CI(name="dash-ci", type_id=server_type.id, status="active"))
    db_session.commit()

    overview = await AsyncDashboardService(async_bundle).overview()

    assert overview.total_ci >= 1
    assert overview.total_relations >= 0
    assert "active" in overview.by_status
    assert overview.model_health.valid is True
