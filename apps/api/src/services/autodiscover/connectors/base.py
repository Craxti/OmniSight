from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class DiscoveredEntity:
    match_key: str
    entity_type: str | None
    fields: dict[str, Any]
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class DiscoverySchema:
    version: str
    entity_types: list[str]
    fields: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {"version": self.version, "entity_types": self.entity_types, "fields": sorted(self.fields)}


@dataclass
class ConnectorDiscoveryResult:
    ok: bool
    entities: list[DiscoveredEntity] = field(default_factory=list)
    schema: DiscoverySchema | None = None
    error: str | None = None
    duration_ms: int = 0
    attempts: int = 0


class DiscoveryConnector(Protocol):
    connector_type: str

    def discover(self) -> ConnectorDiscoveryResult: ...
