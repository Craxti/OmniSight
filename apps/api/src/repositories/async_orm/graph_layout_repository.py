from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.graph_layout import GraphLayout
from src.repositories.async_base import AsyncRepository
from src.repositories.graph_layout_filter import normalize_relation_filter


class AsyncGraphLayoutRepository(AsyncRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get(self, root_ci_id: int, relation_filter: str) -> GraphLayout | None:
        key = normalize_relation_filter(relation_filter)
        stmt = select(GraphLayout).where(
            GraphLayout.root_ci_id == root_ci_id,
            GraphLayout.relation_filter == key,
        )
        return await self.scalar_one_or_none(stmt)

    async def merge_positions(
        self,
        root_ci_id: int,
        relation_filter: str,
        positions: dict[str, dict],
        updated_by: str | None,
    ) -> GraphLayout:
        key = normalize_relation_filter(relation_filter)
        row = await self.get(root_ci_id, key)
        if row:
            row.positions = {**(row.positions or {}), **positions}
            row.updated_by = updated_by
        else:
            row = GraphLayout(
                root_ci_id=root_ci_id,
                relation_filter=key,
                positions=positions,
                updated_by=updated_by,
            )
            self.session.add(row)
        await self.session.flush()
        return row

    async def delete(self, root_ci_id: int, relation_filter: str) -> bool:
        row = await self.get(root_ci_id, relation_filter)
        if not row:
            return False
        await self.session.delete(row)
        return True
