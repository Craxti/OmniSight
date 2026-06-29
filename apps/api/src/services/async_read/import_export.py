from __future__ import annotations

from typing import Any, Literal

from fastapi.responses import StreamingResponse
from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.models import CI, Relation, User
from src.schemas.export_filters import CiExportFilter
from src.services.base.async_domain import AsyncDomainService
from src.services.domain.import_export import (
    build_export_full_payload,
    build_import_type_preview,
    filter_cis_for_export,
)
from src.services.export import build_relations_csv, build_relations_xlsx
from src.services.export.registry import export_tabular
from src.services.import_export.base import csv_streaming_response, xlsx_streaming_response
from src.services.rsm.async_topology import async_find_component_ids_below


class AsyncCiImportExportReadService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)

    async def preview_import_type_mappings(self, items: list[dict[str, Any]]) -> dict[str, Any]:
        existing = await self._bundle.ci_types.list_ordered()
        return build_import_type_preview(existing, items)

    async def query_export_subset(self, filters: CiExportFilter) -> tuple[list[CI], list[Relation]]:
        type_id = filters.type_id
        environment = filters.environment
        owner = filters.owner
        criticality = filters.criticality
        business_service_id = filters.business_service_id
        service_code = filters.service_code

        if business_service_id:
            root = await self._bundle.ci.get_or_404(business_service_id)
            subtree_ids = await async_find_component_ids_below(
                business_service_id,
                ci_repo=self._bundle.ci,
                rel_repo=self._bundle.relations,
            )
            subtree_ids.add(root.id)
            cis = await self._bundle.ci.list_in_ids(
                subtree_ids,
                environment=environment,
                owner=owner,
            )
            cis = filter_cis_for_export(cis, criticality=criticality, service_code=service_code)
            ci_ids = {c.id for c in cis}
            relations = await self._bundle.relations.touching_ci_ids(ci_ids)
            return cis, relations

        type_name = None
        if type_id:
            t = await self._bundle.ci_types.get_by_id(type_id)
            type_name = t.name if t else None
        cis, _ = await self._bundle.ci.search(
            type_name=type_name,
            environment=environment,
            owner=owner,
            service_code=service_code,
            limit=10000,
        )
        cis = filter_cis_for_export(cis, criticality=criticality, service_code=service_code)
        ci_ids = {c.id for c in cis}
        relations = await self._bundle.relations.touching_ci_ids(ci_ids)
        return cis, relations

    async def _log_export(self, user: User, action: str, count: int, *, extra: dict[str, Any] | None = None) -> None:
        payload: dict[str, Any] = {"count": count}
        if extra:
            payload.update(extra)
        await self._bundle.audit.log(
            entity_type="export",
            entity_id=None,
            action=action,
            user_email=user.email,
            new_value=payload,
        )
        await self._bundle.session.commit()

    async def export_full(self, user: User, filters: CiExportFilter) -> dict[str, Any]:
        cis, relations = await self.query_export_subset(filters)
        await self._log_export(
            user,
            "export_full",
            len(cis),
            extra={"relation_count": len(relations), "filters": filters.as_dict()},
        )
        return build_export_full_payload(cis, relations, filters)

    async def export_tabular(
        self,
        user: User,
        *,
        export_format: Literal["csv", "xlsx"],
        filters: CiExportFilter,
    ) -> StreamingResponse:
        cis, relations = await self.query_export_subset(filters)
        action = "export_rsm_csv" if export_format == "csv" else "export_rsm_xlsx"
        await self._log_export(
            user,
            action,
            len(cis),
            extra={"relation_count": len(relations), "filters": filters.as_dict()},
        )
        suffix = "filtered" if any(filters.as_dict().values()) else "full"
        if export_format == "csv":
            body = export_tabular("rsm_csv", cis, relations)
            return StreamingResponse(
                body,
                media_type="application/zip",
                headers={"Content-Disposition": f"attachment; filename=rsm-{suffix}-export.zip"},
            )
        body = export_tabular("rsm_xlsx", cis, relations)
        return StreamingResponse(
            body,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=rsm-{suffix}-export.xlsx"},
        )


class AsyncRelationImportExportReadService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)

    async def list_for_export(self) -> list[Relation]:
        return await self._bundle.relations.list_active()

    async def _log_export(self, user: User, action: str, count: int) -> None:
        await self._bundle.audit.log(
            entity_type="export",
            entity_id=None,
            action=action,
            user_email=user.email,
            new_value={"count": count},
        )
        await self._bundle.session.commit()

    async def export_csv(self, user: User) -> StreamingResponse:
        rels = await self.list_for_export()
        await self._log_export(user, "export_relations_csv", len(rels))
        return csv_streaming_response(build_relations_csv(rels), "relations.csv")

    async def export_xlsx(self, user: User) -> StreamingResponse:
        rels = await self.list_for_export()
        await self._log_export(user, "export_relations_xlsx", len(rels))
        return xlsx_streaming_response(build_relations_xlsx(rels), "relations.xlsx")
