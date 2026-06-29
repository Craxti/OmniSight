"""Shared relation type catalog serializers."""

from __future__ import annotations

from typing import Any


def relation_type_to_dict(row: Any) -> dict:
    return {
        "id": row.id,
        "name": row.name,
        "description": row.description,
        "is_official": row.is_official,
    }


def list_relation_type_dicts(rows: list[Any]) -> list[dict]:
    return [relation_type_to_dict(row) for row in rows]
