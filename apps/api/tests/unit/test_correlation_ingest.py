"""Correlation ingest orchestration tests."""

import pytest
from src.models import CI, CIType
from src.services.async_write.correlation import AsyncCorrelationWriteService
from src.services.rsm.indexed_ids import sync_search_indexes


def _server_with_hostname(db_session, name: str, hostname: str) -> CI:
    server_type = db_session.query(CIType).filter(CIType.name == "Server").first()
    ci = CI(
        name=name,
        type_id=server_type.id,
        status="active",
        external_ids={"hostname": hostname},
    )
    sync_search_indexes(ci)
    db_session.add(ci)
    db_session.flush()
    return ci


@pytest.mark.asyncio
async def test_ingest_correlation_resolves_alert(db_session, async_bundle):
    ci = _server_with_hostname(db_session, "ingest-srv", "ingest-host-01")
    db_session.commit()

    result = await AsyncCorrelationWriteService(async_bundle).ingest(
        [{"hostname": "ingest-host-01"}],
        source="test",
    )
    assert result.resolve.resolved
    assert result.resolve.resolved[0].resource is not None
    assert result.resolve.resolved[0].resource.id == ci.id


@pytest.mark.asyncio
async def test_correlation_context_response(db_session, async_bundle):
    ci = _server_with_hostname(db_session, "ctx-srv", "ctx-host-01")
    db_session.commit()

    result = await AsyncCorrelationWriteService(async_bundle).ingest(
        [{"hostname": "ctx-host-01"}],
        source="test",
        depth=1,
    )
    assert result.schema_version == "rsm-correlation-v1"
    assert ci.id in result.correlation.resource_ids
