"""Shared import/export read helpers (sync + async)."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from src.core.serializers import ci_snapshot, relation_snapshot
from src.models import CI
from src.schemas.export_filters import CiExportFilter
from src.services.ci.import_type_helpers import (
    extract_import_type_name,
    find_best_type_match,
    suggest_draft_type,
)
from src.services.domain.ci_types import type_to_dict


def filter_cis_for_export(
    cis: list[CI],
    *,
    criticality: str | None = None,
    service_code: str | None = None,
) -> list[CI]:
    if criticality:
        cis = [c for c in cis if c.criticality == criticality]
    if service_code:
        cis = [c for c in cis if c.search_service_code == service_code]
    return cis


def build_import_type_preview(existing: list[Any], items: list[dict[str, Any]]) -> dict[str, Any]:
    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    missing_type_items = 0

    for item in items:
        type_name = extract_import_type_name(item)
        if not type_name:
            missing_type_items += 1
            continue
        by_type[type_name].append(item)

    proposals: list[dict[str, Any]] = []
    for source_type, grouped in sorted(by_type.items(), key=lambda x: x[0].casefold()):
        match, confidence = find_best_type_match(source_type, existing)
        attrs = [dict(item.get("attributes") or {}) for item in grouped]
        if match and confidence >= 0.95:
            proposals.append(
                {
                    "source_type": source_type,
                    "item_count": len(grouped),
                    "status": "matched",
                    "matched_type_id": match.id,
                    "matched_type_name": match.name,
                    "suggestion_confidence": confidence,
                    "draft": None,
                }
            )
            continue
        if match and confidence >= 0.7:
            proposals.append(
                {
                    "source_type": source_type,
                    "item_count": len(grouped),
                    "status": "suggested_match",
                    "matched_type_id": match.id,
                    "matched_type_name": match.name,
                    "suggestion_confidence": confidence,
                    "draft": suggest_draft_type(source_type, attrs).model_dump(),
                }
            )
            continue
        proposals.append(
            {
                "source_type": source_type,
                "item_count": len(grouped),
                "status": "unknown",
                "matched_type_id": None,
                "matched_type_name": None,
                "suggestion_confidence": None,
                "draft": suggest_draft_type(source_type, attrs).model_dump(),
            }
        )

    return {
        "proposals": proposals,
        "existing_types": [type_to_dict(t) for t in existing],
        "missing_type_items": missing_type_items,
        "needs_mapping": any(p["status"] != "matched" for p in proposals),
    }


def build_export_full_payload(
    cis: list[CI],
    relations: list[Any],
    filters: CiExportFilter,
) -> dict[str, Any]:
    return {
        "filters": filters.as_dict(),
        "elements": [ci_snapshot(c) for c in cis],
        "relations": [relation_snapshot(r) for r in relations],
    }
