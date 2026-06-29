"""Async import-time validation helpers."""

from __future__ import annotations

from src.core.constants import FIELD_TO_SEARCH_COLUMN
from src.repositories.async_orm.ci_repository import AsyncCiRepository


async def find_external_id_conflict_async(
    ci_repo: AsyncCiRepository,
    external_ids: dict,
    *,
    exclude_ci_id: int | None = None,
) -> str | None:
    for field, col_name in FIELD_TO_SEARCH_COLUMN.items():
        val = external_ids.get(field)
        if val is None or not str(val).strip():
            continue
        other = await ci_repo.find_by_search_field(col_name, str(val), exclude_ci_id=exclude_ci_id)
        if other:
            return f"Duplicate {field}={val!r} already used by CI '{other.name}'"
    return None
