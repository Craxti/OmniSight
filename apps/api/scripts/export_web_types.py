#!/usr/bin/env python3
"""Generate TypeScript entity types from Pydantic schemas (keeps web types in sync with API)."""

from __future__ import annotations

import sys
import types
from pathlib import Path
from typing import Any, Union, get_args, get_origin

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from src.schemas.audit import AuditListResponse, AuditLogResponse, RelationValidationResponse
from src.schemas.auth import UserResponse
from src.schemas.ci import CIDetailResponse, CIListResponse, CIResponse
from src.schemas.common import ImportReport
from src.schemas.correlation import (
    CorrelationContextPayload,
    CorrelationContextResponse,
    CorrelationEnrichmentItem,
    CorrelationIngestResponse,
    CorrelationMatchResult,
    CorrelationResolvePayload,
    GraphDataResponse,
    GraphNodeResponse,
)
from src.schemas.relations import RelationResponse
from src.schemas.resources import (
    BusinessPathResponse,
    ComponentsResponse,
    DashboardModelHealth,
    DashboardOverviewResponse,
    GraphLayoutPosition,
    GraphLayoutResponse,
    ImpactedServiceItem,
    ImpactResponse,
    ResourceGraphResponse,
)

OUT = Path(__file__).resolve().parents[2] / "web" / "src" / "shared" / "api" / "types.generated.ts"

MODELS: list[type[BaseModel]] = [
    CIResponse,
    CIDetailResponse,
    CIListResponse,
    RelationResponse,
    AuditLogResponse,
    AuditListResponse,
    RelationValidationResponse,
    UserResponse,
    ImportReport,
    DashboardModelHealth,
    DashboardOverviewResponse,
    ImpactedServiceItem,
    ImpactResponse,
    ComponentsResponse,
    BusinessPathResponse,
    GraphLayoutPosition,
    GraphLayoutResponse,
    GraphNodeResponse,
    GraphDataResponse,
    CorrelationMatchResult,
    CorrelationResolvePayload,
    CorrelationEnrichmentItem,
    CorrelationContextPayload,
    CorrelationContextResponse,
    CorrelationIngestResponse,
    ResourceGraphResponse,
]

HEADER = """/** AUTO-GENERATED — do not edit. Run: npm run codegen:api */
"""


def _collect_fields(model: type[BaseModel]) -> dict[str, FieldInfo]:
    fields: dict[str, FieldInfo] = {}
    for cls in reversed(model.__mro__):
        if issubclass(cls, BaseModel) and cls is not BaseModel:
            for name, info in cls.model_fields.items():
                if name not in fields:
                    fields[name] = info
    return fields


def _union_origin(annotation: Any) -> Any:
    origin = get_origin(annotation)
    if origin is Union or origin is types.UnionType:
        return origin
    return None


def python_type_to_ts(annotation: Any, *, nullable: bool = False) -> str:
    if annotation is type(None):
        return "null"

    if _union_origin(annotation):
        args = get_args(annotation)
        non_null = [a for a in args if a is not type(None)]
        has_null = type(None) in args
        if len(non_null) == 1:
            return python_type_to_ts(non_null[0], nullable=has_null or nullable)
        inner = " | ".join(python_type_to_ts(a) for a in non_null)
        return f"({inner}) | null" if has_null or nullable else inner

    origin = get_origin(annotation)
    if origin is list:
        (item_type,) = get_args(annotation) or (Any,)
        return _nullable(f"Array<{python_type_to_ts(item_type)}>", nullable)

    if origin is dict:
        key_t, val_t = get_args(annotation) or (str, Any)
        return _nullable(f"Record<{python_type_to_ts(key_t)}, {python_type_to_ts(val_t)}>", nullable)

    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return _nullable(annotation.__name__, nullable)

    mapping: dict[Any, str] = {
        int: "number",
        float: "number",
        str: "string",
        bool: "boolean",
        Any: "unknown",
    }
    return _nullable(mapping.get(annotation, "unknown"), nullable)


def _nullable(ts: str, nullable: bool) -> str:
    if nullable and "| null" not in ts:
        return f"{ts} | null"
    return ts


def field_to_ts(name: str, info: FieldInfo) -> str:
    required = info.is_required()
    annotation = info.annotation
    has_null = False
    if _union_origin(annotation) and type(None) in get_args(annotation):
        has_null = True
    ts_type = python_type_to_ts(annotation, nullable=has_null and required)
    suffix = "" if required else "?"
    return f"  {name}{suffix}: {ts_type}"


def model_to_ts(model: type[BaseModel]) -> str:
    lines = [f"export type {model.__name__} = {{"]
    for name, info in _collect_fields(model).items():
        lines.append(field_to_ts(name, info))
    lines.append("}")
    return "\n".join(lines)


def render() -> str:
    chunks = [HEADER]
    for model in MODELS:
        chunks.append(model_to_ts(model))
        chunks.append("")
    return "\n".join(chunks).rstrip() + "\n"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
