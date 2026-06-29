from __future__ import annotations

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.schemas.ci import CIDetailResponse, CIListResponse, CIResponse
from src.services.base.async_domain import AsyncDomainService
from src.services.domain.ci import ci_detail_async, list_ci_async, list_recycle_bin_async


class AsyncCiReadService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)

    async def list_ci(self, **kwargs) -> CIListResponse:
        type_id = kwargs.pop("type_id", None)
        skip = kwargs.pop("skip", 0)
        limit = kwargs.pop("limit", 50)
        return await list_ci_async(
            self._bundle.ci,
            self._bundle.ci_types,
            skip=skip,
            limit=limit,
            type_id=type_id,
            **kwargs,
        )

    async def get_ci_detail(self, ci_id: int) -> CIDetailResponse:
        return await ci_detail_async(self._bundle.ci, ci_id)

    async def list_recycle_bin(self) -> list[CIResponse]:
        return await list_recycle_bin_async(self._bundle.ci)
