from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Relation
from src.repositories.async_base import AsyncRepository
from src.repositories.queries.relations import (
    apply_relation_list_filters,
    build_adjacency_from_edges,
    dependency_adjacency_select,
    depends_on_edges_select,
    incoming_with_source_select,
    relation_active_base,
)


class AsyncRelationRepository(AsyncRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def count_active(self) -> int:
        stmt = select(func.count()).select_from(Relation).where(Relation.is_deleted.is_(False))
        return int(await self.scalar_one(stmt))

    async def get_active(self, relation_id: int) -> Relation | None:
        stmt = relation_active_base().where(Relation.id == relation_id)
        return await self.scalar_one_or_none(stmt)

    async def find_active(
        self,
        source_ci_id: int,
        target_ci_id: int,
        relation_type: str,
    ) -> Relation | None:
        stmt = relation_active_base().where(
            Relation.source_ci_id == source_ci_id,
            Relation.target_ci_id == target_ci_id,
            Relation.relation_type == relation_type,
            Relation.status != "archived",
        )
        return await self.scalar_one_or_none(stmt)

    async def list_active(self) -> list[Relation]:
        stmt = relation_active_base().order_by(Relation.id.desc())
        return await self.scalars_all(stmt)

    async def list_active_page(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        relation_type: str | None = None,
        status: str | None = None,
        data_source: str | None = None,
        source_name: str | None = None,
        target_name: str | None = None,
        q: str | None = None,
    ) -> tuple[list[Relation], int]:
        stmt = relation_active_base().order_by(Relation.id.desc())
        stmt = apply_relation_list_filters(
            stmt,
            relation_type=relation_type,
            status=status,
            data_source=data_source,
            source_name=source_name,
            target_name=target_name,
            q=q,
        )
        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        total = int((await self.execute(count_stmt)).scalar_one())
        rows = await self.scalars_all(stmt.offset(skip).limit(limit))
        return rows, total

    async def for_ci(self, ci_id: int) -> list[Relation]:
        stmt = relation_active_base().where((Relation.source_ci_id == ci_id) | (Relation.target_ci_id == ci_id))
        return await self.scalars_all(stmt)

    async def list_depends_on_edges(self) -> list[tuple[int, int]]:
        result = await self.execute(depends_on_edges_select())
        return [(row[0], row[1]) for row in result.all()]

    async def list_active_non_archived(self) -> list[Relation]:
        stmt = relation_active_base().where(Relation.status != "archived")
        return await self.scalars_all(stmt)

    async def list_incoming_with_source(
        self,
        target_ci_ids: set[int],
        relation_types: tuple[str, ...],
    ) -> list[Relation]:
        if not target_ci_ids:
            return []
        stmt = incoming_with_source_select(target_ci_ids, relation_types)
        return await self.scalars_all(stmt)

    async def dependency_adjacency(
        self,
        *,
        ci_ids: set[int] | None = None,
        relation_types: tuple[str, ...],
    ) -> tuple[dict[int, set[int]], dict[int, set[int]]]:
        result = await self.execute(dependency_adjacency_select(ci_ids=ci_ids, relation_types=relation_types))
        return build_adjacency_from_edges((row[0], row[1]) for row in result.all())

    async def touching_ci_ids(self, ci_ids: set[int]) -> list[Relation]:
        if not ci_ids:
            return []
        stmt = relation_active_base().where((Relation.source_ci_id.in_(ci_ids)) | (Relation.target_ci_id.in_(ci_ids)))
        return await self.scalars_all(stmt)

    async def delete_for_ci(self, ci_id: int) -> None:
        stmt = delete(Relation).where(
            (Relation.source_ci_id == ci_id) | (Relation.target_ci_id == ci_id),
        )
        await self.execute(stmt)
