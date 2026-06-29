"""Async relation validation for native write paths."""

from __future__ import annotations

from src.core.exceptions import DomainValidationError
from src.repositories.async_orm.ci_repository import AsyncCiRepository
from src.repositories.async_orm.relation_repository import AsyncRelationRepository
from src.repositories.async_orm.relation_type_repository import AsyncRelationTypeRepository
from src.services.import_validate import validate_relation_status
from src.services.rsm import normalize_relation_type
from src.services.rsm.async_depends_on_cycle import would_create_depends_on_cycle_async


async def validate_relation_endpoints_async(
    ci_repo: AsyncCiRepository,
    source_id: int,
    target_id: int,
) -> list[str]:
    errors: list[str] = []
    source = await ci_repo.get_active(source_id)
    target = await ci_repo.get_active(target_id)
    if not source:
        errors.append(f"Source CI {source_id} not found")
    elif source.status == "archived":
        errors.append(f"Source CI '{source.name}' is archived")
    if not target:
        errors.append(f"Target CI {target_id} not found")
    elif target.status == "archived":
        errors.append(f"Target CI '{target.name}' is archived")
    if source_id == target_id:
        errors.append("Self-referencing relation is not allowed")
    return errors


class AsyncRelationValidator:
    def __init__(
        self,
        ci_repo: AsyncCiRepository,
        rel_repo: AsyncRelationRepository,
        relation_type_repo: AsyncRelationTypeRepository,
    ) -> None:
        self._ci = ci_repo
        self._rel = rel_repo
        self._relation_types = relation_type_repo

    async def _allowed_keys(self) -> frozenset[str]:
        keys = await self._relation_types.list_keys()
        return frozenset(keys)

    async def normalize_type(self, relation_type: str) -> str:
        return normalize_relation_type(relation_type, allowed=await self._allowed_keys())

    async def collect_create_errors(
        self,
        source_id: int,
        target_id: int,
        relation_type: str,
        status: str,
    ) -> list[str]:
        errors: list[str] = []
        try:
            validate_relation_status(status)
        except DomainValidationError as exc:
            errors.append(str(exc))
        try:
            rel_type = await self.normalize_type(relation_type)
        except DomainValidationError as exc:
            errors.append(str(exc))
            rel_type = relation_type
        errors.extend(await validate_relation_endpoints_async(self._ci, source_id, target_id))
        if rel_type == "depends_on" and await would_create_depends_on_cycle_async(
            self._rel,
            source_id,
            target_id,
        ):
            errors.append(f"depends_on cycle: {source_id} -> {target_id}")
        return errors

    async def validate_for_create(
        self,
        source_id: int,
        target_id: int,
        relation_type: str,
        status: str,
    ) -> str:
        errors = await self.collect_create_errors(source_id, target_id, relation_type, status)
        if errors:
            raise DomainValidationError(errors[0])
        return await self.normalize_type(relation_type)
