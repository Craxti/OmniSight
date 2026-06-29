"""Async autodiscover write service."""

from __future__ import annotations

from src.models import User
from src.schemas.autodiscover import (
    AutodiscoverApplyRequest,
    AutodiscoverApplyResponse,
    AutodiscoverScanRequest,
    AutodiscoverScanResponse,
    SyncConnectorCreate,
    SyncConnectorResponse,
    SyncConnectorSyncResponse,
    SyncConnectorUpdate,
)
from src.services.autodiscover.runtime.apply_run import AsyncAutodiscoverApplyService
from src.services.autodiscover.runtime.connector_write import AsyncAutodiscoverConnectorWriteService
from src.services.autodiscover.runtime.scan import AsyncAutodiscoverScanService
from src.services.base.async_domain import AsyncDomainService


class AsyncAutodiscoverWriteService(AsyncDomainService):
    def __init__(self, bundle) -> None:
        super().__init__(bundle)
        self._connectors = AsyncAutodiscoverConnectorWriteService(bundle)
        self._apply = AsyncAutodiscoverApplyService(bundle)
        self._scan = AsyncAutodiscoverScanService(bundle)

    async def create_connector(self, body: SyncConnectorCreate) -> SyncConnectorResponse:
        return await self._connectors.create_connector(body)

    async def update_connector(self, connector_id: int, body: SyncConnectorUpdate) -> SyncConnectorResponse:
        return await self._connectors.update_connector(connector_id, body)

    async def delete_connector(self, connector_id: int) -> dict:
        return await self._connectors.delete_connector(connector_id)

    async def sync_connector(self, connector_id: int, user: User) -> SyncConnectorSyncResponse:
        return await self._scan.sync_connector(connector_id, user)

    async def run_scan(self, body: AutodiscoverScanRequest, user: User) -> AutodiscoverScanResponse:
        return await self._scan.run_scan(body, user)

    async def apply_run(self, run_id: int, body: AutodiscoverApplyRequest, user: User) -> AutodiscoverApplyResponse:
        return await self._apply.apply_run(
            run_id,
            user=user,
            mapping_ids=body.mapping_ids,
            apply_auto_only=body.apply_auto_only,
        )
