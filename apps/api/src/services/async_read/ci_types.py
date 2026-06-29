from __future__ import annotations

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.services.base.async_domain import AsyncDomainService
from src.services.domain.ci_types import list_type_dicts


class AsyncCiTypeReadService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)

    async def list_types(self) -> list[dict]:
        types = await self._bundle.ci_types.list_ordered()
        return list_type_dicts(types)
