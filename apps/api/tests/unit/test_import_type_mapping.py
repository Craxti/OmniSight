import pytest
from src.services.ci.import_type_helpers import extract_import_type_name


def test_extract_import_type_name_prefers_type_name():
    assert extract_import_type_name({"type_name": "Server", "type": "Other"}) == "Server"
    assert extract_import_type_name({"type": "Database"}) == "Database"


@pytest.mark.asyncio
async def test_preview_marks_unknown_types(db_session, async_bundle, ci_import_export_read_service):
    items = [
        {"name": "a1", "type_name": "Custom Widget", "attributes": {"color": "red"}},
        {"name": "a2", "type_name": "Custom Widget", "attributes": {"size": "L"}},
        {"name": "a3", "type_name": "Server"},
    ]
    result = await ci_import_export_read_service.preview_import_type_mappings(items)
    assert result["needs_mapping"] is True
    by_source = {p["source_type"]: p for p in result["proposals"]}
    assert by_source["Server"]["status"] == "matched"
    assert by_source["Custom Widget"]["status"] == "unknown"
    assert by_source["Custom Widget"]["item_count"] == 2
    assert by_source["Custom Widget"]["draft"]["name"] == "Custom Widget"
    assert "color" in by_source["Custom Widget"]["draft"]["attribute_schema"]["properties"]


@pytest.mark.asyncio
async def test_apply_creates_draft_type_and_remaps(
    db_session, admin_user, ci_import_export_write_service, async_bundle
):
    items = [{"name": "imp-1", "type_name": "Novel Type", "status": "active"}]
    mappings = [
        {
            "source_type": "Novel Type",
            "action": "create_new",
            "draft": {
                "name": "Novel Type",
                "description": "draft",
                "attribute_schema": {"properties": {}},
            },
        }
    ]
    remapped, errors = await ci_import_export_write_service._import.apply_import_type_mappings(
        items,
        mappings,
        admin_user,
    )
    await async_bundle.session.commit()
    assert not errors
    assert remapped[0]["type_name"] == "Novel Type"
    created_type = await async_bundle.ci_types.get_by_name("Novel Type")
    assert created_type is not None
    assert created_type.is_import_draft is True


@pytest.mark.asyncio
async def test_preview_counts_missing_type_items(db_session, ci_import_export_read_service):
    items = [
        {"name": "no-type"},
        {"name": "with-type", "type_name": "Server"},
    ]
    result = await ci_import_export_read_service.preview_import_type_mappings(items)
    assert result["missing_type_items"] == 1
    assert result["proposals"][0]["source_type"] == "Server"


@pytest.mark.asyncio
async def test_import_ci_items_with_type_mappings_creates_cis(
    db_session, admin_user, ci_import_export_write_service, async_bundle
):
    suffix = "unit-map"
    type_name = f"E2E Unit Type {suffix}"
    items = [
        {
            "name": f"e2e-unit-{suffix}-1",
            "type_name": type_name,
            "status": "active",
            "criticality": "low",
            "environment": "test",
            "owner": "qa",
            "attributes": {"slot": "a"},
        },
    ]
    mappings = [
        {
            "source_type": type_name,
            "action": "create_new",
            "draft": {
                "name": type_name,
                "description": "unit test draft",
                "attribute_schema": {"properties": {"slot": {"type": "string"}}},
            },
        }
    ]
    report = await ci_import_export_write_service.import_ci_items(
        items,
        admin_user,
        type_mappings=mappings,
    )
    await async_bundle.session.commit()
    assert report.created == 1
    assert not report.errors
