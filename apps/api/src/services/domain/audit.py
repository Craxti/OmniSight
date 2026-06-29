"""Shared audit read response builders."""

from __future__ import annotations

from typing import Any, Protocol

from src.core.serializers import audit_to_response
from src.repositories.protocols import AsyncAuditRepositoryProtocol
from src.schemas.audit import AuditListResponse, AuditLogResponse


class AuditSearchRepo(Protocol):
    def search(self, **kwargs: Any) -> tuple[list[Any], int]: ...

    def for_entity(self, entity_type: str, entity_id: int) -> list[Any]: ...

    def for_ci_with_relations(self, ci_id: int) -> list[Any]: ...


class AsyncAuditSearchRepo(Protocol):
    async def search(self, **kwargs: Any) -> tuple[list[Any], int]: ...

    async def for_entity(self, entity_type: str, entity_id: int) -> list[Any]: ...

    async def for_ci_with_relations(self, ci_id: int) -> list[Any]: ...


def build_audit_list(items: list[Any], total: int, skip: int, limit: int) -> AuditListResponse:
    return AuditListResponse(
        items=[audit_to_response(a) for a in items],
        total=total,
        skip=skip,
        limit=limit,
    )


def fetch_entity_history(repo: AuditSearchRepo, entity_type: str, entity_id: int) -> list[Any]:
    if entity_type == "ci":
        return repo.for_ci_with_relations(entity_id)
    return repo.for_entity(entity_type, entity_id)


async def fetch_entity_history_async(
    repo: AsyncAuditRepositoryProtocol,
    entity_type: str,
    entity_id: int,
) -> list[Any]:
    if entity_type == "ci":
        return await repo.for_ci_with_relations(entity_id)
    return await repo.for_entity(entity_type, entity_id)


def build_entity_history(items: list[Any]) -> list[AuditLogResponse]:
    return [audit_to_response(a) for a in items]
