from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundError
from src.models import CIType
from src.repositories.async_base import AsyncRepository


class AsyncCITypeRepository(AsyncRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_by_id(self, type_id: int) -> CIType | None:
        return await self.scalar_one_or_none(select(CIType).where(CIType.id == type_id))

    async def get_by_name(self, name: str) -> CIType | None:
        return await self.scalar_one_or_none(select(CIType).where(CIType.name == name))

    async def list_ordered(self) -> list[CIType]:
        return await self.scalars_all(select(CIType).order_by(CIType.name))

    async def require_by_id(self, type_id: int) -> CIType:
        row = await self.get_by_id(type_id)
        if not row:
            raise NotFoundError("CI type not found")
        return row

    async def require_by_name(self, name: str) -> CIType:
        row = await self.get_by_name(name)
        if not row:
            raise NotFoundError(f"CI type '{name}' not found")
        return row

    async def name_taken(self, name: str, *, exclude_id: int | None = None) -> bool:
        stmt = select(CIType.id).where(CIType.name == name)
        if exclude_id is not None:
            stmt = stmt.where(CIType.id != exclude_id)
        return (await self.scalar_one_or_none(stmt)) is not None

    async def get_or_raise(self, type_id: int) -> CIType:
        row = await self.get_by_id(type_id)
        if not row:
            raise NotFoundError("Type not found")
        return row
