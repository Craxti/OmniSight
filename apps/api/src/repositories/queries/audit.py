"""Audit log SELECT builders."""

from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.sql import Select

from src.models import AuditLog, Relation


def audit_search_base() -> Select:
    return select(AuditLog).order_by(AuditLog.id.desc())


def apply_audit_search_filters(
    stmt: Select,
    *,
    entity_type: str | None = None,
    action: str | None = None,
    user_email: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> Select:
    if entity_type:
        stmt = stmt.where(AuditLog.entity_type == entity_type)
    if action:
        stmt = stmt.where(AuditLog.action == action)
    if user_email:
        stmt = stmt.where(AuditLog.user_email == user_email)
    if date_from:
        stmt = stmt.where(AuditLog.created_at >= date_from)
    if date_to:
        stmt = stmt.where(AuditLog.created_at <= f"{date_to}T23:59:59")
    return stmt


def audit_for_entity_select(entity_type: str, entity_id: int, *, limit: int = 50) -> Select:
    return (
        select(AuditLog)
        .where(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
        .order_by(AuditLog.id.desc())
        .limit(limit)
    )


def audit_for_ci_with_relations_select(ci_id: int, relation_ids: list[int], *, limit: int = 50) -> Select:
    conditions = [(AuditLog.entity_type == "ci") & (AuditLog.entity_id == ci_id)]
    if relation_ids:
        conditions.append((AuditLog.entity_type == "relation") & (AuditLog.entity_id.in_(relation_ids)))
    return select(AuditLog).where(or_(*conditions)).order_by(AuditLog.id.desc()).limit(limit)


def relation_ids_for_ci_select(ci_id: int) -> Select:
    return select(Relation.id).where((Relation.source_ci_id == ci_id) | (Relation.target_ci_id == ci_id))
