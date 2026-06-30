from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundError
from src.models import CorrelationIngestLog
from src.repositories.async_base import AsyncRepository


class AsyncCorrelationIngestLogRepository(AsyncRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def create(
        self,
        *,
        source: str | None,
        alerts: list,
        result: dict,
        alert_count: int,
        resolved_count: int,
        unresolved_count: int,
        chain_related: bool,
    ) -> CorrelationIngestLog:
        entry = CorrelationIngestLog(
            source=source,
            alerts=alerts,
            result=result,
            alert_count=alert_count,
            resolved_count=resolved_count,
            unresolved_count=unresolved_count,
            chain_related=chain_related,
        )
        self._db.add(entry)
        await self._db.flush()
        return entry

    async def get_by_id(self, log_id: int) -> CorrelationIngestLog | None:
        return await self.scalar_one_or_none(select(CorrelationIngestLog).where(CorrelationIngestLog.id == log_id))

    async def get_or_404(self, log_id: int) -> CorrelationIngestLog:
        row = await self.get_by_id(log_id)
        if row is None:
            raise NotFoundError("Correlation ingest log not found")
        return row

    async def list_recent(
        self,
        *,
        source: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[CorrelationIngestLog], int]:
        stmt = select(CorrelationIngestLog).order_by(CorrelationIngestLog.id.desc())
        if source:
            stmt = stmt.where(CorrelationIngestLog.source == source)
        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        total = int((await self.execute(count_stmt)).scalar_one())
        items = await self.scalars_all(stmt.offset(skip).limit(limit))
        return items, total
