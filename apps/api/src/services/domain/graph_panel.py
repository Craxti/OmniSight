"""Shared resource graph panel cache key and async BFS helper."""

from __future__ import annotations

from collections import deque
from collections.abc import Awaitable, Callable
from typing import Any

from src.core.serializers import relation_to_response
from src.schemas.relations import RelationResponse
from src.schemas.resources import ResourceGraphResponse
from src.services.rsm.topology_algorithms import build_resource_graph_panel, graph_node_for_ci

GRAPH_PANEL_CACHE_TTL = 30


def graph_panel_cache_key(root_id: int, depth: int) -> str:
    return f"graph:{root_id}:{depth}"


async def build_graph_panel_async(
    *,
    root_id: int,
    depth: int,
    get_active: Callable[[int], Awaitable[Any | None]],
    relations_for_ci: Callable[[int], Awaitable[list[Any]]],
) -> ResourceGraphResponse:
    visited_nodes: dict[int, Any] = {}
    visited_edges: dict[int, RelationResponse] = {}
    queue: deque[tuple[int, int]] = deque([(root_id, 0)])

    while queue:
        node_id, level = queue.popleft()
        if node_id in visited_nodes:
            continue
        ci = await get_active(node_id)
        if not ci:
            continue
        visited_nodes[node_id] = graph_node_for_ci(ci, level)
        if level >= depth:
            continue
        for rel in await relations_for_ci(node_id):
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


__all__ = [
    "GRAPH_PANEL_CACHE_TTL",
    "build_graph_panel_async",
    "build_resource_graph_panel",
    "graph_panel_cache_key",
]
