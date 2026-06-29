"""Native async autodiscover scope resolution."""

from __future__ import annotations

from collections import deque

from src.repositories.async_orm.ci_repository import AsyncCiRepository
from src.repositories.async_orm.relation_repository import AsyncRelationRepository


async def graph_scope_ids_async(
    root_id: int,
    depth: int,
    *,
    rel_repo: AsyncRelationRepository,
) -> set[int]:
    if depth <= 0:
        return {root_id}
    visited: set[int] = set()
    queue: deque[tuple[int, int]] = deque([(root_id, 0)])
    while queue:
        node_id, level = queue.popleft()
        if node_id in visited:
            continue
        visited.add(node_id)
        if level >= depth:
            continue
        for rel in await rel_repo.for_ci(node_id):
            neighbor = rel.target_ci_id if rel.source_ci_id == node_id else rel.source_ci_id
            if neighbor not in visited:
                queue.append((neighbor, level + 1))
    return visited


async def resolve_scope_ci_ids_async(
    *,
    scope_mode: str,
    scope_config: dict,
    server_ci_ids: list[int],
    ci_repo: AsyncCiRepository,
    rel_repo: AsyncRelationRepository,
) -> set[int]:
    if scope_mode == "all":
        return await ci_repo.list_active_ids()
    if scope_mode == "filters":
        return await ci_repo.list_filtered_ids(
            environment=scope_config.get("environment"),
            owner=scope_config.get("owner"),
            type_id=int(scope_config["type_id"]) if scope_config.get("type_id") else None,
        )
    depth = int(scope_config.get("depth", 2))
    root_id = scope_config.get("root_ci_id")
    if root_id:
        return await graph_scope_ids_async(int(root_id), depth, rel_repo=rel_repo)
    scope: set[int] = set()
    for server_id in server_ci_ids:
        scope |= await graph_scope_ids_async(server_id, depth, rel_repo=rel_repo)
    return scope
