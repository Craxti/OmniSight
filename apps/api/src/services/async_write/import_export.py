"""Async CI/relation import-export writes."""

from __future__ import annotations

import csv
import io
from typing import Any

from src.core.exceptions import DomainValidationError
from src.models import Relation, User
from src.schemas.common import ImportReport
from src.schemas.relations import RelationImportItem, RelationImportRequest
from src.services.async_ci.import_batch import AsyncCiImportBatchService
from src.services.async_import_audit import log_import_audit_async
from src.services.async_relations.validator import AsyncRelationValidator
from src.services.base.async_domain import AsyncDomainService
from src.services.import_validate import validate_relation_status


class AsyncCiImportExportWriteService(AsyncDomainService):
    def __init__(self, bundle) -> None:
        super().__init__(bundle)
        self._import = AsyncCiImportBatchService(bundle)

    async def import_ci_items(
        self,
        items: list[dict[str, Any]],
        user: User,
        *,
        type_mappings: list[dict[str, Any]] | None = None,
    ) -> ImportReport:
        return await self._import.import_ci_items(items, user, type_mappings=type_mappings)

    async def import_ci_csv(self, content: str, user: User) -> ImportReport:
        return await self._import.import_ci_csv(content, user)


class AsyncRelationImportExportWriteService(AsyncDomainService):
    def __init__(self, bundle) -> None:
        super().__init__(bundle)
        self._ci = bundle.ci
        self._validator = AsyncRelationValidator(bundle.ci, bundle.relations, bundle.relation_types)
        self._audit = bundle.audit

    async def _resolve_ci_ids(
        self,
        source_id: int | None,
        source_name: str | None,
        target_id: int | None,
        target_name: str | None,
    ) -> tuple[int | None, int | None]:
        if not source_id and source_name:
            source = await self._ci.get_by_name(source_name)
            source_id = source.id if source else None
        if not target_id and target_name:
            target = await self._ci.get_by_name(target_name)
            target_id = target.id if target else None
        return source_id, target_id

    async def _import_relation_row(
        self,
        *,
        source_id: int | None,
        target_id: int | None,
        relation_type: str,
        status: str,
        data_source: str | None,
        report: ImportReport,
    ) -> None:
        if not source_id or not target_id:
            report.skipped += 1
            report.errors.append("Missing CI for relation")
            return
        try:
            rel_type = await self._validator.validate_for_create(
                source_id,
                target_id,
                relation_type,
                status,
            )
            rel = Relation(
                source_ci_id=source_id,
                target_ci_id=target_id,
                relation_type=rel_type,
                status=status,
                data_source=data_source,
            )
            self._session.add(rel)
            await self._session.flush()
            report.created += 1
        except DomainValidationError as exc:
            report.skipped += 1
            report.errors.append(str(exc))

    async def import_json(self, body: RelationImportRequest, user: User) -> ImportReport:
        report = ImportReport()

        async def _import_json_row(item: RelationImportItem) -> None:
            source_id, target_id = await self._resolve_ci_ids(
                item.source_ci_id,
                item.source_name,
                item.target_ci_id,
                item.target_name,
            )
            await self._import_relation_row(
                source_id=source_id,
                target_id=target_id,
                relation_type=item.relation_type,
                status=item.status,
                data_source=item.data_source,
                report=report,
            )

        for item in body.relations:
            try:
                await _import_json_row(item)
            except DomainValidationError as exc:
                report.errors.append(str(exc))

        await log_import_audit_async(self._session, self._audit, user, "import_relations_json", report)
        return report

    async def import_csv(self, content: str, user: User) -> ImportReport:
        report = ImportReport()
        reader = csv.DictReader(io.StringIO(content))

        for row in reader:
            try:
                source_id, target_id = await self._resolve_ci_ids(
                    None,
                    row.get("source_name"),
                    None,
                    row.get("target_name"),
                )
                status = row.get("status") or "active"
                validate_relation_status(status)
                await self._import_relation_row(
                    source_id=source_id,
                    target_id=target_id,
                    relation_type=row["relation_type"],
                    status=status,
                    data_source=row.get("data_source"),
                    report=report,
                )
            except DomainValidationError as exc:
                report.errors.append(str(exc))
            except KeyError as exc:
                report.errors.append(str(exc))

        await log_import_audit_async(self._session, self._audit, user, "import_relations_csv", report)
        return report
