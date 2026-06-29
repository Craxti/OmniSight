"""RSM graph algorithms — internal sync implementation for parity tests."""

from __future__ import annotations

from sqlalchemy.orm import Session
from src.repositories.protocols import CiRepositoryProtocol, RelationRepositoryProtocol
from src.schemas.relations import RelationResponse
from src.schemas.resources import BusinessPathResponse, ComponentsResponse, ImpactResponse, ResourceGraphResponse
from src.services.rsm.lookup import get_ci_or_404
from src.services.rsm.topology import (
    find_business_path_directed,
    find_components_below,
    find_impacted_business_services,
)
from src.services.rsm.topology_algorithms import build_resource_graph_panel


def build_graph(
    db: Session,
    root_id: int,
    depth: int = 2,
    *,
    ci_repo: CiRepositoryProtocol,
    rel_repo: RelationRepositoryProtocol,
) -> ResourceGraphResponse:
    return build_resource_graph_panel(
        root_id=root_id,
        depth=depth,
        get_active=ci_repo.get_active,
        relations_for_ci=rel_repo.for_ci,
    )


def get_direct_relations(
    db: Session,
    ci_id: int,
    *,
    rel_repo: RelationRepositoryProtocol,
) -> list[RelationResponse]:
    from src.core.serializers import relation_to_response

    return [relation_to_response(r) for r in rel_repo.for_ci(ci_id)]


def compute_impact(
    db: Session,
    ci_id: int,
    *,
    ci_repo: CiRepositoryProtocol,
    rel_repo: RelationRepositoryProtocol,
) -> ImpactResponse:
    get_ci_or_404(db, ci_id, ci_repo=ci_repo)
    impacted = find_impacted_business_services(db, ci_id, ci_repo=ci_repo, rel_repo=rel_repo)
    return ImpactResponse(ci_id=ci_id, impacted_business_services=impacted, count=len(impacted))


def compute_components(
    db: Session,
    ci_id: int,
    *,
    ci_repo: CiRepositoryProtocol,
    rel_repo: RelationRepositoryProtocol,
) -> ComponentsResponse:
    components = find_components_below(db, ci_id, ci_repo=ci_repo, rel_repo=rel_repo)
    return ComponentsResponse(ci_id=ci_id, components=components, count=len(components))


def find_business_path(
    db: Session,
    ci_id: int,
    *,
    ci_repo: CiRepositoryProtocol,
    rel_repo: RelationRepositoryProtocol,
) -> BusinessPathResponse:
    return BusinessPathResponse(
        path=find_business_path_directed(db, ci_id, ci_repo=ci_repo, rel_repo=rel_repo),
    )
