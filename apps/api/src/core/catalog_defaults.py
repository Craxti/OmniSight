"""Idempotent catalog defaults (official CI and relation types)."""

from __future__ import annotations

from sqlalchemy.orm import Session
from src.core.constants import RELATION_TYPES, RSM_OFFICIAL_TYPE_NAMES
from src.core.session_commit import commit_session
from src.models import CIType
from src.models.relation_type import RelationType

DEFAULT_TYPE_SCHEMAS: dict[str, dict] = {
    "Server": {
        "properties": {
            "hostname": {"type": "string"},
            "ip": {"type": "string"},
            "port": {"type": "integer"},
            "os": {"type": "string"},
        }
    },
    "Database": {
        "properties": {
            "hostname": {"type": "string"},
            "ip": {"type": "string"},
            "engine": {"type": "string"},
            "port": {"type": "integer"},
        }
    },
    "Application": {
        "properties": {
            "hostname": {"type": "string"},
            "serviceCode": {"type": "string"},
            "applicationCode": {"type": "string"},
            "health_url": {"type": "string"},
        }
    },
    "Business Service": {
        "properties": {
            "serviceCode": {"type": "string"},
            "sla_tier": {"type": "string"},
        }
    },
    "Technical Component": {
        "properties": {
            "hostname": {"type": "string"},
            "ip": {"type": "string"},
            "port": {"type": "integer"},
            "engine": {"type": "string"},
            "runtime_status": {"type": "string"},
        }
    },
}


def ensure_catalog_defaults(db: Session) -> None:
    """Ensure built-in catalog entries exist; safe to run on every startup."""
    existing_ci_types = {row.name: row for row in db.query(CIType).all()}
    for name in RSM_OFFICIAL_TYPE_NAMES:
        row = existing_ci_types.get(name)
        if row is None:
            db.add(
                CIType(
                    name=name,
                    description=f"Official RSM type: {name}",
                    attribute_schema=DEFAULT_TYPE_SCHEMAS.get(name, {"properties": {}}),
                    is_official=True,
                )
            )
        elif not row.is_official:
            row.is_official = True

    existing_relation_types = {row.name: row for row in db.query(RelationType).all()}
    for name in RELATION_TYPES:
        rel_row = existing_relation_types.get(name)
        if rel_row is None:
            db.add(RelationType(name=name, description=None, is_official=True))
        else:
            if not rel_row.is_official:
                rel_row.is_official = True
            if rel_row.description and rel_row.description.startswith("Official relation type:"):
                rel_row.description = None

    commit_session(db)
