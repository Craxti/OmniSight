"""Shared relation read serializers."""

from __future__ import annotations

from typing import Any

from src.core.serializers import relation_to_response
from src.schemas.relations import RelationResponse


def serialize_relations(rows: list[Any]) -> list[RelationResponse]:
    return [relation_to_response(r) for r in rows]


def serialize_relation(row: Any) -> RelationResponse:
    return relation_to_response(row)


def serialize_relations_page(rows: list[Any], total: int) -> tuple[list[RelationResponse], int]:
    return serialize_relations(rows), total
