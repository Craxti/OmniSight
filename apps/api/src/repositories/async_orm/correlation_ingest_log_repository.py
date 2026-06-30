from __future__ import annotations

from sqlalchemy import case, func, select
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

    async def aggregate_stats(self, *, source: str | None = None) -> dict[str, int | float]:
        filters = []
        if source:
            filters.append(CorrelationIngestLog.source == source)
        base = select(
            func.count(CorrelationIngestLog.id).label("total_batches"),
            func.coalesce(func.sum(CorrelationIngestLog.alert_count), 0).label("total_alerts"),
            func.coalesce(func.sum(CorrelationIngestLog.resolved_count), 0).label("total_resolved"),
            func.coalesce(func.sum(CorrelationIngestLog.unresolved_count), 0).label("total_unresolved"),
            func.coalesce(
                func.sum(case((CorrelationIngestLog.chain_related.is_(True), 1), else_=0)),
                0,
            ).label("chain_related_count"),
        ).select_from(CorrelationIngestLog)
        if filters:
            base = base.where(*filters)
        row = (await self.execute(base)).one()
        total_alerts = int(row.total_alerts)
        total_resolved = int(row.total_resolved)
        total_batches = int(row.total_batches)
        chain_related_count = int(row.chain_related_count)
        resolve_rate = round(100.0 * total_resolved / total_alerts, 1) if total_alerts else 0.0
        chain_pct = round(100.0 * chain_related_count / total_batches, 1) if total_batches else 0.0
        return {
            "total_batches": total_batches,
            "total_alerts": total_alerts,
            "total_resolved": total_resolved,
            "total_unresolved": int(row.total_unresolved),
            "resolve_rate_pct": resolve_rate,
            "chain_related_count": chain_related_count,
            "chain_related_pct": chain_pct,
        }
