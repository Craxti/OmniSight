from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from src.models import SyncConnector
from src.services.autodiscover.connectors.base import (
    ConnectorDiscoveryResult,
    DiscoveredEntity,
    DiscoverySchema,
)
from src.services.autodiscover.credentials import resolve_credentials
from src.services.autodiscover.host_agent import agent_payload_to_entities
from src.services.autodiscover.ssh_collect import discover_via_ssh


def _build_schema(entities: list[DiscoveredEntity], version: str) -> DiscoverySchema:
    entity_types: set[str] = set()
    fields: set[str] = set()
    for ent in entities:
        if ent.entity_type:
            entity_types.add(ent.entity_type)
        fields.update(ent.fields.keys())
    return DiscoverySchema(version=version, entity_types=sorted(entity_types), fields=sorted(fields))


def _load_snapshot(path: Path) -> dict[str, Any]:
    raw_text = path.read_text(encoding="utf-8-sig").strip()
    if not raw_text:
        raise ValueError(f"Snapshot file is empty: {path}")
    payload = json.loads(raw_text)
    if not isinstance(payload, dict):
        raise ValueError("Host snapshot must be a JSON object with host/processes/connections")
    return payload


def _ssh_ready(connector: SyncConnector) -> bool:
    config = connector.config or {}
    if str(config.get("ssh_host") or "").strip():
        return True
    creds = resolve_credentials(connector)
    auth = str(creds.get("auth_type") or "none").lower()
    if auth in ("basic", "ssh_key"):
        return bool(
            creds.get("password")
            or creds.get("private_key")
            or creds.get("private_key_path")
            or config.get("ssh_key_path")
        )
    return False


class HostConnector:
    """Collect inventory from target host via SSH agent script or local snapshot (demo)."""

    connector_type = "host"

    def __init__(self, connector: SyncConnector, server_hostname: str | None = None):
        self._connector = connector
        self._server_hostname = server_hostname

    def discover(self) -> ConnectorDiscoveryResult:
        started = time.perf_counter()
        mode = str(self._connector.config.get("mode") or "auto").lower()
        snapshot_path = self._connector.config.get("snapshot_path")
        inline = self._connector.config.get("snapshot")

        payload: dict[str, Any] | None = None
        errors: list[str] = []

        use_ssh = mode in ("auto", "ssh") and _ssh_ready(self._connector)
        use_snapshot = mode in ("auto", "snapshot") and (inline or snapshot_path)
        prefer_snapshot = (
            mode == "auto" and use_snapshot and not str(self._connector.config.get("ssh_host") or "").strip()
        )

        if prefer_snapshot and use_snapshot:
            try:
                if isinstance(inline, dict):
                    payload = inline
                elif snapshot_path:
                    path = Path(str(snapshot_path))
                    if path.is_file():
                        payload = _load_snapshot(path)
                    else:
                        errors.append(f"Snapshot not found: {snapshot_path}")
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                errors.append(str(exc))

        if payload is None and (use_ssh or mode == "ssh"):
            try:
                payload = discover_via_ssh(self._connector, self._server_hostname)
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                errors.append(f"SSH: {exc}")
                if mode == "ssh":
                    return ConnectorDiscoveryResult(ok=False, error=errors[-1], attempts=1)

        if payload is None and use_snapshot:
            try:
                if isinstance(inline, dict):
                    payload = inline
                elif snapshot_path:
                    path = Path(str(snapshot_path))
                    if path.is_file():
                        payload = _load_snapshot(path)
                    else:
                        errors.append(f"Snapshot not found: {snapshot_path}")
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                errors.append(str(exc))

        if payload is None:
            hint = "Настройте SSH: адрес (IP), логин и пароль/ключ. Или для демо укажите путь к host_snapshot_*.json"
            return ConnectorDiscoveryResult(
                ok=False,
                error=errors[-1] if errors else hint,
                attempts=1,
            )

        entities = agent_payload_to_entities(payload)
        if not entities:
            err = payload.get("error") if isinstance(payload, dict) else None
            return ConnectorDiscoveryResult(
                ok=False,
                error=err or "Host discovery returned no entities",
                attempts=1,
            )
        schema = _build_schema(entities, self._connector.schema_version)
        return ConnectorDiscoveryResult(
            ok=True,
            entities=entities,
            schema=schema,
            duration_ms=int((time.perf_counter() - started) * 1000),
            attempts=1,
        )
