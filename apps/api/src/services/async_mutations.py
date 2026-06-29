"""Async mutation side-effects (audit trail, cache invalidation, commit)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from src.core.cache import cache_invalidate_prefix_async
from src.repositories.async_orm.audit_repository import AsyncAuditRepository

T = TypeVar("T")


async def log_entity_mutation_async(
    session: AsyncSession,
    audit_repo: AsyncAuditRepository,
    *,
    entity_type: str,
    entity_id: int | None,
    action: str,
    user_email: str | None,
    old_value: dict[str, Any] | None = None,
    new_value: dict[str, Any] | None = None,
    cache_prefix: str | Sequence[str] | None = None,
) -> None:
    if cache_prefix:
        prefixes = [cache_prefix] if isinstance(cache_prefix, str) else cache_prefix
        for prefix in prefixes:
            await cache_invalidate_prefix_async(prefix)
    await audit_repo.log(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        user_email=user_email,
        old_value=old_value,
        new_value=new_value,
    )


async def commit_entity_mutation_async(
    session: AsyncSession,
    audit_repo: AsyncAuditRepository,
    entity: T,
    *,
    entity_type: str,
    entity_id: int | None,
    action: str,
    user_email: str | None,
    old_value: dict[str, Any] | None = None,
    new_value: dict[str, Any] | None = None,
    cache_prefix: str | Sequence[str] | None = None,
) -> T:
    await log_entity_mutation_async(
        session,
        audit_repo,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        user_email=user_email,
        old_value=old_value,
        new_value=new_value,
        cache_prefix=cache_prefix,
    )
    await session.commit()
    await session.refresh(entity)
    return entity


async def log_and_commit_mutation_async(
    session: AsyncSession,
    audit_repo: AsyncAuditRepository,
    *,
    entity_type: str,
    entity_id: int | None,
    action: str,
    user_email: str | None,
    old_value: dict[str, Any] | None = None,
    new_value: dict[str, Any] | None = None,
    cache_prefix: str | Sequence[str] | None = None,
) -> None:
    await log_entity_mutation_async(
        session,
        audit_repo,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        user_email=user_email,
        old_value=old_value,
        new_value=new_value,
        cache_prefix=cache_prefix,
    )
    await session.commit()
