"""Topology read adapters.

Graph BFS and path/impact algorithms live in ``services/rsm/topology_algorithms.py``
(sync via ``services/rsm/graph`` + ``topology``, async via ``async_graph`` + ``async_topology``).
"""

from __future__ import annotations

from typing import Any, Protocol


class CiExistsRepo(Protocol):
    def get_or_404(self, ci_id: int) -> Any: ...


async def ensure_ci_exists_async(ci_repo: Any, resource_id: int) -> None:
    await ci_repo.get_or_404(resource_id)


def ensure_ci_exists_sync(db: Any, resource_id: int, *, ci_repo: Any) -> None:
    from src.services.rsm.lookup import get_ci_or_404

    get_ci_or_404(db, resource_id, ci_repo=ci_repo)
