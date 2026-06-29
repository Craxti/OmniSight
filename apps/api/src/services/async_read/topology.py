from __future__ import annotations

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.services.base.async_domain import AsyncDomainService
from src.services.domain.topology import ensure_ci_exists_async
from src.services.rsm.async_graph import (
    async_build_graph,
    async_compute_components,
    async_compute_impact,
    async_find_business_path,
    async_get_direct_relations,
)


class AsyncTopologyService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)

    async def graph(self, resource_id: int, *, depth: int = 2):
        await ensure_ci_exists_async(self._bundle.ci, resource_id)
        return await async_build_graph(
            self._bundle.ci,
            self._bundle.relations,
            resource_id,
            depth=depth,
        )

    async def business_path(self, resource_id: int):
        return await async_find_business_path(
            resource_id,
            ci_repo=self._bundle.ci,
            rel_repo=self._bundle.relations,
        )

    async def impact(self, resource_id: int):
        return await async_compute_impact(
            resource_id,
            ci_repo=self._bundle.ci,
            rel_repo=self._bundle.relations,
        )

    async def components(self, resource_id: int):
        return await async_compute_components(
            resource_id,
            ci_repo=self._bundle.ci,
            rel_repo=self._bundle.relations,
        )

    async def direct_relations(self, resource_id: int):
        await ensure_ci_exists_async(self._bundle.ci, resource_id)
        return await async_get_direct_relations(self._bundle.relations, resource_id)
