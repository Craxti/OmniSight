"""Autodiscover HTTP handlers (v1 envelopes)."""

from __future__ import annotations

from src.api.handlers.v1_envelopes import (
    apply_v1_envelope,
    autodiscover_items_v1_envelope,
    connector_sync_v1_envelope,
    connector_test_v1_envelope,
    connector_v1_envelope,
    delete_result_v1_envelope,
    scan_v1_envelope,
)
from src.core.exceptions import DomainValidationError
from src.models import User
from src.schemas.autodiscover import (
    AutodiscoverApplyRequest,
    AutodiscoverScanRequest,
    SyncConnectorCreate,
    SyncConnectorUpdate,
)
from src.services.async_read.autodiscover import AsyncAutodiscoverReadService
from src.services.async_write.autodiscover import AsyncAutodiscoverWriteService


async def handle_list_connectors(service: AsyncAutodiscoverReadService, *, enabled_only: bool = True):
    items = await service.list_connectors(enabled_only=enabled_only)
    return autodiscover_items_v1_envelope(items)


async def handle_create_connector(service: AsyncAutodiscoverWriteService, body: SyncConnectorCreate):
    result = await service.create_connector(body)
    return connector_v1_envelope(result)


async def handle_update_connector(service: AsyncAutodiscoverWriteService, connector_id: int, body: SyncConnectorUpdate):
    result = await service.update_connector(connector_id, body)
    return connector_v1_envelope(result)


async def handle_delete_connector(service: AsyncAutodiscoverWriteService, connector_id: int):
    result = await service.delete_connector(connector_id)
    return delete_result_v1_envelope(result)


async def handle_test_connector(service: AsyncAutodiscoverReadService, connector_id: int):
    result = await service.test_connector(connector_id)
    return connector_test_v1_envelope(result)


async def handle_sync_connector(service: AsyncAutodiscoverWriteService, connector_id: int, user: User):
    result = await service.sync_connector(connector_id, user)
    return connector_sync_v1_envelope(result)


async def handle_list_profiles(service: AsyncAutodiscoverReadService):
    items = await service.list_profiles()
    return autodiscover_items_v1_envelope(items)


async def handle_autodiscover_scan(service: AsyncAutodiscoverWriteService, body: AutodiscoverScanRequest, user: User):
    if not body.connector_ids and not body.server_ci_ids and not body.profile_id:
        raise DomainValidationError("profile_id, connector_ids or server_ci_ids required")
    result = await service.run_scan(body, user)
    return scan_v1_envelope(result)


async def handle_list_runs(service: AsyncAutodiscoverReadService, *, limit: int = 20):
    items = await service.list_runs(limit)
    return autodiscover_items_v1_envelope(items)


async def handle_get_run(service: AsyncAutodiscoverReadService, run_id: int):
    result = await service.get_run(run_id)
    return scan_v1_envelope(result)


async def handle_apply_run(
    service: AsyncAutodiscoverWriteService,
    run_id: int,
    body: AutodiscoverApplyRequest,
    user: User,
):
    result = await service.apply_run(run_id, body, user)
    return apply_v1_envelope(result)
