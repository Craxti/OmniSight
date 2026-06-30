"""Unit tests for model health metrics."""

import pytest
from src.models import CI, CIType
from src.services.rsm.indexed_ids import sync_search_indexes
from src.services.rsm.model_health import compute_model_health


@pytest.mark.asyncio
async def test_model_health_reports_orphan_and_missing_external_id(db_session, async_bundle):
    server_type = db_session.query(CIType).filter(CIType.name == "Server").first()
    orphan = CI(name="orphan-srv", type_id=server_type.id, status="active")
    with_id = CI(
        name="with-host",
        type_id=server_type.id,
        status="active",
        external_ids={"hostname": "host-01"},
        criticality="critical",
    )
    sync_search_indexes(with_id)
    db_session.add_all([orphan, with_id])
    db_session.commit()

    health = await compute_model_health(
        ci_repo=async_bundle.ci,
        rel_repo=async_bundle.relations,
        relation_valid=True,
        relation_issue_count=0,
    )

    warning_types = {warning.type for warning in health.warnings}
    assert "orphan_ci" in warning_types
    assert "no_external_id" in warning_types
    assert "critical_no_owner" in warning_types
    assert health.external_id_coverage_pct < 100.0
    assert health.correlation_ready is False


@pytest.mark.asyncio
async def test_model_health_duplicate_external_id(db_session, async_bundle):
    server_type = db_session.query(CIType).filter(CIType.name == "Server").first()
    first = CI(
        name="dup-a",
        type_id=server_type.id,
        status="active",
        external_ids={"hostname": "dup-host"},
    )
    second = CI(
        name="dup-b",
        type_id=server_type.id,
        status="active",
        external_ids={"hostname": "dup-host"},
    )
    sync_search_indexes(first)
    sync_search_indexes(second)
    db_session.add_all([first, second])
    db_session.commit()

    health = await compute_model_health(
        ci_repo=async_bundle.ci,
        rel_repo=async_bundle.relations,
        relation_valid=True,
        relation_issue_count=0,
    )

    assert any(warning.type == "duplicate_external_id" for warning in health.warnings)
