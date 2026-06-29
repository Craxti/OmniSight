"""Async correlation context builder."""

from __future__ import annotations

from src.repositories.async_orm.ci_repository import AsyncCiRepository
from src.repositories.async_orm.relation_repository import AsyncRelationRepository
from src.schemas.correlation import (
    CorrelationContextPayload,
    CorrelationEnrichmentItem,
    GraphDataResponse,
    GraphNodeResponse,
)
from src.schemas.relations import RelationResponse
from src.services.rsm.async_graph import async_build_graph, async_compute_impact, async_get_direct_relations
from src.services.rsm.async_topology import async_find_root_cause_candidates, async_on_same_dependency_chain
from src.services.rsm.indexed_ids import merge_external_ids


async def build_correlation_context_async(
    resource_ids: list[int],
    depth: int = 3,
    *,
    ci_repo: AsyncCiRepository,
    rel_repo: AsyncRelationRepository,
) -> CorrelationContextPayload:
    all_nodes: dict[int, GraphNodeResponse] = {}
    all_edges: dict[int, RelationResponse] = {}
    direct: list[RelationResponse] = []

    for rid in resource_ids:
        graph = await async_build_graph(ci_repo, rel_repo, rid, depth=depth)
        for node in graph.nodes:
            all_nodes[node.id] = node
        for edge in graph.edges:
            all_edges[edge.id] = edge
        direct.extend(await async_get_direct_relations(rel_repo, rid))

    enrichment: list[CorrelationEnrichmentItem] = []
    for rid in resource_ids:
        ci = await ci_repo.get_active(rid)
        if not ci:
            continue
        impact = await async_compute_impact(rid, ci_repo=ci_repo, rel_repo=rel_repo)
        enrichment.append(
            CorrelationEnrichmentItem(
                resource_id=rid,
                name=ci.name,
                type=ci.ci_type.name if ci.ci_type else None,
                criticality=ci.criticality,
                environment=ci.environment,
                owner=ci.owner,
                team=ci.team,
                external_ids=merge_external_ids(ci.attributes, ci.external_ids),
                impacted_services=[s.model_dump() for s in impact.impacted_business_services],
            )
        )

    return CorrelationContextPayload(
        resource_ids=resource_ids,
        chain_related=await async_on_same_dependency_chain(resource_ids, rel_repo=rel_repo),
        chain_algorithm="depends_on_directed",
        graph=GraphDataResponse(nodes=list(all_nodes.values()), edges=list(all_edges.values())),
        direct_relations=direct,
        potential_root_cause_zone=await async_find_root_cause_candidates(
            resource_ids,
            ci_repo=ci_repo,
            rel_repo=rel_repo,
        ),
        enrichment=enrichment,
    )
