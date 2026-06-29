"""v1 response envelope builders — single place for api_version wrappers."""

from __future__ import annotations

from typing import Any

from src.core.pagination import pagination_meta
from src.schemas.audit import RelationValidationResponse
from src.schemas.ci import CIDetailResponse, CIListResponse, CIResponse
from src.schemas.relations import RelationResponse
from src.schemas.v1.auth import AUTH_SCHEMA_V1
from src.schemas.v1.autodiscover import AUTODISCOVER_SCHEMA_V1
from src.schemas.v1.inventory import INVENTORY_SCHEMA_V1
from src.schemas.v1.meta import META_SCHEMA_V1
from src.schemas.v1.ops import OPS_SCHEMA_V1
from src.schemas.v1.topology import TOPOLOGY_SCHEMA_V1
from src.schemas.v1.versions import CORRELATION_SCHEMA_V1


def wrap_v1(payload: dict[str, Any], *, schema_version: str | None = None) -> dict[str, Any]:
    envelope: dict[str, Any] = {"api_version": "v1", **payload}
    if schema_version:
        envelope["schema_version"] = schema_version
    return envelope


def ci_list_v1_envelope(result: CIListResponse, *, page: int, page_size: int) -> dict[str, Any]:
    return wrap_v1(
        {
            "items": [item.model_dump() for item in result.items],
            "pagination": pagination_meta(result.total, page, page_size),
        },
        schema_version=INVENTORY_SCHEMA_V1,
    )


