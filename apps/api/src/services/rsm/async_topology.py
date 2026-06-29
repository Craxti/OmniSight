"""Async topology helpers (``await`` on async repositories)."""

from __future__ import annotations

from src.core.serializers import ci_to_response
from src.repositories.async_orm.ci_repository import AsyncCiRepository
from src.repositories.async_orm.relation_repository import AsyncRelationRepository
from src.repositories.protocols import AsyncRelationTopologyRepositoryProtocol
from src.schemas.ci import CIResponse
from src.schemas.resources import ImpactedServiceItem
from src.services.rsm.lookup import is_business_service
from src.services.rsm.topology_algorithms import (
    BUSINESS_PATH_MAX_HOPS,
    CHAIN_RELATION_TYPES,
    DEPENDENCY_TYPES,
    business_path_extend,
    component_ids_below,
    filter_non_business_ci_ids,
    filter_non_business_ci_responses,
    impacted_dependent_ids,
    root_cause_candidate_ids,
    to_impacted_business_services,
)
from src.services.rsm.topology_algorithms import (
    on_same_dependency_chain as resources_on_same_chain,
)


async def async_on_same_dependency_chain(
    resource_ids: list[int],
    *,
    rel_repo: AsyncRelationTopologyRepositoryProtocol,
) -> bool:
    if len(resource_ids) <= 1:
        return True
    ids = set(resource_ids)
    forward, reverse = await rel_repo.dependency_adjacency(ci_ids=ids, relation_types=CHAIN_RELATION_TYPES)
    return resources_on_same_chain(resource_ids, forward, reverse)


async def async_find_impacted_business_services(
    ci_id: int,
    *,
    ci_repo: AsyncCiRepository,
    rel_repo: AsyncRelationRepository,
) -> list[ImpactedServiceItem]:
    _, reverse = await rel_repo.dependency_adjacency(relation_types=CHAIN_RELATION_TYPES)
    dependents = impacted_dependent_ids(ci_id, reverse)
    if not dependents:
        return []
    return to_impacted_business_services(await ci_repo.list_in_ids(dependents))


async def async_find_components_below(
    ci_id: int,
    *,
    ci_repo: AsyncCiRepository,
    rel_repo: AsyncRelationRepository,
) -> list[CIResponse]:
    root = await ci_repo.get_or_404(ci_id)
    if not is_business_service(root):
        return []
    forward, _ = await rel_repo.dependency_adjacency(relation_types=CHAIN_RELATION_TYPES)
    below = component_ids_below(ci_id, forward)
    if not below:
        return []
    return filter_non_business_ci_responses(await ci_repo.list_in_ids(below))


async def async_find_business_path_directed(
    ci_id: int,
    *,
    ci_repo: AsyncCiRepository,
    rel_repo: AsyncRelationRepository,
) -> list[CIResponse]:
    ci = await ci_repo.get_or_404(ci_id)
    path = [ci_to_response(ci)]
    if is_business_service(ci):
        return path
    current_ids = {ci_id}
    visited = {ci_id}
    for _ in range(BUSINESS_PATH_MAX_HOPS):
        rels = await rel_repo.list_incoming_with_source(current_ids, DEPENDENCY_TYPES)
        if not rels:
            break
        path, next_ids, done = business_path_extend(path, visited, rels)
        if done:
            return path
        if not next_ids:
            break
        current_ids = next_ids
    return path


async def async_find_component_ids_below(
    ci_id: int,
    *,
    ci_repo: AsyncCiRepository,
    rel_repo: AsyncRelationRepository,
) -> set[int]:
    root = await ci_repo.get_or_404(ci_id)
    if not is_business_service(root):
        return set()
    forward, _ = await rel_repo.dependency_adjacency(relation_types=CHAIN_RELATION_TYPES)
    below = component_ids_below(ci_id, forward)
    if not below:
        return set()
    return filter_non_business_ci_ids(await ci_repo.list_in_ids(below))


async def async_find_root_cause_candidates(
    resource_ids: list[int],
    *,
    ci_repo: AsyncCiRepository,
    rel_repo: AsyncRelationRepository,
) -> list[CIResponse]:
    if not resource_ids:
        return []
    ids = set(resource_ids)
    forward, _ = await rel_repo.dependency_adjacency(ci_ids=ids, relation_types=CHAIN_RELATION_TYPES)
    leaves = root_cause_candidate_ids(resource_ids, forward)
    cis = await ci_repo.list_in_ids(set(leaves))
    return [ci_to_response(c) for c in cis]
