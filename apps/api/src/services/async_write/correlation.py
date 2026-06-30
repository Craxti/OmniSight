"""Native async correlation write service (ingest + webhook outbox)."""

from __future__ import annotations

from typing import Any

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.schemas.correlation import CorrelationContextPayload, CorrelationIngestResponse
from src.services.async_read.correlation import AsyncCorrelationReadService
from src.services.base.async_domain import AsyncDomainService
from src.services.integrations.async_webhook import dispatch_correlation_webhook_async


class AsyncCorrelationWriteService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)
        self._read = AsyncCorrelationReadService(bundle)

    async def ingest(
        self,
        alerts: list[dict[str, Any]],
        *,
        source: str | None = None,
        depth: int = 3,
        page: int = 1,
        page_size: int | None = None,
        webhook_url: str | None = None,
        dispatch_webhook: bool = False,
    ) -> CorrelationIngestResponse:
        resolve_result = await self._read.resolve_batch(alerts, page=page, page_size=page_size)
        resource_ids = [r.resource.id for r in resolve_result.resolved if r.resource]
        context = (
            await self._read.build_context(resource_ids, depth=depth) if resource_ids else CorrelationContextPayload()
        )
        result = CorrelationIngestResponse(
            source=source,
            schema_version="rsm-correlation-v1",
            resolve=resolve_result,
            correlation=context,
            enrichment=context.enrichment,
            potential_root_cause_zone=context.potential_root_cause_zone,
        )
        log_entry = await self._bundle.correlation_ingest_logs.create(
            source=source,
            alerts=alerts,
            result=result.model_dump(),
            alert_count=len(alerts),
            resolved_count=len(resolve_result.resolved),
            unresolved_count=len(resolve_result.unresolved),
            chain_related=bool(context.chain_related),
        )
        result = result.model_copy(update={"ingest_log_id": log_entry.id})
        if dispatch_webhook or webhook_url:
            webhook = await self._dispatch_webhook(result.model_dump(), webhook_url=webhook_url)
            return result.model_copy(update={"webhook": webhook})
        await self._session.commit()
        return result

    async def _dispatch_webhook(self, payload: dict[str, Any], *, webhook_url: str | None = None) -> dict[str, Any]:
        return await dispatch_correlation_webhook_async(self._session, payload, webhook_url=webhook_url)
