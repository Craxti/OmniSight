from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.repositories.async_base import AsyncRepository


class AsyncUserRepository(AsyncRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_by_email(self, email: str) -> User | None:
        return await self.scalar_one_or_none(select(User).where(User.email == email))

    async def list_ordered(self) -> list[User]:
        return await self.scalars_all(select(User).order_by(User.email))

    async def count_admins(self) -> int:
        from sqlalchemy import func

        stmt = select(func.count()).select_from(User).where(User.role == "admin", User.is_active.is_(True))
        return int(await self.scalar_one(stmt))

    async def count_all(self) -> int:
        from sqlalchemy import func

        stmt = select(func.count()).select_from(User)
        return int(await self.scalar_one(stmt))
