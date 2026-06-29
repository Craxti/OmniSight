"""Regression: import CI must write per-row audit via async import service."""

import pytest
from src.models import AuditLog
from src.repositories.async_orm.ci_type_repository import AsyncCITypeRepository


@pytest.mark.asyncio
async def test_import_ci_items_writes_import_create_audit(
    db_session, admin_user, ci_import_export_write_service, async_bundle
):
    server_type = await AsyncCITypeRepository(async_bundle.session).require_by_name("Server")

    report = await ci_import_export_write_service.import_ci_items(
        [
            {
                "name": "import-audit-regression",
                "type_id": server_type.id,
                "status": "active",
                "owner": "qa",
                "environment": "test",
            }
        ],
        admin_user,
    )
    await async_bundle.session.commit()
    assert report.created == 1

    logs = db_session.query(AuditLog).filter(AuditLog.entity_type == "ci", AuditLog.action == "import_create").all()
    assert any(log.new_value and log.new_value.get("name") == "import-audit-regression" for log in logs)
