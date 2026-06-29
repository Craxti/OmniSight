"""Async depends_on cycle detection for native write paths."""

from __future__ import annotations

from collections import deque

from src.repositories.async_orm.relation_repository import AsyncRelationRepository


async def would_create_depends_on_cycle_async(
    rel_repo: AsyncRelationRepository,
    source_id: int,
    target_id: int,
) -> bool:
    forward: dict[int, set[int]] = {}
    for src, tgt in await rel_repo.list_depends_on_edges():
        forward.setdefault(src, set()).add(tgt)
    seen = {target_id}
    queue: deque[int] = deque([target_id])
    while queue:
        node = queue.popleft()
        for nxt in forward.get(node, ()):
            if nxt == source_id:
                return True
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return False
