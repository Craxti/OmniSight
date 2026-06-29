"""Unit tests for AsyncSearchService."""

import pytest
from sqlalchemy.orm import sessionmaker
from src.models import CI, CIType
from src.services.async_read.search import AsyncSearchService
from src.services.rsm.async_alert_search import find_cis_for_alert_async
from src.services.rsm.indexed_ids import sync_search_indexes


def _commit_ci(test_engine, **kwargs) -> CI:
    session = sessionmaker(bind=test_engine)()
    try:
        server_type = session.query(CIType).filter(CIType.name == "Server").first()
        ci = CI(type_id=server_type.id, status="active", **kwargs)
        sync_search_indexes(ci)
        session.add(ci)
        session.commit()
        session.refresh(ci)
        return ci
    finally:
        session.close()


@pytest.mark.asyncio
async def test_resource_search_finds_ci_by_name(test_engine, async_bundle):
    _commit_ci(test_engine, name="searchable-host")

    result = await AsyncSearchService(async_bundle).resource_search(q="searchable", limit=10)
    assert result.total >= 1
    assert any(item.name == "searchable-host" for item in result.items)


@pytest.mark.asyncio
async def test_find_cis_for_alert_by_hostname(test_engine, async_bundle):
    _commit_ci(
        test_engine,
        name="alert-host",
        external_ids={"hostname": "pay-srv-01"},
    )

    matches = await find_cis_for_alert_async({"hostname": "pay-srv-01"}, ci_repo=async_bundle.ci)
    assert len(matches) == 1
    assert matches[0].name == "alert-host"


@pytest.mark.asyncio
async def test_resource_search_returns_results(test_engine, async_bundle):
    _commit_ci(test_engine, name="resource-find-me", owner="ops")

    result = await AsyncSearchService(async_bundle).resource_search(q="resource-find", limit=10)
    assert result.total >= 1
    assert any(item.name == "resource-find-me" for item in result.items)
