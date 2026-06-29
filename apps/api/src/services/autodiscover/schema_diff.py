from __future__ import annotations

from typing import Any


def schema_fingerprint(schema: dict[str, Any] | None) -> dict[str, Any]:
    if not schema:
        return {"version": "0", "entity_types": [], "fields": []}
    return {
        "version": schema.get("version", "0"),
        "entity_types": sorted(schema.get("entity_types", [])),
        "fields": sorted(schema.get("fields", [])),
    }


def diff_schemas(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
    prev = schema_fingerprint(previous)
    cur = schema_fingerprint(current)
    prev_fields = set(prev.get("fields", []))
    cur_fields = set(cur.get("fields", []))
    prev_types = set(prev.get("entity_types", []))
    cur_types = set(cur.get("entity_types", []))
    return {
        "added_fields": sorted(cur_fields - prev_fields),
        "removed_fields": sorted(prev_fields - cur_fields),
        "added_entity_types": sorted(cur_types - prev_types),
        "removed_entity_types": sorted(prev_types - cur_types),
        "version_changed": prev.get("version") != cur.get("version"),
    }


def merge_schema(schemas: list[dict]) -> dict[str, Any]:
    entity_types: set[str] = set()
    fields: set[str] = set()
    version = "1"
    for schema in schemas:
        if not schema:
            continue
        version = schema.get("version", version)
        entity_types.update(schema.get("entity_types", []))
        fields.update(schema.get("fields", []))
    return schema_fingerprint({"version": version, "entity_types": list(entity_types), "fields": list(fields)})
