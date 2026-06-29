"""Unit tests for async import audit helpers."""

import pytest
from src.models import AuditLog
from src.schemas.common import ImportReport
from src.services.async_import_audit import log_import_audit_async


@pytest.mark.asyncio
async def test_log_import_audit_commits(db_session, admin_user, async_bundle):
    report = ImportReport(created=2, updated=1, skipped=0, errors=[])
    await log_import_audit_async(async_bundle.session, async_bundle.audit, admin_user, "import_test", report)
    await async_bundle.session.commit()

    row = db_session.query(AuditLog).filter(AuditLog.action == "import_test").first()
    assert row is not None
    assert row.new_value["created"] == 2
