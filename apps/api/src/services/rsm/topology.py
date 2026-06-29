"""Directed dependency topology for impact, components, chain_related (FR 17, 18, 39).

Internal algorithms — use ``TopologyService`` as the public entry point.
"""

from sqlalchemy.orm import Session
from src.core.serializers import ci_to_response
from src.repositories.protocols import CiRepositoryProtocol, RelationRepositoryProtocol
from src.schemas.ci import CIResponse
from src.schemas.resources import ImpactedServiceItem
from src.services.rsm.lookup import get_ci_or_404, is_business_service
from src.services.rsm.topology_algorithms import (
    BUSINESS_PATH_MAX_HOPS,
    CHAIN_RELATION_TYPES,
    DEPENDENCY_TYPES,
    business_path_extend,
    component_ids_below,
    filter_non_business_ci_ids,
    impacted_dependent_ids,
    root_cause_candidate_ids,
    to_impacted_business_services,
)
from src.services.rsm.topology_algorithms import (
    on_same_dependency_chain as resources_on_same_chain,
)


def _load_dependency_edges(
    db: Session,
    *,
    ci_ids: set[int] | None = None,
    relation_types: tuple[str, ...] = DEPENDENCY_TYPES,
    rel_repo: RelationRepositoryProtocol,
) -> tuple[dict[int, set[int]], dict[int, set[int]]]:
    return rel_repo.dependency_adjacency(ci_ids=ci_ids, relation_types=relation_types)


def on_same_dependency_chain(
    db: Session,
    resource_ids: list[int],
    *,
    rel_repo: RelationRepositoryProtocol,
) -> bool:
    """FR 39: all resources lie on one directed depends_on chain."""
    if len(resource_ids) <= 1:
        return True
    ids = set(resource_ids)
    forward, reverse = rel_repo.dependency_adjacency(ci_ids=ids, relation_types=CHAIN_RELATION_TYPES)
    return resources_on_same_chain(resource_ids, forward, reverse)


def find_impacted_business_services(
    db: Session,
    ci_id: int,
    *,
    ci_repo: CiRepositoryProtocol,
    rel_repo: RelationRepositoryProtocol,
) -> list[ImpactedServiceItem]:
    _, reverse = _load_dependency_edges(db, relation_types=CHAIN_RELATION_TYPES, rel_repo=rel_repo)
    dependents = impacted_dependent_ids(ci_id, reverse)
    if not dependents:
        return []
    return to_impacted_business_services(ci_repo.list_in_ids(dependents))


def find_component_ids_below(
    db: Session,
    ci_id: int,
    *,
    ci_repo: CiRepositoryProtocol,
    rel_repo: RelationRepositoryProtocol,
) -> set[int]:
    root = get_ci_or_404(db, ci_id, ci_repo=ci_repo)
    if not is_business_service(root):
        return set()
    forward, _ = _load_dependency_edges(db, relation_types=CHAIN_RELATION_TYPES, rel_repo=rel_repo)
    below = component_ids_below(ci_id, forward)
    if not below:
        return set()
    return filter_non_business_ci_ids(ci_repo.list_in_ids(below))


def find_components_below(
    db: Session,
    ci_id: int,
    *,
    ci_repo: CiRepositoryProtocol,
    rel_repo: RelationRepositoryProtocol,
) -> list[CIResponse]:
    below_ids = find_component_ids_below(db, ci_id, ci_repo=ci_repo, rel_repo=rel_repo)
    if not below_ids:
        return []
    return [ci_to_response(c) for c in ci_repo.list_in_ids(below_ids)]


def find_business_path_directed(
    db: Session,
    ci_id: int,
    *,
    ci_repo: CiRepositoryProtocol,
    rel_repo: RelationRepositoryProtocol,
) -> list[CIResponse]:
    ci = get_ci_or_404(db, ci_id, ci_repo=ci_repo)
    path = [ci_to_response(ci)]
    if is_business_service(ci):
        return path
    current_ids = {ci_id}
    visited = {ci_id}
    for _ in range(BUSINESS_PATH_MAX_HOPS):
        rels = rel_repo.list_incoming_with_source(current_ids, DEPENDENCY_TYPES)
        if not rels:
            break
        path, next_ids, done = business_path_extend(path, visited, rels)
        if done:
            return path
        if not next_ids:
            break
        current_ids = next_ids
    return path


def find_root_cause_candidates(
    db: Session,
    resource_ids: list[int],
    *,
    ci_repo: CiRepositoryProtocol,
    rel_repo: RelationRepositoryProtocol,
) -> list[CIResponse]:
    if not resource_ids:
        return []
    ids = set(resource_ids)
    forward, _ = _load_dependency_edges(
        db,
        ci_ids=ids,
        relation_types=CHAIN_RELATION_TYPES,
        rel_repo=rel_repo,
    )
    leaves = root_cause_candidate_ids(resource_ids, forward)
    return [ci_to_response(c) for c in ci_repo.list_in_ids(set(leaves))]
