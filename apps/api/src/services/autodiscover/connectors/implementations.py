from __future__ import annotations

import json
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.models import SyncConnector
from src.services.autodiscover.connectors.base import ConnectorDiscoveryResult, DiscoveredEntity
from src.services.autodiscover.connectors.helpers import entities_from_records, raw_to_entity, success_result
from src.services.autodiscover.credentials import auth_headers, resolve_database_url


class FileConnector:
    connector_type = "file"

    def __init__(self, connector: SyncConnector):
        self._connector = connector

    def discover(self) -> ConnectorDiscoveryResult:
        started = time.perf_counter()
        path_value = self._connector.config.get("path")
        if not path_value:
            return ConnectorDiscoveryResult(ok=False, error="File connector: path is required", attempts=1)
        path = Path(str(path_value))
        if not path.is_file():
            return ConnectorDiscoveryResult(ok=False, error=f"File not found: {path}", attempts=1)
        try:
            raw_text = path.read_text(encoding="utf-8-sig").strip()
            if not raw_text:
                return ConnectorDiscoveryResult(
                    ok=False,
                    error=f"File is empty: {path}. Add a JSON array of entities.",
                    attempts=1,
                )
            payload = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            return ConnectorDiscoveryResult(
                ok=False,
                error=f"Invalid JSON in {path.name}: {exc}. Expected array like autodiscover_inventory.json",
                attempts=1,
            )
        except OSError as exc:
            return ConnectorDiscoveryResult(ok=False, error=str(exc), attempts=1)
        entities_path = self._connector.config.get("entities_path")
        if entities_path and isinstance(payload, dict):
            records = payload.get(entities_path, [])
        elif isinstance(payload, list):
            records = payload
        else:
            records = payload.get("elements", []) if isinstance(payload, dict) else []
        if not isinstance(records, list):
            return ConnectorDiscoveryResult(ok=False, error="File connector: expected list of entities", attempts=1)
        entities: list[DiscoveredEntity] = []
        for raw in records:
            if not isinstance(raw, dict):
                continue
            ext = raw.get("external_ids") or {}
            merged = {**raw, **ext, "entity_type": raw.get("entity_type") or raw.get("type_name")}
            if "name" in merged and "hostname" not in merged:
                merged.setdefault("match_hostname", merged["name"])
            ent = raw_to_entity(merged)
            if ent:
                entities.append(ent)
        return success_result(self._connector, entities=entities, started=started)


class ApiConnector:
    connector_type = "api"

    def __init__(self, connector: SyncConnector):
        self._connector = connector

    def discover(self) -> ConnectorDiscoveryResult:
        started = time.perf_counter()
        url = self._connector.config.get("url")
        if not url:
            return ConnectorDiscoveryResult(ok=False, error="API connector: url is required", attempts=1)
        headers = auth_headers(self._connector)
        req = Request(str(url), headers=headers, method="GET")
        try:
            with urlopen(req, timeout=self._connector.timeout_seconds) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            return ConnectorDiscoveryResult(ok=False, error=str(exc), attempts=1)
        path = self._connector.config.get("entities_json_path")
        records = payload
        if path:
            for part in str(path).split("."):
                records = records.get(part, []) if isinstance(records, dict) else []
        if not isinstance(records, list):
            return ConnectorDiscoveryResult(ok=False, error="API connector: entities list not found", attempts=1)
        entities = entities_from_records([raw for raw in records if isinstance(raw, dict)])
        return success_result(self._connector, entities=entities, started=started)


class DbConnector:
    connector_type = "db"

    def __init__(self, connector: SyncConnector):
        self._connector = connector

    def discover(self) -> ConnectorDiscoveryResult:
        from sqlalchemy import create_engine, text

        started = time.perf_counter()
        db_url = resolve_database_url(self._connector)
        query = self._connector.config.get("query")
        if not db_url or not query:
            return ConnectorDiscoveryResult(
                ok=False,
                error="DB connector: database_url (or database_url_env) and query are required",
                attempts=1,
            )
        try:
            engine = create_engine(str(db_url), pool_pre_ping=True)
            with engine.connect() as conn:
                rows = conn.execute(text(str(query))).mappings().all()
        except Exception as exc:
            return ConnectorDiscoveryResult(ok=False, error=str(exc), attempts=1)
        entities = entities_from_records([dict(row) for row in rows])
        return success_result(self._connector, entities=entities, started=started)


class StreamConnector:
    connector_type = "stream"

    def __init__(self, connector: SyncConnector):
        self._connector = connector

    def discover(self) -> ConnectorDiscoveryResult:
        snapshot = self._connector.config.get("snapshot")
        if isinstance(snapshot, list):
            entities = entities_from_records([raw for raw in snapshot if isinstance(raw, dict)])
            return success_result(self._connector, entities=entities, started=time.perf_counter(), attempts=1)
        return ConnectorDiscoveryResult(
            ok=False,
            error="Stream connector: configure snapshot[] or stream endpoint in config",
            attempts=1,
        )
