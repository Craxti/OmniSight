"""Async RSM graph/topology (native await on repositories)."""

from __future__ import annotations

from src.core.cache import cache_get_async, cache_set_async
from src.core.serializers import relation_to_response
from src.repositories.async_orm.ci_repository import AsyncCiRepository
from src.repositories.async_orm.relation_repository import AsyncRelationRepository
from src.schemas.relations import RelationResponse
from src.schemas.resources import BusinessPathResponse, ComponentsResponse, ImpactResponse, ResourceGraphResponse
from src.services.domain.graph_panel import (
    GRAPH_PANEL_CACHE_TTL,
    build_graph_panel_async,
    graph_panel_cache_key,
)
from src.services.rsm.async_topology import (
    async_find_business_path_directed,
    async_find_components_below,
    async_find_impacted_business_services,
)


async def async_build_graph(
    ci_repo: AsyncCiRepository,
    rel_repo: AsyncRelationRepository,
    root_id: int,
    depth: int = 2,
) -> ResourceGraphResponse:
    cache_key = graph_panel_cache_key(root_id, depth)
    hit = await cache_get_async(cache_key)
    if hit is not None:
        return hit

    result = await build_graph_panel_async(
        root_id=root_id,
        depth=depth,
        get_active=ci_repo.get_active,
        relations_for_ci=rel_repo.for_ci,
    )
    await cache_set_async(cache_key, result, ttl=GRAPH_PANEL_CACHE_TTL)
    return result


async def async_get_direct_relations(
    rel_repo: AsyncRelationRepository,
    resource_id: int,
) -> list[RelationResponse]:
    relations = await rel_repo.for_ci(resource_id)
    return [relation_to_response(r) for r in relations]


async def async_compute_impact(
    ci_id: int,
    *,
    ci_repo: AsyncCiRepository,
    rel_repo: AsyncRelationRepository,
) -> ImpactResponse:
    await ci_repo.get_or_404(ci_id)
    impacted = await async_find_impacted_business_services(ci_id, ci_repo=ci_repo, rel_repo=rel_repo)
    return ImpactResponse(ci_id=ci_id, impacted_business_services=impacted, count=len(impacted))


async def async_compute_components(
    ci_id: int,
    *,
    ci_repo: AsyncCiRepository,
    rel_repo: AsyncRelationRepository,
) -> ComponentsResponse:
    components = await async_find_components_below(ci_id, ci_repo=ci_repo, rel_repo=rel_repo)
    return ComponentsResponse(ci_id=ci_id, components=components, count=len(components))


async def async_find_business_path(
    ci_id: int,
    *,
    ci_repo: AsyncCiRepository,
    rel_repo: AsyncRelationRepository,
) -> BusinessPathResponse:
    path = await async_find_business_path_directed(ci_id, ci_repo=ci_repo, rel_repo=rel_repo)
    return BusinessPathResponse(path=path)
