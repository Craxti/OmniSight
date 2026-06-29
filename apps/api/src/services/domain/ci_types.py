"""Shared CI type list read serializers."""

from __future__ import annotations

from typing import Any


def type_to_dict(t: Any) -> dict:
    return {
        "id": t.id,
        "name": t.name,
        "description": t.description,
        "attribute_schema": t.attribute_schema,
        "is_official": t.is_official,
        "is_import_draft": t.is_import_draft,
    }


def list_type_dicts(types: list[Any]) -> list[dict]:
    return [type_to_dict(t) for t in types]
