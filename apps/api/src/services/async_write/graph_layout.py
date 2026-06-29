"""Native async graph layout write service."""

from __future__ import annotations

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.services.base.async_domain import AsyncDomainService
from src.services.domain.topology import ensure_ci_exists_async


class AsyncGraphLayoutWriteService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)
        self._repo = bundle.graph_layout
        self._ci = bundle.ci

    async def merge_layout(
        self,
        root_ci_id: int,
        relation_filter: str,
        positions: dict[str, dict],
        updated_by: str | None,
    ) -> dict:
        await ensure_ci_exists_async(self._ci, root_ci_id)
        row = await self._repo.merge_positions(root_ci_id, relation_filter, positions, updated_by)
        await self._session.commit()
        await self._session.refresh(row)
        return row.positions or {}

    async def clear_layout(self, root_ci_id: int, relation_filter: str) -> None:
        await ensure_ci_exists_async(self._ci, root_ci_id)
        if await self._repo.delete(root_ci_id, relation_filter):
            await self._session.commit()
