from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import AuditLog
from src.repositories.async_base import AsyncRepository
from src.repositories.queries.audit import (
    apply_audit_search_filters,
    audit_for_ci_with_relations_select,
    audit_for_entity_select,
    audit_search_base,
    relation_ids_for_ci_select,
)


class AsyncAuditRepository(AsyncRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def search(
        self,
        *,
        entity_type: str | None = None,
        action: str | None = None,
        user_email: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[AuditLog], int]:
        stmt = apply_audit_search_filters(
            audit_search_base(),
            entity_type=entity_type,
            action=action,
            user_email=user_email,
            date_from=date_from,
            date_to=date_to,
        )
        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        total = int((await self.execute(count_stmt)).scalar_one())
        items = await self.scalars_all(stmt.offset(skip).limit(limit))
        return items, total

    async def for_entity(self, entity_type: str, entity_id: int, *, limit: int = 50) -> list[AuditLog]:
        return await self.scalars_all(audit_for_entity_select(entity_type, entity_id, limit=limit))

    async def for_ci_with_relations(self, ci_id: int, *, limit: int = 50) -> list[AuditLog]:
        rel_result = await self.execute(relation_ids_for_ci_select(ci_id))
        relation_ids = [row[0] for row in rel_result.all()]
        return await self.scalars_all(audit_for_ci_with_relations_select(ci_id, relation_ids, limit=limit))

    async def list_recent(self, *, limit: int = 50, offset: int = 0) -> list[AuditLog]:
        stmt = select(AuditLog).order_by(AuditLog.id.desc()).offset(offset).limit(limit)
        return await self.scalars_all(stmt)

    async def log(
        self,
        *,
        entity_type: str,
        entity_id: int | None,
        action: str,
        user_email: str | None,
        old_value: dict | None = None,
        new_value: dict | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_email=user_email,
            old_value=old_value,
            new_value=new_value,
        )
        self._db.add(entry)
        await self._db.flush()
        return entry
