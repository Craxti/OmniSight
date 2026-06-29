"""Async integration outbox repository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import IntegrationOutbox
from src.repositories.async_base import AsyncRepository


class AsyncOutboxRepository(AsyncRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def fetch_retryable(self, *, limit: int, max_attempts: int) -> list[IntegrationOutbox]:
        stmt = (
            select(IntegrationOutbox)
            .where(
                IntegrationOutbox.status.in_(("pending", "failed")),
                IntegrationOutbox.attempts < max_attempts,
            )
            .order_by(IntegrationOutbox.created_at.asc())
            .limit(limit)
        )
        bind = self._db.get_bind()
        if bind is not None and bind.dialect.name == "postgresql":
            stmt = stmt.with_for_update(skip_locked=True)
        return await self.scalars_all(stmt)
