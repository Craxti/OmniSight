"""Async uniqueness guards for native write paths."""

from __future__ import annotations

from src.core.exceptions import ConflictError
from src.repositories.async_orm.ci_repository import AsyncCiRepository


async def assert_unique_ci_name_async(
    ci_repo: AsyncCiRepository,
    name: str,
    *,
    exclude_id: int | None = None,
) -> None:
    if await ci_repo.name_exists(name, exclude_id=exclude_id):
        raise ConflictError(f"CI with name '{name}' already exists")
