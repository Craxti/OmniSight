"""Autodiscover scan pipeline value objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.models import SyncConnector


@dataclass
class ScanConfig:
    profile: Any
    connector_ids: list[int] | None
    server_ci_ids: list[int]
    source_types: list[str] | None
    scope_mode: str
    scope_config: dict[str, Any]
    mapping_rules: dict[str, Any]
    connectors: list[SyncConnector]
    previous_schema: dict[str, Any] | None


@dataclass
class CollectResult:
    source_reports: list[dict[str, Any]]
    all_mappings: list[dict[str, Any]]
    schemas: list[dict[str, Any]]
    sources_ok: int
