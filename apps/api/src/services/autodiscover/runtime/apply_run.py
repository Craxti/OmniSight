"""Native async autodiscover run apply."""

from __future__ import annotations

from datetime import UTC, datetime

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.core.constants import CACHE_PREFIXES_CORRELATION
from src.core.exceptions import ConflictError, DomainValidationError, NotFoundError
from src.core.serializers import ci_audit_snapshot
from src.models import CI, AutodiscoverMapping, Relation, User
from src.repositories.async_orm.audit_repository import AsyncAuditRepository
from src.repositories.async_orm.autodiscover_repository import (
    AsyncAutodiscoverMappingRepository,
    AsyncAutodiscoverRunRepository,
)
from src.repositories.async_orm.ci_repository import AsyncCiRepository
from src.repositories.async_orm.ci_type_repository import AsyncCITypeRepository
from src.repositories.async_orm.relation_repository import AsyncRelationRepository
from src.schemas.autodiscover import AutodiscoverApplyResponse
from src.services.async_import_validate import find_external_id_conflict_async
from src.services.async_mutations import log_entity_mutation_async
from src.services.async_relations.validator import AsyncRelationValidator
from src.services.autodiscover.apply_ci import apply_field
from src.services.autodiscover.normalize import EXTERNAL_ID_FIELDS
from src.services.autodiscover.runtime.scope_helpers import resolve_relation_target_async
from src.services.autodiscover.scope import current_field_value
from src.services.base.async_domain import AsyncDomainService
from src.services.ci.factory import build_ci_from_autodiscover
from src.services.import_validate import validate_relation_status
from src.services.rsm.indexed_ids import merge_external_ids, sync_search_indexes


