"""Native async CI batch import (JSON/CSV) and type-mapping apply."""

from __future__ import annotations

import csv
import io
import json
from typing import Any, Literal

from pydantic import ValidationError as PydanticValidationError
from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.core.constants import CACHE_PREFIXES_CORRELATION
from src.core.exceptions import DomainValidationError
from src.core.serializers import ci_audit_snapshot
from src.models import CIType, User
from src.repositories.async_orm.audit_repository import AsyncAuditRepository
from src.repositories.async_orm.ci_repository import AsyncCiRepository
from src.repositories.async_orm.ci_type_repository import AsyncCITypeRepository
from src.schemas.ci import CICreate, CITypeCreate
from src.schemas.common import ImportReport
from src.services.async_import_audit import log_import_audit_async
from src.services.async_import_validate import find_external_id_conflict_async
from src.services.async_mutations import log_entity_mutation_async
from src.services.base.async_domain import AsyncDomainService
from src.services.ci.base import CiDomainMixin
from src.services.ci.factory import build_ci_from_create
from src.services.ci.import_type_helpers import extract_import_type_name
from src.services.ci.types import type_to_dict
from src.services.import_export.base import IMPORT_ROW_ERRORS
from src.services.rsm.indexed_ids import sync_search_indexes

_TYPE_KEYS = ("type_name", "type", "Type", "ci_type", "element_type")


