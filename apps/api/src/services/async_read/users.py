from __future__ import annotations

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.schemas.auth import UserResponse
from src.services.base.async_domain import AsyncDomainService
from src.services.domain.users import list_user_responses


class AsyncUserReadService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)

    async def list_users(self) -> list[UserResponse]:
        users = await self._bundle.users.list_ordered()
        return list_user_responses(users)
