"""RSM search helper tests."""

import pytest
from src.models import CI, CIType
from src.services.rsm.async_alert_search import find_cis_for_alert_async
from src.services.rsm.search import _ci_matches_alert, _extract_alert_lookup_fields


def test_extract_alert_lookup_fields_normalizes_keys():
    fields = _extract_alert_lookup_fields(
        {
            "cmdbId": 42,
            "hostname": "app-01",
            "ip": "10.0.0.1",
            "externalId": "ext-1",
            "serviceCode": "SVC",
            "applicationCode": "APP",
        }
    )
    assert fields["cmdb_id"] == 42
    assert fields["hostname"] == "app-01"
    assert fields["service_code"] == "SVC"


def test_ci_matches_alert_uses_extracted_fields(db_session):
    server_type = db_session.query(CIType).filter(CIType.name == "Server").first()
    ci = CI(
        name="alert-host",
        type_id=server_type.id,
        status="active",
        search_hostname="app-01",
        external_ids={"hostname": "app-01"},
    )
    assert _ci_matches_alert(ci, {"hostname": "app-01"}) is True
    assert _ci_matches_alert(ci, {"cmdbId": str(ci.id)}) is True
    assert _ci_matches_alert(ci, {"hostname": "other"}) is False


@pytest.mark.asyncio
async def test_find_cis_for_alert_skips_invalid_cmdb_id(db_session, async_bundle):
    server_type = db_session.query(CIType).filter(CIType.name == "Server").first()
    ci = CI(
        name="svc-only",
        type_id=server_type.id,
        status="active",
        search_service_code="PAY",
        external_ids={"serviceCode": "PAY"},
    )
    db_session.add(ci)
    db_session.commit()

    found = await find_cis_for_alert_async(
        {"cmdbId": "not-a-number", "serviceCode": "PAY"},
        ci_repo=async_bundle.ci,
    )
    assert any(c.id == ci.id for c in found)


def test_ci_matches_alert_service_and_application_pair(db_session):
    server_type = db_session.query(CIType).filter(CIType.name == "Server").first()
    ci = CI(
        name="pair-host",
        type_id=server_type.id,
        status="active",
        external_ids={"serviceCode": "PAY", "applicationCode": "APP"},
    )
    assert _ci_matches_alert(ci, {"serviceCode": "PAY", "applicationCode": "APP"}) is True
    assert _ci_matches_alert(ci, {"serviceCode": "PAY", "applicationCode": "OTHER"}) is False
    assert _ci_matches_alert(ci, {"serviceCode": "PAY"}) is True


@pytest.mark.asyncio
async def test_search_cis_delegates_to_repository(db_session, async_bundle):
    server_type = db_session.query(CIType).filter(CIType.name == "Server").first()
    db_session.add(CI(name="backfill-host", type_id=server_type.id, status="active"))
    db_session.commit()

    items, total = await async_bundle.ci.search(q="backfill-host", limit=10)
    assert total >= 0
    assert isinstance(items, list)


@pytest.mark.asyncio
async def test_find_cis_for_alert_by_external_id(db_session, async_bundle):
    server_type = db_session.query(CIType).filter(CIType.name == "Server").first()
    ci = CI(
        name="ext-host",
        type_id=server_type.id,
        status="active",
        search_external_id="ext-42",
        external_ids={"externalId": "ext-42"},
    )
    db_session.add(ci)
    db_session.commit()
    found = await find_cis_for_alert_async({"externalId": "ext-42"}, ci_repo=async_bundle.ci)
    assert any(c.id == ci.id for c in found)


@pytest.mark.asyncio
async def test_find_cis_for_alert_by_ip(db_session, async_bundle):
    server_type = db_session.query(CIType).filter(CIType.name == "Server").first()
    ci = CI(
        name="ip-host",
        type_id=server_type.id,
        status="active",
        search_ip="10.1.2.3",
        external_ids={"ip": "10.1.2.3"},
    )
    db_session.add(ci)
    db_session.commit()
    found = await find_cis_for_alert_async({"ip": "10.1.2.3"}, ci_repo=async_bundle.ci)
    assert any(c.id == ci.id for c in found)


@pytest.mark.asyncio
async def test_find_cis_for_alert_by_cmdb_id(db_session, async_bundle):
    server_type = db_session.query(CIType).filter(CIType.name == "Server").first()
    ci = CI(name="cmdb-host", type_id=server_type.id, status="active")
    db_session.add(ci)
    db_session.commit()
    found = await find_cis_for_alert_async({"cmdbId": str(ci.id)}, ci_repo=async_bundle.ci)
    assert any(c.id == ci.id for c in found)
