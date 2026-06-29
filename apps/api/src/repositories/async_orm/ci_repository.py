"""Async CI read repository — native ``await session.execute(select(...))``."""

from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.exceptions import NotFoundError
from src.models import CI
from src.repositories.async_base import AsyncRepository
from src.repositories.queries.ci import (
    ci_base_select,
    ci_detail_select,
    ci_search_count_select,
    ci_search_select,
)


class AsyncCiRepository(AsyncRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_active(self, ci_id: int) -> CI | None:
        stmt = ci_base_select().where(CI.id == ci_id)
        return await self.scalar_one_or_none(stmt)

    async def get_or_404(self, ci_id: int, *, include_deleted: bool = False) -> CI:
        if include_deleted:
            stmt = select(CI).options(joinedload(CI.ci_type)).where(CI.id == ci_id)
            ci = await self.scalar_one_or_none(stmt)
        else:
            ci = await self.get_active(ci_id)
        if not ci:
            raise NotFoundError("CI not found")
        return ci

    async def get_detail_or_404(self, ci_id: int, *, include_deleted: bool = False) -> CI:
        ci = await self.scalar_one_or_none(ci_detail_select(ci_id, include_deleted=include_deleted))
        if not ci:
            raise NotFoundError("CI not found")
        return ci

    async def search(self, **kwargs) -> tuple[list[CI], int]:
        filter_kwargs = {k: v for k, v in kwargs.items() if k not in ("skip", "limit", "sort_by", "sort_dir")}
        total = await self.scalar_one(ci_search_count_select(**filter_kwargs))
        rows = await self.scalars_all(ci_search_select(**kwargs))
        return rows, int(total)

    async def list_deleted(self) -> list[CI]:
        stmt = ci_base_select(include_deleted=True).where(CI.is_deleted.is_(True))
        return await self.scalars_all(stmt)

    async def list_active(self, *, limit: int = 10_000) -> list[CI]:
        stmt = ci_base_select().limit(limit)
        return await self.scalars_all(stmt)

    async def count_active(self) -> int:
        stmt = select(func.count()).select_from(CI).where(CI.is_deleted.is_(False))
        return int(await self.scalar_one(stmt))

    async def count_active_by_status(self, status: str) -> int:
        stmt = select(func.count()).select_from(CI).where(CI.is_deleted.is_(False), CI.status == status)
        return int(await self.scalar_one(stmt))

    async def count_active_by_type_name(self) -> dict[str, int]:
        from src.models import CIType

        stmt = (
            select(CIType.name, func.count(CI.id))
            .join(CI, CI.type_id == CIType.id)
            .where(CI.is_deleted.is_(False))
            .group_by(CIType.name)
        )
        result = await self.execute(stmt)
        return {name: count for name, count in result.all()}

    async def list_in_ids(
        self,
        ci_ids: set[int],
        *,
        environment: str | None = None,
        owner: str | None = None,
    ) -> list[CI]:
        if not ci_ids:
            return []
        stmt = ci_base_select().where(CI.id.in_(ci_ids))
        if environment:
            stmt = stmt.where(CI.environment == environment)
        if owner:
            stmt = stmt.where(CI.owner.ilike(f"%{owner}%"))
        return await self.scalars_all(stmt)

    async def find_for_alert_conditions(self, conditions: list) -> list[CI]:
        if not conditions:
            return []
        stmt = ci_base_select().where(or_(*conditions))
        return await self.scalars_all(stmt)

    async def list_active_ids(self) -> set[int]:
        stmt = select(CI.id).where(CI.is_deleted.is_(False))
        result = await self.execute(stmt)
        return {row[0] for row in result.all()}

    async def list_filtered_ids(
        self,
        *,
        environment: str | None = None,
        owner: str | None = None,
        type_id: int | None = None,
    ) -> set[int]:
        stmt = select(CI.id).where(CI.is_deleted.is_(False))
        if environment:
            stmt = stmt.where(CI.environment == environment)
        if owner:
            stmt = stmt.where(CI.owner == owner)
        if type_id:
            stmt = stmt.where(CI.type_id == type_id)
        result = await self.execute(stmt)
        return {row[0] for row in result.all()}

    async def count_active_by_type(self, type_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(CI)
            .where(
                CI.type_id == type_id,
                CI.is_deleted.is_(False),
            )
        )
        return int(await self.scalar_one(stmt))

    async def list_recycled_by_type(self, type_id: int) -> list[CI]:
        stmt = select(CI).where(CI.type_id == type_id, CI.is_deleted.is_(True))
        return await self.scalars_all(stmt)

    async def name_exists(self, name: str, *, exclude_id: int | None = None) -> bool:
        stmt = select(CI.id).where(CI.name == name, CI.is_deleted.is_(False))
        if exclude_id is not None:
            stmt = stmt.where(CI.id != exclude_id)
        return (await self.scalar_one_or_none(stmt)) is not None

    async def get_by_name(self, name: str, *, include_deleted: bool = False) -> CI | None:
        stmt = ci_base_select(include_deleted=include_deleted).where(CI.name == name)
        return await self.scalar_one_or_none(stmt)

    async def find_by_search_field(
        self,
        field: str,
        value: str,
        *,
        exclude_ci_id: int | None = None,
    ) -> CI | None:
        col = getattr(CI, field, None)
        if col is None:
            return None
        stmt = ci_base_select().where(col == value)
        if exclude_ci_id is not None:
            stmt = stmt.where(CI.id != exclude_ci_id)
        return await self.scalar_one_or_none(stmt)

    async def next_unique_name(self, base: str) -> str:
        name = base
        suffix = 1
        while await self.name_exists(name):
            suffix += 1
            name = f"{base}-{suffix}"
        return name

    async def find_by_identifier(self, identifier: str) -> CI | None:
        key = identifier.strip()
        if not key:
            return None
        for column in (
            CI.search_hostname,
            CI.name,
            CI.search_ip,
            CI.search_service_code,
            CI.search_application_code,
            CI.search_external_id,
        ):
            stmt = ci_base_select().where(column == key)
            ci = await self.scalar_one_or_none(stmt)
            if ci:
                return ci
        for column in (CI.search_hostname, CI.name):
            stmt = ci_base_select().where(column.ilike(key))
            ci = await self.scalar_one_or_none(stmt)
            if ci:
                return ci
        if "." in key:
            short = key.split(".")[0]
            if short != key:
                return await self.find_by_identifier(short)
        return None

    async def archived_active_ids(self) -> set[int]:
        stmt = select(CI.id).where(CI.is_deleted.is_(False), CI.status == "archived")
        result = await self.execute(stmt)
        return {row[0] for row in result.all()}
