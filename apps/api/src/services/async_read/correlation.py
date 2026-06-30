from __future__ import annotations

from typing import Any

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.core.cache import cache_get_async, cache_set_async
from src.schemas.correlation import ChainCheckResponse, CorrelationContextPayload, CorrelationIngestLogDetail, CorrelationIngestLogListResponse, CorrelationResolvePayload
from src.services.base.async_domain import AsyncDomainService
from src.services.domain.correlation import (
    build_chain_check_response,
    build_ingest_log_list,
    build_resolve_payload,
    match_alert_to_result,
    paginate_alerts,
    resolve_batch_cache_key,
)
from src.services.rsm.async_alert_search import find_cis_for_alert_async
from src.services.rsm.async_correlation import build_correlation_context_async
from src.services.rsm.async_topology import async_on_same_dependency_chain


class AsyncCorrelationReadService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)

    async def chain_check(self, resource_ids: list[int]) -> ChainCheckResponse:
        for resource_id in resource_ids:
            await self._bundle.ci.get_or_404(resource_id)
        chain_related = await async_on_same_dependency_chain(
            resource_ids,
            rel_repo=self._bundle.relations,
        )
        return build_chain_check_response(resource_ids, chain_related)

    async def build_context(self, resource_ids: list[int], *, depth: int = 3) -> CorrelationContextPayload:
        return await build_correlation_context_async(
            resource_ids,
            depth=depth,
            ci_repo=self._bundle.ci,
            rel_repo=self._bundle.relations,
        )

    async def resolve_batch(
        self,
        alerts: list[dict[str, Any]],
        *,
        page: int = 1,
        page_size: int | None = None,
    ) -> CorrelationResolvePayload:
        cache_key = resolve_batch_cache_key(alerts, page=page, page_size=page_size)
        hit = await cache_get_async(cache_key)
        if hit is not None:
            return hit

        slice_alerts, pagination = paginate_alerts(alerts, page=page, page_size=page_size)
        resolved = []
        unresolved = []
        for alert in slice_alerts:
            matches = await find_cis_for_alert_async(alert, ci_repo=self._bundle.ci)
            result = match_alert_to_result(alert, matches)
            if result.resolved:
                resolved.append(result)
            else:
                unresolved.append(result)

        payload = build_resolve_payload(resolved, unresolved, pagination=pagination)
        await cache_set_async(cache_key, payload, ttl=30)
        return payload

    async def list_ingest_logs(
        self,
        *,
        source: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> CorrelationIngestLogListResponse:
        items, total = await self._bundle.correlation_ingest_logs.list_recent(
            source=source,
            skip=skip,
            limit=limit,
        )
        return build_ingest_log_list(items, total, skip, limit)

    async def get_ingest_log(self, log_id: int) -> CorrelationIngestLogDetail:
        from src.core.serializers import correlation_ingest_log_to_detail

        row = await self._bundle.correlation_ingest_logs.get_or_404(log_id)
        return correlation_ingest_log_to_detail(row)
