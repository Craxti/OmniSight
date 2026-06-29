"""Shared autodiscover mapping helpers (pure logic)."""

from __future__ import annotations

import re

from src.models import CI
from src.services.autodiscover.connectors.base import DiscoveredEntity
from src.services.autodiscover.normalize import EXTERNAL_ID_FIELDS, TOP_LEVEL_FIELDS


def rules_flag(rules: dict | None, key: str, default: bool = True) -> bool:
    if not rules:
        return default
    if key in rules:
        return bool(rules[key])
    return default


def proposed_ci_name(hostname: str, entity: DiscoveredEntity | None = None) -> str:
    if entity:
        for key in ("service_name", "container_name", "name"):
            val = entity.fields.get(key) or (entity.raw or {}).get(key)
            if val and not str(val).startswith("localhost-app-"):
                slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", str(val).strip()).strip("-").lower()
                if slug:
                    return slug
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", hostname.strip()).strip("-").lower()
    return slug or "discovered-ci"


def template_fields_for_type(ci: CI, rules: dict | None) -> set[str]:
    templates = (rules or {}).get("templates", {})
    ci_type = ci.ci_type.name if ci.ci_type else None
    if ci_type and ci_type in templates:
        return set(templates[ci_type])
    schema_props = (ci.ci_type.attribute_schema or {}).get("properties", {}) if ci.ci_type else {}
    return set(EXTERNAL_ID_FIELDS) | set(TOP_LEVEL_FIELDS) | set(schema_props.keys())