class AsyncCiImportBatchService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)
        self._ci: AsyncCiRepository = bundle.ci
        self._types: AsyncCITypeRepository = bundle.ci_types
        self._audit: AsyncAuditRepository = bundle.audit

    async def _resolve_type_id(self, body: CICreate) -> int:
        if body.type_id:
            return (await self._types.require_by_id(body.type_id)).id
        if body.type_name:
            return (await self._types.require_by_name(body.type_name)).id
        raise DomainValidationError("type_id or type_name required")

    async def _create_type_for_import(self, body: CITypeCreate, user: User) -> dict:
        if await self._types.name_taken(body.name):
            existing = await self._types.get_by_name(body.name)
            assert existing is not None
            return type_to_dict(existing)
        schema = body.attribute_schema or {"properties": {}}
        ci_type = CIType(
            name=body.name,
            description=body.description,
            attribute_schema=schema,
            is_official=False,
            is_import_draft=True,
        )
        self._session.add(ci_type)
        await self._session.flush()
        ci_type = await self._types.get_or_raise(ci_type.id)
        await log_entity_mutation_async(
            self._session,
            self._audit,
            entity_type="ci_type",
            entity_id=ci_type.id,
            action="create",
            user_email=user.email,
            new_value=type_to_dict(ci_type),
            cache_prefix=CACHE_PREFIXES_CORRELATION,
        )
        await self._session.flush()
        return type_to_dict(ci_type)

    async def apply_import_type_mappings(
        self,
        items: list[dict[str, Any]],
        mappings: list[dict[str, Any]],
        user: User,
    ) -> tuple[list[dict[str, Any]], list[str]]:
        remap: dict[str, str] = {}
        errors: list[str] = []

        for entry in mappings:
            source = str(entry.get("source_type", "")).strip()
            if not source:
                continue
            action = entry.get("action")
            if action == "use_existing":
                type_id = entry.get("target_type_id")
                if not type_id:
                    errors.append(f"{source}: target_type_id required")
                    continue
                type_row = await self._types.get_by_id(type_id)
                if not type_row:
                    errors.append(f"{source}: type id {type_id} not found")
                    continue
                remap[source] = type_row.name
            elif action == "create_new":
                draft_data = entry.get("draft") or {}
                try:
                    draft = CITypeCreate(**draft_data)
                except PydanticValidationError as exc:
                    errors.append(f"{source}: invalid draft — {exc}")
                    continue
                created_type = await self._create_type_for_import(draft, user)
                remap[source] = created_type["name"]
            elif action == "skip":
                continue
            else:
                errors.append(f"{source}: unknown action {action!r}")

        remapped: list[dict[str, Any]] = []
        for item in items:
            item_row = dict(item)
            import_type = extract_import_type_name(item_row)
            if import_type and import_type in remap:
                item_row["type_name"] = remap[import_type]
                for key in _TYPE_KEYS:
                    if key != "type_name":
                        item_row.pop(key, None)
            remapped.append(item_row)

        return remapped, errors

    async def upsert_from_import(self, body: CICreate, user: User) -> Literal["created", "updated", "skipped"]:
        CiDomainMixin.validate_status(body.status)
        CiDomainMixin.validate_ip_fields(body.attributes, body.external_ids)
        type_id = await self._resolve_type_id(body)
        existing = await self._ci.get_by_name(body.name)
        if existing:
            if CiDomainMixin.ci_row_unchanged(existing, body, type_id):
                return "skipped"
            old = ci_audit_snapshot(existing)
            for field, val in body.model_dump(exclude={"type_id", "type_name"}).items():
                if val is not None:
                    setattr(existing, field, val)
            existing.type_id = type_id
            sync_search_indexes(existing)
            await log_entity_mutation_async(
                self._session,
                self._audit,
                entity_type="ci",
                entity_id=existing.id,
                action="import_update",
                user_email=user.email,
                old_value=old,
                new_value=ci_audit_snapshot(existing),
                cache_prefix=CACHE_PREFIXES_CORRELATION,
            )
            await self._session.flush()
            return "updated"
        ci = build_ci_from_create(body, type_id)
        sync_search_indexes(ci)
        self._session.add(ci)
        await self._session.flush()
        await log_entity_mutation_async(
            self._session,
            self._audit,
            entity_type="ci",
            entity_id=ci.id,
            action="import_create",
            user_email=user.email,
            new_value=ci_audit_snapshot(ci),
            cache_prefix=CACHE_PREFIXES_CORRELATION,
        )
        await self._session.flush()
        return "created"

    async def import_ci_items(
        self,
        items: list[dict[str, Any]],
        user: User,
        *,
        type_mappings: list[dict[str, Any]] | None = None,
    ) -> ImportReport:
        if type_mappings:
            items, map_errors = await self.apply_import_type_mappings(items, type_mappings, user)
            report = ImportReport()
            report.errors.extend(map_errors)
            if map_errors and not items:
                return report
        else:
            report = ImportReport()

        for item in items:
            try:
                body = CICreate(**item)
                merged_ext = {**(body.attributes or {}), **(body.external_ids or {})}
                existing = await self._ci.get_by_name(body.name)
                dup = await find_external_id_conflict_async(
                    self._ci,
                    merged_ext,
                    exclude_ci_id=existing.id if existing else None,
                )
                if dup:
                    report.errors.append(f"{body.name}: {dup}")
                    report.skipped += 1
                    continue
                outcome = await self.upsert_from_import(body, user)
                if outcome == "created":
                    report.created += 1
                elif outcome == "updated":
                    report.updated += 1
                else:
                    report.skipped += 1
            except IMPORT_ROW_ERRORS as exc:
                name = item.get("name", "?") if isinstance(item, dict) else "?"
                report.errors.append(f"{name}: {exc}")

        await log_import_audit_async(self._session, self._audit, user, "import_ci_json", report)
        return report

    async def import_ci_csv(self, content: str, user: User) -> ImportReport:
        reader = csv.DictReader(io.StringIO(content))
        items: list[dict[str, Any]] = []
        for row in reader:
            items.append(
                {
                    "name": row["name"],
                    "status": row.get("status", "active"),
                    "type_name": row.get("type_name"),
                    "attributes": json.loads(row.get("attributes") or "{}"),
                    "external_ids": json.loads(row.get("external_ids") or "{}"),
                    "criticality": row.get("criticality"),
                    "environment": row.get("environment"),
                    "owner": row.get("owner"),
                    "team": row.get("team"),
                }
            )
        return await self.import_ci_items(items, user)
