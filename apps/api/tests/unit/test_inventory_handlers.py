"""Unit tests for v1 inventory handlers."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from src.api.handlers.inventory import (
    handle_ci_bulk_status,
    handle_ci_create,
    handle_ci_detail,
    handle_ci_list,
    handle_relation_create,
    handle_relation_delete,
    handle_relation_detail,
    handle_relation_update,
    handle_relations_list,
    handle_relations_validate,
)
from src.schemas.ci import BulkStatusUpdate, CICreate, CIDetailResponse, CIListResponse, CIResponse
from src.schemas.relations import RelationCreate, RelationResponse, RelationUpdate


@pytest.mark.asyncio
async def test_handle_ci_list_v1_envelope(monkeypatch):
    service = MagicMock()
    service.list_ci = AsyncMock(
        return_value=CIListResponse(
            items=[CIResponse(id=1, name="a", type_id=1, status="active")],
            total=1,
            skip=0,
            limit=10,
        )
    )
    body = await handle_ci_list(service, page=1, page_size=10)
    assert body["api_version"] == "v1"
    assert body["pagination"]["total_items"] == 1


@pytest.mark.asyncio
async def test_handle_relations_list_v1_uses_db_page(monkeypatch):
    service = MagicMock()
    service.list_relations_page = AsyncMock(
        return_value=(
            [
                RelationResponse(
                    id=2,
                    source_ci_id=1,
                    target_ci_id=2,
                    relation_type="depends_on",
                    status="active",
                    direction="outgoing",
                )
            ],
            3,
        )
    )
    body = await handle_relations_list(service, page=2, page_size=1)
    service.list_relations_page.assert_awaited_once_with(skip=1, limit=1)
    assert body["pagination"]["page"] == 2
    assert len(body["items"]) == 1
    assert body["items"][0]["id"] == 2
    assert body["pagination"]["total_items"] == 3


@pytest.mark.asyncio
async def test_handle_relations_validate_v1(monkeypatch):
    from src.schemas.audit import RelationValidationResponse

    service = MagicMock()
    service.validate_model = AsyncMock(return_value=RelationValidationResponse(valid=True, issue_count=0, issues=[]))
    body = await handle_relations_validate(service)
    assert body["validation"]["valid"] is True


@pytest.mark.asyncio
async def test_handle_ci_bulk_status_v1(monkeypatch):
    service = MagicMock()
    service.bulk_status = AsyncMock(return_value={"ok": True, "updated": 0})
    user = MagicMock()
    user.email = "admin@omnisight.local"
    body = await handle_ci_bulk_status(service, BulkStatusUpdate(ci_ids=[], status="active"), user)
    assert body["result"]["ok"] is True


@pytest.mark.asyncio
async def test_handle_ci_create_v1_envelope(monkeypatch):
    service = MagicMock()
    service.create_ci = AsyncMock(return_value=CIResponse(id=1, name="new", type_id=1, status="active"))
    user = MagicMock()
    user.email = "admin@omnisight.local"

    body = await handle_ci_create(
        service,
        CICreate(name="new", type_name="Server", owner="ops", environment="test", criticality="low"),
        user,
    )
    assert body["ci"]["id"] == 1


@pytest.mark.asyncio
async def test_handle_relation_mutations_v1(monkeypatch):
    service = MagicMock()
    user = MagicMock()
    user.email = "admin@omnisight.local"
    relation = RelationResponse(
        id=5,
        source_ci_id=1,
        target_ci_id=2,
        relation_type="depends_on",
        status="active",
        direction="outgoing",
    )
    service.create_relation = AsyncMock(return_value=relation)
    service.update_relation = AsyncMock(return_value=relation)
    service.delete_relation = AsyncMock(return_value={"ok": True})

    created = await handle_relation_create(
        service,
        RelationCreate(source_ci_id=1, target_ci_id=2, relation_type="depends_on", data_source="manual"),
        user,
    )
    assert created["relation"]["id"] == 5

    updated = await handle_relation_update(service, 5, RelationUpdate(status="active"), user)
    assert updated["relation"]["id"] == 5

    deleted = await handle_relation_delete(service, 5, user)
    assert deleted["result"]["ok"] is True


@pytest.mark.asyncio
async def test_handle_ci_detail_v1_envelope(monkeypatch):
    service = MagicMock()
    service.get_ci_detail = AsyncMock(return_value=CIDetailResponse(id=7, name="srv", type_id=1, status="active"))

    body = await handle_ci_detail(service, 7)
    assert body["api_version"] == "v1"
    assert body["ci"]["id"] == 7


@pytest.mark.asyncio
async def test_handle_relation_detail_v1_envelope(monkeypatch):
    service = MagicMock()
    service.get_relation = AsyncMock(
        return_value=RelationResponse(
            id=9,
            source_ci_id=1,
            target_ci_id=2,
            relation_type="depends_on",
            status="active",
            direction="outgoing",
        )
    )
    body = await handle_relation_detail(service, 9)
    assert body["relation"]["id"] == 9
