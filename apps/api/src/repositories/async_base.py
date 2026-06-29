"""Async SQLAlchemy repository helpers (``await session.execute(select(...))``)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession


class AsyncRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    @property
    def session(self) -> AsyncSession:
        return self._db

    async def execute(self, stmt):
        return await self._db.execute(stmt)

    async def scalar_one(self, stmt: Select) -> Any:
        result = await self._db.execute(stmt)
        return result.scalar_one()

    async def scalar_one_or_none(self, stmt: Select) -> Any:
        result = await self._db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def scalars_all(self, stmt: Select) -> list[Any]:
        result = await self._db.execute(stmt)
        return list(result.unique().scalars().all())

    async def count_select(self, stmt: Select) -> int:
        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        result = await self._db.execute(count_stmt)
        return int(result.scalar_one())
