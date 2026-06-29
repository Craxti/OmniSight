"""Unit tests for autodiscover apply pipeline."""

from __future__ import annotations

import uuid

import pytest
from src.models import CI, AutodiscoverMapping, AutodiscoverRun, CIType
from src.services.autodiscover.runtime.apply_run import AsyncAutodiscoverApplyService


def _mapping_id() -> str:
    return uuid.uuid4().hex


def _server_ci(db_session) -> CI:
    server_type = db_session.query(CIType).filter(CIType.name == "Server").first()
    ci = CI(
        name="apply-test-srv",
        type_id=server_type.id,
        status="active",
        owner="qa",
        environment="test",
        criticality="low",
        external_ids={"ip": "10.0.0.1"},
    )
    db_session.add(ci)
    db_session.commit()
    db_session.refresh(ci)
    return ci


@pytest.mark.asyncio
async def test_apply_run_mappings_updates_ci_field(db_session, admin_user, async_bundle):
    ci = _server_ci(db_session)

    run = AutodiscoverRun(status="draft", user_email=admin_user.email, request_snapshot={}, report={})
    db_session.add(run)
    db_session.flush()

    row = AutodiscoverMapping(
        run_id=run.id,
        mapping_id=_mapping_id(),
        mapping_kind="field",
        ci_id=ci.id,
        ci_name=ci.name,
        field="ip",
        discovered_value="10.99.0.1",
        current_value="10.0.0.1",
        status="needs_confirmation",
        selected=True,
    )
    db_session.add(row)
    db_session.commit()

    result = await AsyncAutodiscoverApplyService(async_bundle).apply_run(run_id=run.id, user=admin_user)
    await async_bundle.session.commit()

    db_session.refresh(ci)
    db_session.refresh(run)
    assert result.applied == 1
    assert result.skipped == 0
    assert ci.external_ids.get("ip") == "10.99.0.1"
    assert run.status == "completed"
    assert row.applied_at is not None


@pytest.mark.asyncio
async def test_apply_run_mappings_skips_unchanged_value(db_session, admin_user, async_bundle):
    ci = _server_ci(db_session)
    current_ip = ci.external_ids["ip"]

    run = AutodiscoverRun(status="draft", user_email=admin_user.email, request_snapshot={}, report={})
    db_session.add(run)
    db_session.flush()

    row = AutodiscoverMapping(
        run_id=run.id,
        mapping_id=_mapping_id(),
        mapping_kind="field",
        ci_id=ci.id,
        ci_name=ci.name,
        field="ip",
        discovered_value=current_ip,
        current_value=current_ip,
        status="auto",
        selected=True,
    )
    db_session.add(row)
    db_session.commit()

    result = await AsyncAutodiscoverApplyService(async_bundle).apply_run(
        run_id=run.id,
        user=admin_user,
        apply_auto_only=True,
    )
    await async_bundle.session.commit()

    assert result.applied == 0
    assert result.skipped == 1
