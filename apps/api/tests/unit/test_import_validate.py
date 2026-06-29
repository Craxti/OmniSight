"""Unit tests for import-time validation helpers."""

import pytest
from src.core.exceptions import DomainValidationError
from src.models import CI, CIType
from src.services.async_import_validate import find_external_id_conflict_async
from src.services.async_relations.validator import validate_relation_endpoints_async
from src.services.import_validate import validate_relation_status


def test_validate_relation_status_rejects_unknown():
    with pytest.raises(DomainValidationError, match="Invalid relation status"):
        validate_relation_status("unknown")


@pytest.mark.asyncio
async def test_find_external_id_conflict_detects_duplicate(db_session, async_bundle):
    server_type = db_session.query(CIType).filter(CIType.name == "Server").first()
    existing = CI(
        name="dup-host",
        type_id=server_type.id,
        status="active",
        search_hostname="app-01",
    )
    db_session.add(existing)
    db_session.commit()

    conflict = await find_external_id_conflict_async(
        async_bundle.ci,
        {"hostname": "app-01"},
    )
    assert conflict is not None
    assert "Duplicate hostname" in conflict


@pytest.mark.asyncio
async def test_validate_relation_endpoints_archived_and_self(db_session, async_bundle):
    server_type = db_session.query(CIType).filter(CIType.name == "Server").first()
    archived = CI(name="arch-src", type_id=server_type.id, status="archived")
    db_session.add(archived)
    db_session.commit()

    self_errors = await validate_relation_endpoints_async(
        async_bundle.ci,
        archived.id,
        archived.id,
    )
    assert any("Self-referencing" in err for err in self_errors)
    assert any("archived" in err for err in self_errors)

    missing_errors = await validate_relation_endpoints_async(
        async_bundle.ci,
        99999,
        88888,
    )
    assert any("not found" in err for err in missing_errors)
