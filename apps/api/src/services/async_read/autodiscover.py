from __future__ import annotations

import asyncio

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.core.exceptions import NotFoundError
from src.schemas.autodiscover import (
    AutodiscoverRunSummary,
    SyncConnectorResponse,
    SyncConnectorTestResponse,
    SyncProfileResponse,
)
from src.services.autodiscover.connectors.registry import discover_with_retry
from src.services.autodiscover.runtime.seed import ensure_default_sync_assets_async
from src.services.autodiscover.serializers import run_to_scan_response
from src.services.base.async_domain import AsyncDomainService
from src.services.domain.autodiscover import list_profile_responses, list_run_summaries


class AsyncAutodiscoverReadService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)

    async def _ensure_defaults(self) -> None:
        await ensure_default_sync_assets_async(self._bundle.session)

    async def list_connectors(self, *, enabled_only: bool = True) -> list[SyncConnectorResponse]:
        await self._ensure_defaults()
        from src.services.autodiscover.serializers import connector_to_response

        connectors = await self._bundle.autodiscover_connectors.list_ordered(enabled_only=enabled_only)
        return [connector_to_response(c) for c in connectors]

    async def list_profiles(self) -> list[SyncProfileResponse]:
        await self._ensure_defaults()
        profiles = await self._bundle.autodiscover_profiles.list_all()
        return list_profile_responses(profiles)

    async def list_runs(self, limit: int = 20) -> list[AutodiscoverRunSummary]:
        runs = await self._bundle.autodiscover_runs.list_recent(limit)
        return list_run_summaries(runs)

    async def get_run(self, run_id: int):
        run = await self._bundle.autodiscover_runs.get_with_mappings(run_id)
        if not run:
            raise NotFoundError("Autodiscover run not found")
        return run_to_scan_response(run)

    async def test_connector(self, connector_id: int) -> SyncConnectorTestResponse:
        connector = await self._bundle.autodiscover_connectors.get_by_id(connector_id)
        if not connector:
            raise NotFoundError("Connector not found")
        result = await asyncio.to_thread(discover_with_retry, connector)
        return SyncConnectorTestResponse(
            ok=result.ok,
            records_found=len(result.entities),
            error=result.error,
            duration_ms=result.duration_ms,
        )
