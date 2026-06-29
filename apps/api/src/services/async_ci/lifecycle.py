"""Async CI lifecycle helpers."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from src.models import CI
from src.repositories.async_orm.relation_repository import AsyncRelationRepository


async def hard_delete_recycled_ci_async(
    session: AsyncSession,
    ci: CI,
    *,
    rel_repo: AsyncRelationRepository,
) -> None:
    await rel_repo.delete_for_ci(ci.id)
    await session.delete(ci)
