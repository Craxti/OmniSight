"""Relation list SELECT filters and topology edge queries."""

from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import or_, select
from sqlalchemy.orm import aliased, joinedload
from sqlalchemy.sql import Select

from src.models import CI, Relation


def apply_relation_list_filters(
    stmt: Select,
    *,
    relation_type: str | None = None,
    status: str | None = None,
    data_source: str | None = None,
    source_name: str | None = None,
    target_name: str | None = None,
    q: str | None = None,
) -> Select:
    if relation_type:
        stmt = stmt.where(Relation.relation_type == relation_type)
    if status:
        stmt = stmt.where(Relation.status == status)
    if data_source:
        stmt = stmt.where(Relation.data_source.ilike(f"%{data_source}%"))

    if source_name or target_name or q:
        source_ci = aliased(CI)
        target_ci = aliased(CI)
        stmt = stmt.join(source_ci, Relation.source_ci_id == source_ci.id).join(
            target_ci, Relation.target_ci_id == target_ci.id
        )
        if source_name:
            stmt = stmt.where(source_ci.name.ilike(f"%{source_name}%"))
        if target_name:
            stmt = stmt.where(target_ci.name.ilike(f"%{target_name}%"))
        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(
                or_(
                    source_ci.name.ilike(pattern),
                    target_ci.name.ilike(pattern),
                    Relation.data_source.ilike(pattern),
                    Relation.relation_type.ilike(pattern),
                    Relation.status.ilike(pattern),
                )
            )
    return stmt


def relation_active_base() -> Select:
    return (
        select(Relation)
        .options(joinedload(Relation.source_ci), joinedload(Relation.target_ci))
        .where(Relation.is_deleted.is_(False))
    )


def depends_on_edges_select() -> Select:
    return select(Relation.source_ci_id, Relation.target_ci_id).where(
        Relation.is_deleted.is_(False),
        Relation.status != "archived",
        Relation.relation_type == "depends_on",
    )


def dependency_adjacency_select(
    *,
    ci_ids: set[int] | None = None,
    relation_types: tuple[str, ...],
) -> Select:
    """Edges for topology BFS. When ``ci_ids`` is set, both endpoints must be in the set."""
    stmt = select(Relation.source_ci_id, Relation.target_ci_id).where(
        Relation.is_deleted.is_(False),
        Relation.status != "archived",
        Relation.relation_type.in_(relation_types),
    )
    if ci_ids is not None:
        stmt = stmt.where(
            Relation.source_ci_id.in_(ci_ids),
            Relation.target_ci_id.in_(ci_ids),
        )
    return stmt


def incoming_with_source_select(
    target_ci_ids: set[int],
    relation_types: tuple[str, ...],
) -> Select:
    return (
        relation_active_base()
        .options(joinedload(Relation.source_ci).joinedload(CI.ci_type))
        .where(Relation.target_ci_id.in_(target_ci_ids))
        .where(Relation.relation_type.in_(relation_types))
    )


def relation_ids_touching_ci_select(ci_id: int) -> Select:
    return select(Relation.id).where((Relation.source_ci_id == ci_id) | (Relation.target_ci_id == ci_id))


def build_adjacency_from_edges(
    rows: Iterable[tuple[int, int]],
) -> tuple[dict[int, set[int]], dict[int, set[int]]]:
    forward: dict[int, set[int]] = {}
    reverse: dict[int, set[int]] = {}
    for source_id, target_id in rows:
        forward.setdefault(source_id, set()).add(target_id)
        reverse.setdefault(target_id, set()).add(source_id)
    return forward, reverse
