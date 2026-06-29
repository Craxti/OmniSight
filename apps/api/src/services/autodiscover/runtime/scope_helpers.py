"""Async helpers for autodiscover apply scope resolution."""

from __future__ import annotations

from src.models import CI
from src.repositories.async_orm.ci_repository import AsyncCiRepository


async def resolve_relation_target_async(
    ci_repo: AsyncCiRepository,
    *,
    hostname: str | None = None,
    ip: str | None = None,
) -> CI | None:
    for candidate in (hostname, ip):
        if not candidate:
            continue
        ci = await ci_repo.find_by_identifier(str(candidate).strip())
        if ci:
            return ci
    if hostname and "." in hostname:
        short = hostname.split(".")[0]
        if short != hostname:
            return await ci_repo.find_by_identifier(short)
    return None
