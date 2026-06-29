"""Autodiscover scope field helpers (pure logic)."""

from __future__ import annotations

from src.models import CI
from src.services.rsm.indexed_ids import merge_external_ids


def current_field_value(ci: CI, field: str) -> str | None:
    if field in {"environment", "owner", "criticality", "team"}:
        val = getattr(ci, field, None)
        return str(val) if val else None
    if field in {"hostname", "ip", "externalId", "serviceCode", "applicationCode"}:
        ext = merge_external_ids(ci.attributes, ci.external_ids)
        val = ext.get(field)
        return str(val) if val else None
    if field.startswith("attributes."):
        key = field.split(".", 1)[1]
        val = (ci.attributes or {}).get(key)
        return str(val) if val else None
    val = (ci.attributes or {}).get(field)
    return str(val) if val else None


def hostname_of(ci: CI) -> str | None:
    ext = merge_external_ids(ci.attributes, ci.external_ids)
    host = ext.get("hostname")
    return str(host).strip() if host else None


def ssh_target_of(ci: CI) -> str | None:
    ext = merge_external_ids(ci.attributes, ci.external_ids)
    host = ext.get("hostname") or ext.get("ip") or ci.search_hostname or ci.search_ip
    return str(host).strip() if host else None
