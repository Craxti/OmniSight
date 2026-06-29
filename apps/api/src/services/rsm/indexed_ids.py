"""Denormalized search columns for indexed lookup at scale (FR 9, §9)."""

from src.core.constants import SEARCH_INDEX_FIELDS
from src.models import CI


def merge_external_ids(attrs: dict | None, external: dict | None) -> dict:
    merged = dict(external or {})
    attrs = attrs or {}
    for key in (*SEARCH_INDEX_FIELDS, "cmdbId"):
        if key in attrs and attrs[key]:
            merged[key] = attrs[key]
    return merged


def sync_search_indexes(ci: CI) -> None:
    ext = merge_external_ids(ci.attributes, ci.external_ids)
    ci.search_hostname = ext.get("hostname") or None
    ci.search_ip = ext.get("ip") or None
    ci.search_service_code = ext.get("serviceCode") or None
    ci.search_application_code = ext.get("applicationCode") or None
    ci.search_external_id = ext.get("externalId") or None
