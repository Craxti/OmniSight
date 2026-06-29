from __future__ import annotations

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.services.base.async_domain import AsyncDomainService
from src.services.domain.relation_types import list_relation_type_dicts


class AsyncRelationTypeReadService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)

    async def list_types(self) -> list[dict]:
        rows = await self._bundle.relation_types.list_ordered()
        return list_relation_type_dicts(rows)

    async def list_keys(self) -> list[str]:
        return await self._bundle.relation_types.list_keys()
