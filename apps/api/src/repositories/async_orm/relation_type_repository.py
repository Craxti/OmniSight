from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundError
from src.models.relation_type import RelationType
from src.repositories.async_base import AsyncRepository


class AsyncRelationTypeRepository(AsyncRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_by_id(self, type_id: int) -> RelationType | None:
        return await self.scalar_one_or_none(select(RelationType).where(RelationType.id == type_id))

    async def get_by_name(self, name: str) -> RelationType | None:
        return await self.scalar_one_or_none(select(RelationType).where(RelationType.name == name))

    async def list_ordered(self) -> list[RelationType]:
        return await self.scalars_all(select(RelationType).order_by(RelationType.name))

    async def get_or_raise(self, type_id: int) -> RelationType:
        row = await self.get_by_id(type_id)
        if not row:
            raise NotFoundError("Relation type not found")
        return row

    async def name_taken(self, name: str, *, exclude_id: int | None = None) -> bool:
        stmt = select(RelationType.id).where(RelationType.name == name)
        if exclude_id is not None:
            stmt = stmt.where(RelationType.id != exclude_id)
        return (await self.scalar_one_or_none(stmt)) is not None

    async def list_keys(self) -> list[str]:
        rows = await self.list_ordered()
        return [row.name for row in rows]
