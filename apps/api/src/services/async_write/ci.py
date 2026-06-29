"""Native async CI write service."""

from __future__ import annotations

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.core.constants import CACHE_PREFIXES_CORRELATION, CI_STATUSES
from src.core.exceptions import DomainValidationError
from src.core.ip_validation import is_valid_ip_address
from src.core.serializers import ci_snapshot, ci_to_response
from src.models import User
from src.schemas.ci import BulkStatusUpdate, CICreate, CIResponse, CIUpdate
from src.services.async_ci.lifecycle import hard_delete_recycled_ci_async
from src.services.async_mutations import (
    commit_entity_mutation_async,
    log_and_commit_mutation_async,
    log_entity_mutation_async,
)
from src.services.async_uniqueness import assert_unique_ci_name_async
from src.services.base.async_domain import AsyncDomainService
from src.services.ci.factory import build_ci_from_create
from src.services.rsm.indexed_ids import sync_search_indexes


class AsyncCiWriteService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)
        self._ci = bundle.ci
        self._types = bundle.ci_types
        self._relations = bundle.relations
        self._audit = bundle.audit

    async def _ci_response(self, ci_id: int, *, include_deleted: bool = False) -> CIResponse:
        ci = await self._ci.get_or_404(ci_id, include_deleted=include_deleted)
        return ci_to_response(ci)

    async def _resolve_type_id(self, body: CICreate) -> int:
        if body.type_id:
            return (await self._types.require_by_id(body.type_id)).id
        if body.type_name:
            return (await self._types.require_by_name(body.type_name)).id
        raise DomainValidationError("type_id or type_name required")

    @staticmethod
    def _validate_status(status: str) -> None:
        if status not in CI_STATUSES:
            raise DomainValidationError(f"Invalid status. Allowed: {CI_STATUSES}")

    @staticmethod
    def _validate_ip_fields(attributes: dict | None, external_ids: dict | None) -> None:
        for container in (attributes, external_ids):
            if not container:
                continue
            ip = container.get("ip")
            if ip is None:
                continue
            if not is_valid_ip_address(str(ip)):
                raise DomainValidationError("Invalid IP address")

    async def create_ci(self, body: CICreate, user: User) -> CIResponse:
        self._validate_status(body.status)
        self._validate_ip_fields(body.attributes, body.external_ids)
        type_id = await self._resolve_type_id(body)
        await assert_unique_ci_name_async(self._ci, body.name)
        ci = build_ci_from_create(body, type_id)
        sync_search_indexes(ci)
        self._session.add(ci)
        await self._session.flush()
        ci = await self._ci.get_or_404(ci.id)
        await commit_entity_mutation_async(
            self._session,
            self._audit,
            ci,
            entity_type="ci",
            entity_id=ci.id,
            action="create",
            user_email=user.email,
            new_value=ci_snapshot(ci),
            cache_prefix=CACHE_PREFIXES_CORRELATION,
        )
        return await self._ci_response(ci.id)

    async def update_ci(self, ci_id: int, body: CIUpdate, user: User) -> CIResponse:
        ci = await self._ci.get_or_404(ci_id)
        old = ci_snapshot(ci)
        data = body.model_dump(exclude_unset=True)
        if "status" in data:
            self._validate_status(data["status"])
        if "name" in data:
            await assert_unique_ci_name_async(self._ci, data["name"], exclude_id=ci_id)
        attrs = data.get("attributes", ci.attributes)
        ext = data.get("external_ids", ci.external_ids)
        if "attributes" in data or "external_ids" in data:
            self._validate_ip_fields(attrs, ext)
        for key, value in data.items():
            setattr(ci, key, value)
        sync_search_indexes(ci)
        await commit_entity_mutation_async(
            self._session,
            self._audit,
            ci,
            entity_type="ci",
            entity_id=ci.id,
            action="update",
            user_email=user.email,
            old_value=old,
            new_value=ci_snapshot(ci),
            cache_prefix=CACHE_PREFIXES_CORRELATION,
        )
        return await self._ci_response(ci.id)

    async def delete_ci(self, ci_id: int, user: User) -> dict:
        ci = await self._ci.get_or_404(ci_id)
        old = ci_snapshot(ci)
        ci.is_deleted = True
        ci.status = "archived"
        await log_and_commit_mutation_async(
            self._session,
            self._audit,
            entity_type="ci",
            entity_id=ci.id,
            action="delete",
            user_email=user.email,
            old_value=old,
            new_value=ci_snapshot(ci),
            cache_prefix=CACHE_PREFIXES_CORRELATION,
        )
        return {"ok": True}

    async def restore_ci(self, ci_id: int, user: User) -> CIResponse:
        ci = await self._ci.get_or_404(ci_id, include_deleted=True)
        if not ci.is_deleted:
            raise DomainValidationError("CI is not deleted")
        await assert_unique_ci_name_async(self._ci, ci.name, exclude_id=ci_id)
        old = ci_snapshot(ci)
        ci.is_deleted = False
        ci.status = "active"
        await commit_entity_mutation_async(
            self._session,
            self._audit,
            ci,
            entity_type="ci",
            entity_id=ci.id,
            action="restore",
            user_email=user.email,
            old_value=old,
            new_value=ci_snapshot(ci),
            cache_prefix=CACHE_PREFIXES_CORRELATION,
        )
        return await self._ci_response(ci.id)

    async def purge_ci(self, ci_id: int, user: User) -> dict:
        ci = await self._ci.get_or_404(ci_id, include_deleted=True)
        if not ci.is_deleted:
            raise DomainValidationError("CI must be in recycle bin to purge")
        old = ci_snapshot(ci)
        await hard_delete_recycled_ci_async(self._session, ci, rel_repo=self._relations)
        await log_and_commit_mutation_async(
            self._session,
            self._audit,
            entity_type="ci",
            entity_id=ci_id,
            action="purge",
            user_email=user.email,
            old_value=old,
            new_value=None,
            cache_prefix=CACHE_PREFIXES_CORRELATION,
        )
        return {"ok": True}

    async def bulk_status(self, body: BulkStatusUpdate, user: User) -> dict:
        self._validate_status(body.status)
        updated = 0
        for ci_id in body.ci_ids:
            ci = await self._ci.get_active(ci_id)
            if not ci:
                continue
            old = ci_snapshot(ci)
            ci.status = body.status
            await log_entity_mutation_async(
                self._session,
                self._audit,
                entity_type="ci",
                entity_id=ci.id,
                action="bulk_status",
                user_email=user.email,
                old_value=old,
                new_value=ci_snapshot(ci),
                cache_prefix=CACHE_PREFIXES_CORRELATION,
            )
            updated += 1
        if updated:
            await self._session.commit()
        return {"updated": updated}
