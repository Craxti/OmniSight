from typing import Any

from src.models import CI, AuditLog, Relation
from src.schemas.audit import AuditLogResponse
from src.schemas.ci import CIDetailResponse, CIResponse
from src.schemas.relations import RelationResponse


def ci_to_response(ci: CI) -> CIResponse:
    return CIResponse(
        id=ci.id,
        name=ci.name,
        type=ci.ci_type.name if ci.ci_type else None,
        type_id=ci.type_id,
        description=ci.description,
        status=ci.status,
        criticality=ci.criticality,
        environment=ci.environment,
        owner=ci.owner,
        team=ci.team,
        attributes=ci.attributes or {},
        external_ids=ci.external_ids or {},
        last_changed_at=ci.updated_at.isoformat() if ci.updated_at else None,
        created_at=ci.created_at.isoformat() if ci.created_at else None,
    )


def ci_to_detail(ci: CI) -> CIDetailResponse:
    return CIDetailResponse(
        **ci_to_response(ci).model_dump(),
        relations={
            "outgoing": [relation_to_response(r).model_dump() for r in ci.outgoing_relations if not r.is_deleted],
            "incoming": [relation_to_response(r).model_dump() for r in ci.incoming_relations if not r.is_deleted],
        },
    )


def relation_to_response(rel: Relation) -> RelationResponse:
    return RelationResponse(
        id=rel.id,
        source_ci_id=rel.source_ci_id,
        target_ci_id=rel.target_ci_id,
        source_name=rel.source_ci.name if rel.source_ci else None,
        target_name=rel.target_ci.name if rel.target_ci else None,
        relation_type=rel.relation_type,
        status=rel.status,
        data_source=rel.data_source,
        direction="source_to_target",
        created_at=rel.created_at.isoformat() if rel.created_at else None,
        last_changed_at=rel.updated_at.isoformat() if rel.updated_at else None,
    )


def audit_to_response(entry: AuditLog) -> AuditLogResponse:
    return AuditLogResponse(
        id=entry.id,
        entity_type=entry.entity_type,
        entity_id=entry.entity_id,
        action=entry.action,
        user_email=entry.user_email,
        old_value=entry.old_value,
        new_value=entry.new_value,
        created_at=entry.created_at.isoformat() if entry.created_at else None,
    )


def ci_snapshot(ci: CI) -> dict[str, Any]:
    """JSON-serializable snapshot for audit and export."""
    return ci_to_response(ci).model_dump()


def ci_audit_snapshot(ci: CI) -> dict[str, Any]:
    """Audit snapshot without lazy-loaded relationships (async-safe)."""
    return {
        "id": ci.id,
        "name": ci.name,
        "type": None,
        "type_id": ci.type_id,
        "description": ci.description,
        "status": ci.status,
        "criticality": ci.criticality,
        "environment": ci.environment,
        "owner": ci.owner,
        "team": ci.team,
        "attributes": ci.attributes or {},
        "external_ids": ci.external_ids or {},
        "last_changed_at": ci.updated_at.isoformat() if ci.updated_at else None,
        "created_at": ci.created_at.isoformat() if ci.created_at else None,
    }


def ci_to_dict(ci: CI, include_relations: bool = False) -> dict[str, Any]:
    """Backward-compatible alias for audit/export snapshots."""
    if include_relations:
        return ci_to_detail(ci).model_dump()
    return ci_snapshot(ci)


def relation_snapshot(rel: Relation) -> dict[str, Any]:
    return relation_to_response(rel).model_dump()


def relation_to_dict(rel: Relation) -> dict[str, Any]:
    return relation_snapshot(rel)


def build_field_diff(old: dict | None, new: dict | None) -> dict[str, dict[str, Any]]:
    old = old or {}
    new = new or {}
    keys = set(old.keys()) | set(new.keys())
    diff: dict[str, dict[str, Any]] = {}
    for key in keys:
        if old.get(key) != new.get(key):
            diff[key] = {"old": old.get(key), "new": new.get(key)}
    return diff
