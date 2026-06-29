"""Pure topology/graph algorithms shared by sync and async RSM paths."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterable, Sequence
from typing import Any

from src.core.serializers import ci_to_response, relation_to_response
from src.schemas.ci import CIResponse
from src.schemas.correlation import GraphNodeResponse
from src.schemas.relations import RelationResponse
from src.schemas.resources import ImpactedServiceItem, ResourceGraphResponse
from src.services.rsm.lookup import is_business_service

DEPENDENCY_TYPES: tuple[str, ...] = ("depends_on", "uses", "hosted_on", "part_of")
CHAIN_RELATION_TYPES: tuple[str, ...] = ("depends_on",)
BUSINESS_PATH_MAX_HOPS = 20


def bfs_reachable(start: int, adj: dict[int, set[int]]) -> set[int]:
    seen = {start}
    queue: deque[int] = deque([start])
    while queue:
        node = queue.popleft()
        for nxt in adj.get(node, ()):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def on_same_dependency_chain(
    resource_ids: list[int],
    forward: dict[int, set[int]],
    reverse: dict[int, set[int]],
) -> bool:
    if len(resource_ids) <= 1:
        return True
    ids = set(resource_ids)
    combined: dict[int, set[int]] = {node: set() for node in ids}
    for node in ids:
        for nxt in forward.get(node, ()):
            if nxt in ids:
                combined[node].add(nxt)
                combined[nxt].add(node)
        for prev in reverse.get(node, ()):
            if prev in ids:
                combined[prev].add(node)
                combined[node].add(prev)
    for i, a in enumerate(resource_ids):
        for b in resource_ids[i + 1 :]:
            if b not in bfs_reachable(a, combined):
                return False
    return True


def impacted_dependent_ids(ci_id: int, reverse: dict[int, set[int]]) -> set[int]:
    return bfs_reachable(ci_id, reverse) - {ci_id}


def to_impacted_business_services(cis: Iterable[Any]) -> list[ImpactedServiceItem]:
    return [
        ImpactedServiceItem(id=c.id, name=c.name, criticality=c.criticality)
        for c in cis
        if c.ci_type and c.ci_type.name == "Business Service"
    ]


def component_ids_below(ci_id: int, forward: dict[int, set[int]]) -> set[int]:
    return bfs_reachable(ci_id, forward) - {ci_id}


def filter_non_business_ci_responses(cis: Iterable[Any]) -> list[CIResponse]:
    return [ci_to_response(c) for c in cis if not is_business_service(c)]


def filter_non_business_ci_ids(cis: Iterable[Any]) -> set[int]:
    return {c.id for c in cis if not is_business_service(c)}


def root_cause_candidate_ids(resource_ids: list[int], forward: dict[int, set[int]]) -> list[int]:
    if not resource_ids:
        return []
    ids = set(resource_ids)
    leaves = [rid for rid in resource_ids if not any(tgt in ids for tgt in forward.get(rid, ()))]
    return leaves if leaves else list(resource_ids)


def business_path_extend(
    path: list[CIResponse],
    visited: set[int],
    rels: Sequence[Any],
) -> tuple[list[CIResponse], set[int], bool]:
    """Walk one hop up dependency edges. Returns (path, next_source_ids, reached_business_service)."""
    next_ids: set[int] = set()
    for rel in rels:
        source = rel.source_ci
        if not source or getattr(source, "is_deleted", False) or source.id in visited:
            continue
        path.append(ci_to_response(source))
        visited.add(source.id)
        next_ids.add(source.id)
        if is_business_service(source):
            return path, next_ids, True
    return path, next_ids, False


def graph_node_for_ci(ci: Any, level: int) -> GraphNodeResponse:
    return GraphNodeResponse(**{**ci_to_response(ci).model_dump(), "depth": level})


def build_resource_graph_panel(
    *,
    root_id: int,
    depth: int,
    get_active: Callable[[int], Any | None],
    relations_for_ci: Callable[[int], list[Any]],
) -> ResourceGraphResponse:
    visited_nodes: dict[int, GraphNodeResponse] = {}
    visited_edges: dict[int, RelationResponse] = {}
    queue: deque[tuple[int, int]] = deque([(root_id, 0)])

    while queue:
        node_id, level = queue.popleft()
        if node_id in visited_nodes:
            continue
        ci = get_active(node_id)
        if not ci:
            continue
        visited_nodes[node_id] = graph_node_for_ci(ci, level)
        if level >= depth:
            continue
        for rel in relations_for_ci(node_id):
            visited_edges[rel.id] = relation_to_response(rel)
            neighbor = rel.target_ci_id if rel.source_ci_id == node_id else rel.source_ci_id
            if neighbor not in visited_nodes:
                queue.append((neighbor, level + 1))

    return ResourceGraphResponse(
        root_id=root_id,
        depth=depth,
        nodes=list(visited_nodes.values()),
        edges=list(visited_edges.values()),
    )
