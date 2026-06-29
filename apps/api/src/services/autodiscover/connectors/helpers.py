from __future__ import annotations

import time
from typing import Any

from src.services.autodiscover.connectors.base import (
    ConnectorDiscoveryResult,
    DiscoveredEntity,
    DiscoverySchema,
)


def build_schema(entities: list[DiscoveredEntity], version: str) -> DiscoverySchema:
    entity_types: set[str] = set()
    fields: set[str] = set()
    for ent in entities:
        if ent.entity_type:
            entity_types.add(ent.entity_type)
        fields.update(ent.fields.keys())
    return DiscoverySchema(version=version, entity_types=sorted(entity_types), fields=sorted(fields))


def raw_to_entity(raw: dict[str, Any]) -> DiscoveredEntity | None:
    match_key = raw.get("match_hostname") or raw.get("hostname") or raw.get("name")
    if not match_key:
        return None
    fields = {k: v for k, v in raw.items() if k not in ("match_hostname", "entity_type") and v is not None}
    return DiscoveredEntity(
        match_key=str(match_key),
        entity_type=raw.get("entity_type") or raw.get("type_name"),
        fields=fields,
        raw=raw,
    )


def entities_from_records(records: list) -> list[DiscoveredEntity]:
    entities: list[DiscoveredEntity] = []
    for raw in records:
        if not isinstance(raw, dict):
            continue
        ent = raw_to_entity(raw)
        if ent:
            entities.append(ent)
    return entities


def success_result(
    connector,
    *,
    entities: list[DiscoveredEntity],
    started: float,
    attempts: int = 1,
) -> ConnectorDiscoveryResult:
    return ConnectorDiscoveryResult(
        ok=True,
        entities=entities,
        schema=build_schema(entities, connector.schema_version),
        duration_ms=int((time.perf_counter() - started) * 1000),
        attempts=attempts,
    )
