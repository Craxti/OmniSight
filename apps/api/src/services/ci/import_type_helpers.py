"""Pure helpers for CI import type mapping (no DB/session deps)."""

from __future__ import annotations

import re
from typing import Any

from src.core.constants import RSM_OFFICIAL_TYPE_NAMES
from src.models import CIType
from src.schemas.ci import CITypeCreate

_TYPE_KEYS = ("type_name", "type", "Type", "ci_type", "element_type")


def normalize_type_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def extract_import_type_name(item: dict[str, Any]) -> str | None:
    for key in _TYPE_KEYS:
        raw = item.get(key)
        if raw is not None and str(raw).strip():
            return str(raw).strip()
    return None


def infer_schema_properties(attribute_samples: list[dict[str, Any]]) -> dict[str, Any]:
    keys: set[str] = set()
    for attrs in attribute_samples:
        keys.update(attrs.keys())
    properties: dict[str, Any] = {}
    for key in sorted(keys):
        properties[key] = {"type": "string", "title": key}
    return {"properties": properties}


def suggest_draft_type(source_type: str, attribute_samples: list[dict[str, Any]]) -> CITypeCreate:
    cleaned = re.sub(r"\s+", " ", source_type.strip())
    name = cleaned[:128] if cleaned else "Imported Type"
    description = f"Draft type from import: {source_type}"
    schema = infer_schema_properties(attribute_samples) if attribute_samples else {"properties": {}}
    return CITypeCreate(name=name, description=description, attribute_schema=schema)


def find_best_type_match(source_type: str, existing: list[CIType]) -> tuple[CIType | None, float]:
    norm_source = normalize_type_key(source_type)
    if not norm_source:
        return None, 0.0

    by_norm: dict[str, CIType] = {}
    for row in existing:
        by_norm[normalize_type_key(row.name)] = row

    exact = by_norm.get(norm_source)
    if exact:
        return exact, 1.0

    official_by_norm = {normalize_type_key(name): name for name in RSM_OFFICIAL_TYPE_NAMES}
    if norm_source in official_by_norm:
        official_name = official_by_norm[norm_source]
        for row in existing:
            if row.name == official_name:
                return row, 0.95

    for row in existing:
        norm_name = normalize_type_key(row.name)
        if norm_source in norm_name or norm_name in norm_source:
            return row, 0.75

    return None, 0.0
