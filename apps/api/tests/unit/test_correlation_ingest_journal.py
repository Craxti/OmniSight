"""Correlation ingest journal persistence tests."""

import pytest
from src.models import CI, CIType
from src.services.async_read.correlation import AsyncCorrelationReadService
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
async def test_ingest_persists_journal_entry(db_session, async_bundle):
    _server_with_hostname(db_session, "journal-srv", "journal-host-01")
    db_session.commit()

    result = await AsyncCorrelationWriteService(async_bundle).ingest(
        [{"hostname": "journal-host-01"}],
        source="demo-ce",
    )
    assert result.ingest_log_id is not None

    listed = await AsyncCorrelationReadService(async_bundle).list_ingest_logs()
    assert listed.stats.total_batches >= 1
    assert listed.stats.total_alerts >= 1
    assert listed.stats.resolve_rate_pct >= 0
    assert listed.total >= 1
    summary = next(item for item in listed.items if item.id == result.ingest_log_id)
    assert summary.source == "demo-ce"
    assert summary.alert_count == 1
    assert summary.resolved_count == 1
    assert summary.unresolved_count == 0

    detail = await AsyncCorrelationReadService(async_bundle).get_ingest_log(result.ingest_log_id)
    assert detail.alerts == [{"hostname": "journal-host-01"}]
    assert detail.result["schema_version"] == "rsm-correlation-v1"
    assert detail.result["resolve"]["resolved"]
