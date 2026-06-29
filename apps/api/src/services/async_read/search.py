from __future__ import annotations

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.core.cache import cache_get_async, cache_set_async
from src.schemas.resources import ResourceSearchResponse
from src.services.base.async_domain import AsyncDomainService
from src.services.domain.search import build_resource_search_response, resource_search_cache_key


class AsyncSearchService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)

    async def resource_search(self, **kwargs) -> ResourceSearchResponse:
        cache_key = resource_search_cache_key(**kwargs)
        hit = await cache_get_async(cache_key)
        if hit is not None:
            return hit
        cis, total = await self._bundle.ci.search(**kwargs)
        result = build_resource_search_response(cis, total)
        await cache_set_async(cache_key, result, ttl=30)
        return result
