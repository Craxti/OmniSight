"""Unit tests for async relation import/export."""

import pytest
from src.models import CI, AuditLog, CIType, Relation
from src.schemas.relations import RelationImportItem, RelationImportRequest


def _two_cis(db_session) -> tuple[CI, CI]:
    server_type = db_session.query(CIType).filter(CIType.name == "Server").first()
    app_type = db_session.query(CIType).filter(CIType.name == "Application").first()
    source = CI(name="rel-imp-src", type_id=server_type.id, status="active")
    target = CI(name="rel-imp-tgt", type_id=app_type.id, status="active")
    db_session.add_all([source, target])
    db_session.commit()
    db_session.refresh(source)
    db_session.refresh(target)
    return source, target


@pytest.mark.asyncio
async def test_export_csv_writes_audit(db_session, admin_user, relation_import_export_read_service, async_bundle):
    source, target = _two_cis(db_session)
    db_session.add(
        Relation(
            source_ci_id=source.id,
            target_ci_id=target.id,
            relation_type="depends_on",
            status="active",
        )
    )
    db_session.commit()

    resp = await relation_import_export_read_service.export_csv(admin_user)
    await async_bundle.session.commit()
    assert resp.media_type == "text/csv"
    assert "relations.csv" in resp.headers["Content-Disposition"]

    logs = db_session.query(AuditLog).filter(AuditLog.action == "export_relations_csv").all()
    assert logs


@pytest.mark.asyncio
async def test_export_xlsx_returns_spreadsheet(db_session, admin_user, relation_import_export_read_service):
    resp = await relation_import_export_read_service.export_xlsx(admin_user)
    assert "spreadsheetml" in resp.media_type
    assert "relations.xlsx" in resp.headers["Content-Disposition"]


@pytest.mark.asyncio
async def test_import_csv_creates_relation(db_session, admin_user, relation_import_export_write_service, async_bundle):
    source, target = _two_cis(db_session)
    csv_content = (
        "source_name,target_name,relation_type,status,data_source\n"
        f"{source.name},{target.name},depends_on,active,pytest\n"
    )

    report = await relation_import_export_write_service.import_csv(csv_content, admin_user)
    await async_bundle.session.commit()
    assert report.created == 1
    assert not report.errors

    rel = (
        db_session.query(Relation)
        .filter(Relation.source_ci_id == source.id, Relation.target_ci_id == target.id)
        .first()
    )
    assert rel is not None

    logs = db_session.query(AuditLog).filter(AuditLog.action == "import_relations_csv").all()
    assert logs


@pytest.mark.asyncio
async def test_import_json_by_ci_names(db_session, admin_user, relation_import_export_write_service, async_bundle):
    source, target = _two_cis(db_session)
    body = RelationImportRequest(
        relations=[
            RelationImportItem(
                source_name=source.name,
                target_name=target.name,
                relation_type="uses",
                status="active",
                data_source="json-import",
            )
        ]
    )

    report = await relation_import_export_write_service.import_json(body, admin_user)
    await async_bundle.session.commit()
    assert report.created == 1


@pytest.mark.asyncio
async def test_import_csv_skips_missing_ci(db_session, admin_user, relation_import_export_write_service):
    csv_content = "source_name,target_name,relation_type,status,data_source\nmissing-a,missing-b,depends_on,active,x\n"
    report = await relation_import_export_write_service.import_csv(csv_content, admin_user)
    assert report.skipped == 1
    assert report.errors
