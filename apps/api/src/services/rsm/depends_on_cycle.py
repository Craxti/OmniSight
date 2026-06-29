"""depends_on cycle detection — single implementation for import and model validation."""

from __future__ import annotations

from collections import deque

from sqlalchemy.orm import Session
from src.repositories.protocols import RelationRepositoryProtocol


def build_depends_on_forward(
    db: Session,
    *,
    rel_repo: RelationRepositoryProtocol,
) -> dict[int, set[int]]:
    forward: dict[int, set[int]] = {}
    for src, tgt in rel_repo.list_depends_on_edges():
        forward.setdefault(src, set()).add(tgt)
    return forward


def would_create_depends_on_cycle(
    db: Session,
    source_id: int,
    target_id: int,
    *,
    rel_repo: RelationRepositoryProtocol,
) -> bool:
    """True if adding source depends_on target creates a cycle."""
    forward = build_depends_on_forward(db, rel_repo=rel_repo)
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


def find_depends_on_cycle_start(adj: dict[int, list[int]]) -> int | None:
    """Return a CI id where a depends_on cycle exists, or None."""

    def has_cycle(start: int) -> bool:
        stack = [(start, [start])]
        while stack:
            node, trail = stack.pop()
            for nxt in adj.get(node, []):
                if nxt in trail:
                    return True
                stack.append((nxt, trail + [nxt]))
        return False

    for node in adj:
        if has_cycle(node):
            return node
    return None
