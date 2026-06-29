"""Unit tests for async CI import/export."""

import pytest
from src.models import CI, CIType, Relation
from src.schemas.export_filters import CiExportFilter


@pytest.mark.asyncio
async def test_export_full_includes_elements_and_relations(
    db_session, admin_user, ci_import_export_read_service, async_bundle
):
    server_type = db_session.query(CIType).filter(CIType.name == "Server").first()
    db_session.add(CI(name="export-ci", type_id=server_type.id, status="active"))
    db_session.commit()

    payload = await ci_import_export_read_service.export_full(admin_user, CiExportFilter())
    await async_bundle.session.commit()
    assert "elements" in payload
    assert "relations" in payload
    assert "filters" in payload
    assert len(payload["elements"]) >= 1


@pytest.mark.asyncio
async def test_import_ci_csv_parses_rows(db_session, admin_user, ci_import_export_write_service, async_bundle):
    csv_content = (
        "name,status,type_name,attributes,external_ids,criticality,environment,owner,team\n"
        "csv-import-ci,active,Server,{},{},low,test,qa,ops\n"
    )
    report = await ci_import_export_write_service.import_ci_csv(csv_content, admin_user)
    await async_bundle.session.commit()

    assert report.created == 1
    assert await async_bundle.ci.get_by_name("csv-import-ci") is not None


@pytest.mark.asyncio
async def test_export_subset_by_business_service_includes_subtree(
    db_session, ci_import_export_read_service, async_bundle
):
    biz_type = db_session.query(CIType).filter(CIType.name == "Business Service").first()
    app_type = db_session.query(CIType).filter(CIType.name == "Application").first()
    db_type = db_session.query(CIType).filter(CIType.name == "Database").first()
    biz = CI(name="export-biz", type_id=biz_type.id, status="active")
    app = CI(name="export-app", type_id=app_type.id, status="active")
    db = CI(name="export-db", type_id=db_type.id, status="active")
    db_session.add_all([biz, app, db])
    db_session.flush()
    db_session.add_all(
        [
            Relation(source_ci_id=app.id, target_ci_id=db.id, relation_type="depends_on", status="active"),
            Relation(source_ci_id=biz.id, target_ci_id=app.id, relation_type="depends_on", status="active"),
        ]
    )
    db_session.commit()

    cis, _relations = await ci_import_export_read_service.query_export_subset(
        CiExportFilter(business_service_id=biz.id)
    )
    names = {c.name for c in cis}
    assert names == {"export-biz", "export-app", "export-db"}
