"""Shared graph layout read helpers."""

from __future__ import annotations

from typing import Any

from src.schemas.resources import GraphLayoutPosition, GraphLayoutResponse


def layout_positions(row: Any | None) -> dict:
    return row.positions if row else {}


def layout_response(
    resource_id: int,
    relation_filter: str,
    positions: dict,
) -> GraphLayoutResponse:
    return GraphLayoutResponse(
        root_ci_id=resource_id,
        relation_filter=relation_filter,
        positions={
            str(node_id): GraphLayoutPosition(**pos) if isinstance(pos, dict) else pos
            for node_id, pos in (positions or {}).items()
        },
    )
