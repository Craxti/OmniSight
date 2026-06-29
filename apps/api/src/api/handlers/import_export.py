"""Import/export HTTP handlers (v1 envelopes)."""

from __future__ import annotations

from typing import Any, Literal

from src.api.handlers.v1_envelopes import (
    export_payload_v1_envelope,
    import_report_v1_envelope,
    relation_items_v1_envelope,
)
from src.core.serializers import relation_to_response
from src.models import User
from src.schemas.ci import ImportTypeMappingEntry
from src.schemas.export_filters import CiExportFilter
from src.schemas.relations import RelationImportRequest
from src.services.async_read.import_export import (
    AsyncCiImportExportReadService,
    AsyncRelationImportExportReadService,
)
from src.services.async_read.relations import AsyncRelationReadService
from src.services.async_write.import_export import (
    AsyncCiImportExportWriteService,
    AsyncRelationImportExportWriteService,
)


async def handle_ci_import_preview(service: AsyncCiImportExportReadService, items: list[dict[str, Any]]):
    preview = await service.preview_import_type_mappings(items)
    return export_payload_v1_envelope(preview)


async def handle_ci_import_json(
    service: AsyncCiImportExportWriteService,
    items: list[dict[str, Any]],
    user: User,
    *,
    type_mappings: list[ImportTypeMappingEntry] | None = None,
):
    mappings = [m.model_dump() for m in type_mappings] if type_mappings else None
    report = await service.import_ci_items(items, user, type_mappings=mappings)
    return import_report_v1_envelope(report)


async def handle_ci_import_csv(service: AsyncCiImportExportWriteService, content: str, user: User):
    report = await service.import_ci_csv(content, user)
    return import_report_v1_envelope(report)


async def handle_ci_export_full(service: AsyncCiImportExportReadService, user: User, filters: CiExportFilter):
    payload = await service.export_full(user, filters)
    return export_payload_v1_envelope(payload)


async def handle_relations_import_json(
    service: AsyncRelationImportExportWriteService,
    body: RelationImportRequest,
    user: User,
):
    report = await service.import_json(body, user)
    return import_report_v1_envelope(report)


async def handle_relations_import_csv(service: AsyncRelationImportExportWriteService, content: str, user: User):
    report = await service.import_csv(content, user)
    return import_report_v1_envelope(report)


async def handle_relations_export_json(service: AsyncRelationReadService):
    rels = await service.list_for_export()
    items = [relation_to_response(r) for r in rels]
    return relation_items_v1_envelope(items)


async def handle_ci_export_tabular(
    service: AsyncCiImportExportReadService,
    user: User,
    *,
    export_format: Literal["csv", "xlsx"],
    filters: CiExportFilter,
):
    return await service.export_tabular(user, export_format=export_format, filters=filters)


async def handle_relations_export_tabular(
    service: AsyncRelationImportExportReadService,
    user: User,
    *,
    export_format: Literal["csv", "xlsx"],
):
    if export_format == "csv":
        return await service.export_csv(user)
    return await service.export_xlsx(user)