def relations_list_v1_envelope(
    items: list[RelationResponse],
    *,
    total: int,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    return wrap_v1(
        {
            "items": [item.model_dump() for item in items],
            "pagination": pagination_meta(total, page, page_size),
        },
        schema_version=INVENTORY_SCHEMA_V1,
    )


def ci_detail_v1_envelope(detail: CIDetailResponse) -> dict[str, Any]:
    return wrap_v1({"ci": detail.model_dump()}, schema_version=INVENTORY_SCHEMA_V1)


def relation_detail_v1_envelope(relation: RelationResponse) -> dict[str, Any]:
    return wrap_v1({"relation": relation.model_dump()}, schema_version=INVENTORY_SCHEMA_V1)


def ci_mutation_v1_envelope(ci: CIResponse) -> dict[str, Any]:
    return wrap_v1({"ci": ci.model_dump()}, schema_version=INVENTORY_SCHEMA_V1)


def relation_mutation_v1_envelope(relation: RelationResponse) -> dict[str, Any]:
    return wrap_v1({"relation": relation.model_dump()}, schema_version=INVENTORY_SCHEMA_V1)


def delete_result_v1_envelope(result: dict[str, Any]) -> dict[str, Any]:
    return wrap_v1({"result": result}, schema_version=INVENTORY_SCHEMA_V1)


def relation_validation_v1_envelope(validation: RelationValidationResponse) -> dict[str, Any]:
    return wrap_v1({"validation": validation.model_dump()}, schema_version=INVENTORY_SCHEMA_V1)


def relation_items_v1_envelope(items: list[RelationResponse]) -> dict[str, Any]:
    total = len(items)
    return wrap_v1(
        {
            "items": [item.model_dump() for item in items],
            "pagination": pagination_meta(total, 1, max(1, total)),
        },
        schema_version=INVENTORY_SCHEMA_V1,
    )


def ci_type_list_v1_envelope(items: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(items)
    return wrap_v1(
        {
            "items": items,
            "pagination": pagination_meta(total, 1, max(1, total)),
        },
        schema_version=INVENTORY_SCHEMA_V1,
    )


def ci_type_mutation_v1_envelope(ci_type: dict[str, Any]) -> dict[str, Any]:
    return wrap_v1({"ci_type": ci_type}, schema_version=INVENTORY_SCHEMA_V1)


def relation_type_list_v1_envelope(items: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(items)
    return wrap_v1(
        {
            "items": items,
            "pagination": pagination_meta(total, 1, max(1, total)),
        },
        schema_version=INVENTORY_SCHEMA_V1,
    )


def relation_type_mutation_v1_envelope(relation_type: dict[str, Any]) -> dict[str, Any]:
    return wrap_v1({"relation_type": relation_type}, schema_version=INVENTORY_SCHEMA_V1)


def graph_v1_envelope(graph: Any) -> dict[str, Any]:
    data = graph.model_dump() if hasattr(graph, "model_dump") else graph
    return wrap_v1({"graph": data}, schema_version=TOPOLOGY_SCHEMA_V1)


def impact_v1_envelope(impact: Any) -> dict[str, Any]:
    data = impact.model_dump() if hasattr(impact, "model_dump") else impact
    return wrap_v1({"impact": data}, schema_version=TOPOLOGY_SCHEMA_V1)


def components_v1_envelope(components: Any) -> dict[str, Any]:
    data = components.model_dump() if hasattr(components, "model_dump") else components
    return wrap_v1({"components": data}, schema_version=TOPOLOGY_SCHEMA_V1)


def business_path_v1_envelope(path: Any) -> dict[str, Any]:
    data = path.model_dump() if hasattr(path, "model_dump") else path
    return wrap_v1({"business_path": data}, schema_version=TOPOLOGY_SCHEMA_V1)


def graph_layout_v1_envelope(layout: Any) -> dict[str, Any]:
    data = layout.model_dump() if hasattr(layout, "model_dump") else layout
    return wrap_v1({"layout": data}, schema_version=TOPOLOGY_SCHEMA_V1)


def resource_search_v1_envelope(result: Any) -> dict[str, Any]:
    data = result.model_dump() if hasattr(result, "model_dump") else result
    return wrap_v1({"search": data}, schema_version=INVENTORY_SCHEMA_V1)


def domain_constants_v1_envelope(constants: dict[str, Any]) -> dict[str, Any]:
    return wrap_v1({"constants": constants}, schema_version=META_SCHEMA_V1)


def dashboard_v1_envelope(overview: Any) -> dict[str, Any]:
    data = overview.model_dump() if hasattr(overview, "model_dump") else overview
    return wrap_v1({"dashboard": data}, schema_version=OPS_SCHEMA_V1)


def audit_list_v1_envelope(result: Any, *, page: int, page_size: int) -> dict[str, Any]:
    data = result.model_dump() if hasattr(result, "model_dump") else result
    total = data["total"]
    return wrap_v1(
        {
            "items": data["items"],
            "pagination": pagination_meta(total, page, page_size),
        },
        schema_version=OPS_SCHEMA_V1,
    )


def audit_items_v1_envelope(items: list[Any]) -> dict[str, Any]:
    payload = [item.model_dump() if hasattr(item, "model_dump") else item for item in items]
    total = len(payload)
    return wrap_v1(
        {
            "items": payload,
            "pagination": pagination_meta(total, 1, max(1, total)),
        },
        schema_version=OPS_SCHEMA_V1,
    )


def _dump_payload(payload: Any) -> Any:
    return payload.model_dump() if hasattr(payload, "model_dump") else payload


def autodiscover_items_v1_envelope(items: list[Any]) -> dict[str, Any]:
    payload = [_dump_payload(item) for item in items]
    total = len(payload)
    return wrap_v1(
        {
            "items": payload,
            "pagination": pagination_meta(total, 1, max(1, total)),
        },
        schema_version=AUTODISCOVER_SCHEMA_V1,
    )


def connector_v1_envelope(connector: Any) -> dict[str, Any]:
    return wrap_v1({"connector": _dump_payload(connector)}, schema_version=AUTODISCOVER_SCHEMA_V1)


def scan_v1_envelope(scan: Any) -> dict[str, Any]:
    return wrap_v1({"scan": _dump_payload(scan)}, schema_version=AUTODISCOVER_SCHEMA_V1)


def apply_v1_envelope(apply: Any) -> dict[str, Any]:
    return wrap_v1({"apply": _dump_payload(apply)}, schema_version=AUTODISCOVER_SCHEMA_V1)


def connector_test_v1_envelope(test: Any) -> dict[str, Any]:
    return wrap_v1({"test": _dump_payload(test)}, schema_version=AUTODISCOVER_SCHEMA_V1)


def connector_sync_v1_envelope(sync: Any) -> dict[str, Any]:
    return wrap_v1({"sync": _dump_payload(sync)}, schema_version=AUTODISCOVER_SCHEMA_V1)


def session_v1_envelope(session: Any) -> dict[str, Any]:
    return wrap_v1({"session": _dump_payload(session)}, schema_version=AUTH_SCHEMA_V1)


def user_v1_envelope(user: Any) -> dict[str, Any]:
    return wrap_v1({"user": _dump_payload(user)}, schema_version=AUTH_SCHEMA_V1)


def auth_items_v1_envelope(items: list[Any]) -> dict[str, Any]:
    payload = [_dump_payload(item) for item in items]
    total = len(payload)
    return wrap_v1(
        {
            "items": payload,
            "pagination": pagination_meta(total, 1, max(1, total)),
        },
        schema_version=AUTH_SCHEMA_V1,
    )


def auth_result_v1_envelope(result: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = result if result is not None else {"ok": True}
    return wrap_v1({"result": payload}, schema_version=AUTH_SCHEMA_V1)


def import_report_v1_envelope(report: Any) -> dict[str, Any]:
    payload = report.model_dump() if hasattr(report, "model_dump") else report
    return wrap_v1({"report": payload}, schema_version=INVENTORY_SCHEMA_V1)


def export_payload_v1_envelope(payload: Any) -> dict[str, Any]:
    data = payload.model_dump() if hasattr(payload, "model_dump") else payload
    return wrap_v1({"export": data}, schema_version=INVENTORY_SCHEMA_V1)


def ci_items_v1_envelope(items: list[CIResponse], *, page: int = 1, page_size: int | None = None) -> dict[str, Any]:
    total = len(items)
    size = page_size if page_size is not None else max(1, total)
    return wrap_v1(
        {
            "items": [item.model_dump() for item in items],
            "pagination": pagination_meta(total, page, size),
        },
        schema_version=INVENTORY_SCHEMA_V1,
    )


def correlation_context_v1_envelope(ctx: Any) -> dict[str, Any]:
    return wrap_v1(
        {"correlation": ctx.model_dump()},
        schema_version=CORRELATION_SCHEMA_V1,
    )


def correlation_ingest_v1_envelope(result: Any) -> dict[str, Any]:
    return wrap_v1(result.model_dump(), schema_version=CORRELATION_SCHEMA_V1)


def resolve_v1_envelope(payload: Any) -> dict[str, Any]:
    return wrap_v1(payload.model_dump())