class AsyncAutodiscoverApplyService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)
        self._runs: AsyncAutodiscoverRunRepository = bundle.autodiscover_runs
        self._mappings: AsyncAutodiscoverMappingRepository = bundle.autodiscover_mappings
        self._ci: AsyncCiRepository = bundle.ci
        self._types: AsyncCITypeRepository = bundle.ci_types
        self._relations: AsyncRelationRepository = bundle.relations
        self._audit: AsyncAuditRepository = bundle.audit
        self._validator = AsyncRelationValidator(bundle.ci, bundle.relations, bundle.relation_types)

    async def _apply_ci_create(self, row: AutodiscoverMapping, user: User) -> CI | None:
        payload = row.payload or {}
        hostname = str(payload.get("hostname") or row.discovered_value)
        fields = dict(payload.get("fields") or {})
        type_id = payload.get("type_id")
        entity_type = payload.get("entity_type") or row.field
        if not type_id:
            type_row = await self._types.get_by_name(str(entity_type))
            if not type_row:
                return None
            type_id = type_row.id

        attrs = {k: v for k, v in fields.items() if k not in ("entity_type", "match_hostname")}
        if hostname and "hostname" not in attrs:
            attrs["hostname"] = hostname
        ext = {k: str(v) for k, v in attrs.items() if k in EXTERNAL_ID_FIELDS and v is not None}

        name = await self._ci.next_unique_name(row.ci_name)
        if await self._ci.name_exists(name):
            raise ConflictError(f"CI with name '{name}' already exists")

        ci = build_ci_from_autodiscover(
            name=name,
            type_id=int(type_id),
            attributes=attrs,
            external_ids=ext,
        )
        sync_search_indexes(ci)
        self._session.add(ci)
        await self._session.flush()
        await log_entity_mutation_async(
            self._session,
            self._audit,
            entity_type="ci",
            entity_id=ci.id,
            action="autodiscover_create",
            user_email=user.email,
            new_value=ci_audit_snapshot(ci),
            cache_prefix=CACHE_PREFIXES_CORRELATION,
        )
        await self._session.flush()
        row.ci_id = ci.id
        row.ci_name = ci.name
        row.applied_at = datetime.now(UTC).replace(tzinfo=None)
        row.status = "applied"
        return ci

    async def _apply_relation(self, row: AutodiscoverMapping, user: User) -> bool:
        if not row.relation_type:
            return False
        source_id = row.ci_id
        if not source_id:
            src_key = (row.payload or {}).get("source_hostname") or row.ci_name
            source = await self._ci.find_by_identifier(str(src_key))
            if not source:
                return False
            source_id = source.id
            row.ci_id = source_id
            row.ci_name = source.name
        target_id = row.target_ci_id
        if not target_id:
            host = (row.payload or {}).get("target_hostname") or row.discovered_value
            target_ip = (row.payload or {}).get("target_ip")
            target = await resolve_relation_target_async(
                self._ci,
                hostname=str(host) if host else None,
                ip=str(target_ip) if target_ip else None,
            )
            if not target:
                return False
            target_id = target.id
            row.target_ci_id = target_id
            row.target_ci_name = target.name
        rel_type = await self._validator.normalize_type(row.relation_type)
        if await self._relations.find_active(source_id, target_id, rel_type):
            row.applied_at = datetime.now(UTC).replace(tzinfo=None)
            return False
        validate_relation_status("active")
        rel = Relation(
            source_ci_id=source_id,
            target_ci_id=target_id,
            relation_type=rel_type,
            status="active",
            data_source="autodiscover",
        )
        self._session.add(rel)
        await self._session.flush()
        await log_entity_mutation_async(
            self._session,
            self._audit,
            entity_type="relation",
            entity_id=rel.id,
            action="autodiscover_apply",
            user_email=user.email,
            new_value={"id": rel.id, "relation_type": rel.relation_type},
            cache_prefix=CACHE_PREFIXES_CORRELATION,
        )
        await self._session.flush()
        row.applied_at = datetime.now(UTC).replace(tzinfo=None)
        row.status = "applied"
        return True

    async def apply_run(
        self,
        run_id: int,
        *,
        user: User,
        mapping_ids: list[str] | None = None,
        apply_auto_only: bool = False,
    ) -> AutodiscoverApplyResponse:
        run = await self._runs.get_by_id(run_id)
        if not run:
            raise NotFoundError("Autodiscover run not found")

        rows = await self._mappings.list_pending_for_apply(
            run_id,
            mapping_ids=mapping_ids,
            apply_auto_only=apply_auto_only,
        )
        kind_order = {"ci_create": 0, "field": 1, "relation": 2}
        rows.sort(key=lambda r: (kind_order.get(r.mapping_kind or "field", 9), r.id))

        applied = 0
        skipped = 0
        created_cis = 0
        applied_relations = 0
        errors: list[str] = []
        updated_ids: set[int] = set()

        for row in rows:
            kind = row.mapping_kind or "field"
            if kind == "ci_create":
                try:
                    ci = await self._apply_ci_create(row, user)
                    if ci:
                        created_cis += 1
                        applied += 1
                        updated_ids.add(ci.id)
                    else:
                        errors.append(f"Cannot create CI for {row.discovered_value}")
                        skipped += 1
                except (DomainValidationError, NotFoundError, ValueError, ConflictError) as exc:
                    errors.append(f"{row.ci_name}: {exc}")
                    skipped += 1
                continue

            if kind == "relation":
                try:
                    if await self._apply_relation(row, user):
                        applied_relations += 1
                        applied += 1
                    else:
                        skipped += 1
                except (DomainValidationError, NotFoundError, ValueError) as exc:
                    errors.append(f"{row.ci_name} → {row.target_ci_name}: {exc}")
                    skipped += 1
                continue

            if not row.ci_id:
                skipped += 1
                continue
            ci = await self._ci.get_active(row.ci_id)
            if not ci:
                errors.append(f"CI {row.ci_id} not found")
                skipped += 1
                continue
            if row.field in EXTERNAL_ID_FIELDS:
                probe = dict(merge_external_ids(ci.attributes, ci.external_ids))
                probe[row.field] = row.discovered_value
                conflict = await find_external_id_conflict_async(self._ci, probe, exclude_ci_id=ci.id)
                if conflict:
                    errors.append(f"{ci.name}: {conflict}")
                    skipped += 1
                    continue
            current = current_field_value(ci, row.field)
            if current == row.discovered_value:
                skipped += 1
                row.applied_at = datetime.now(UTC).replace(tzinfo=None)
                continue
            old = ci_audit_snapshot(ci)
            apply_field(ci, row.field, row.discovered_value)
            sync_search_indexes(ci)
            await log_entity_mutation_async(
                self._session,
                self._audit,
                entity_type="ci",
                entity_id=ci.id,
                action="autodiscover_apply",
                user_email=user.email,
                old_value=old,
                new_value=ci_audit_snapshot(ci),
                cache_prefix=CACHE_PREFIXES_CORRELATION,
            )
            await self._session.flush()
            row.applied_at = datetime.now(UTC).replace(tzinfo=None)
            row.status = "applied"
            applied += 1
            updated_ids.add(ci.id)

        if run.status == "draft":
            run.status = "completed"

        return AutodiscoverApplyResponse(
            applied=applied,
            skipped=skipped,
            errors=errors,
            updated_ci_ids=sorted(updated_ids),
            created_cis=created_cis,
            applied_relations=applied_relations,
        )
