from typing import Annotated

from fastapi import APIRouter, Depends, Query
from src.api.handlers.autodiscover import (
    handle_apply_run,
    handle_autodiscover_scan,
    handle_create_connector,
    handle_delete_connector,
    handle_get_run,
    handle_list_connectors,
    handle_list_profiles,
    handle_list_runs,
    handle_sync_connector,
    handle_test_connector,
    handle_update_connector,
)
from src.core.auth import require_admin, require_editor, require_viewer
from src.core.deps import (
    get_autodiscover_read_port,
    get_autodiscover_write_port,
    get_transactional_autodiscover_write_port,
)
from src.models import User
from src.schemas.autodiscover import (
    AutodiscoverApplyRequest,
    AutodiscoverScanRequest,
    SyncConnectorCreate,
    SyncConnectorUpdate,
)
from src.services.async_read.autodiscover import AsyncAutodiscoverReadService
from src.services.async_write.autodiscover import AsyncAutodiscoverWriteService

router = APIRouter(prefix="/autodiscover", tags=["Autodiscover v1"])

AutodiscoverSvc = Annotated[AsyncAutodiscoverWriteService, Depends(get_autodiscover_write_port)]
AutodiscoverReadSvc = Annotated[AsyncAutodiscoverReadService, Depends(get_autodiscover_read_port)]
TransactionalAutodiscoverSvc = Annotated[
    AsyncAutodiscoverWriteService,
    Depends(get_transactional_autodiscover_write_port),
]


@router.get("/connectors")
async def list_connectors_v1(
    service: AutodiscoverReadSvc,
    _: Annotated[User, Depends(require_viewer)],
    enabled_only: bool = True,
):
    return await handle_list_connectors(service, enabled_only=enabled_only)


@router.post("/connectors")
async def create_connector_v1(
    body: SyncConnectorCreate,
    service: AutodiscoverSvc,
    _: Annotated[User, Depends(require_editor)],
):
    return await handle_create_connector(service, body)


@router.patch("/connectors/{connector_id}")
async def update_connector_v1(
    connector_id: int,
    body: SyncConnectorUpdate,
    service: AutodiscoverSvc,
    _: Annotated[User, Depends(require_editor)],
):
    return await handle_update_connector(service, connector_id, body)


@router.delete("/connectors/{connector_id}")
async def delete_connector_v1(
    connector_id: int,
    service: AutodiscoverSvc,
    _: Annotated[User, Depends(require_admin)],
):
    return await handle_delete_connector(service, connector_id)


@router.post("/connectors/{connector_id}/test")
async def test_connector_v1(
    connector_id: int,
    service: AutodiscoverReadSvc,
    _: Annotated[User, Depends(require_editor)],
):
    return await handle_test_connector(service, connector_id)


@router.post("/connectors/{connector_id}/sync")
async def sync_connector_v1(
    connector_id: int,
    service: AutodiscoverSvc,
    user: Annotated[User, Depends(require_editor)],
):
    return await handle_sync_connector(service, connector_id, user)


@router.get("/profiles")
async def list_profiles_v1(
    service: AutodiscoverReadSvc,
    _: Annotated[User, Depends(require_viewer)],
):
    return await handle_list_profiles(service)


@router.post("/scan")
async def autodiscover_scan_v1(
    body: AutodiscoverScanRequest,
    service: AutodiscoverSvc,
    user: Annotated[User, Depends(require_editor)],
):
    return await handle_autodiscover_scan(service, body, user)


@router.get("/runs")
async def list_runs_v1(
    service: AutodiscoverReadSvc,
    _: Annotated[User, Depends(require_viewer)],
    limit: int = Query(default=20, ge=1, le=100),
):
    return await handle_list_runs(service, limit=limit)


@router.get("/runs/{run_id}")
async def get_run_v1(
    run_id: int,
    service: AutodiscoverReadSvc,
    _: Annotated[User, Depends(require_viewer)],
):
    return await handle_get_run(service, run_id)


@router.post("/runs/{run_id}/apply")
async def apply_run_v1(
    run_id: int,
    body: AutodiscoverApplyRequest,
    service: TransactionalAutodiscoverSvc,
    user: Annotated[User, Depends(require_editor)],
):
    return await handle_apply_run(service, run_id, body, user)
