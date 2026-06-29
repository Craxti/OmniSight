"""Async audit logging for import batches."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from src.models import User
from src.repositories.async_orm.audit_repository import AsyncAuditRepository
from src.schemas.common import ImportReport


async def log_import_audit_async(
    session: AsyncSession,
    audit_repo: AsyncAuditRepository,
    user: User,
    action: str,
    report: ImportReport,
) -> None:
    await audit_repo.log(
        entity_type="import",
        entity_id=None,
        action=action,
        user_email=user.email,
        new_value=report.model_dump(),
    )
    await session.flush()
