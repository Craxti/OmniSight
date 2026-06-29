from __future__ import annotations

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.services.base.async_domain import AsyncDomainService
from src.services.domain.graph_layout import layout_positions


class AsyncGraphLayoutReadService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)

    async def get_layout(self, root_ci_id: int, relation_filter: str) -> dict:
        await self._bundle.ci.get_or_404(root_ci_id)
        row = await self._bundle.graph_layout.get(root_ci_id, relation_filter)
        return layout_positions(row)
