from __future__ import annotations

from typing import Any

from src.services.autodiscover.connectors.base import DiscoveredEntity
from src.services.autodiscover.port_constants import DB_PORTS, QUEUE_PORTS


def _append_relation(raw: dict, relation_type: str, target: str, **meta: object) -> None:
    relations = raw.setdefault("relations", [])
    if not isinstance(relations, list):
        return
    for item in relations:
        if isinstance(item, dict) and item.get("type") == relation_type and item.get("target_hostname") == target:
            return
    entry: dict[str, object] = {"type": relation_type, "target_hostname": target}
    entry.update({k: v for k, v in meta.items() if v is not None})
    relations.append(entry)


def _infer_target_hostname(conn: dict) -> str | None:
    if host := conn.get("target_hostname") or conn.get("target"):
        return str(host).strip()
    target_ip = conn.get("target_ip") or conn.get("ip")
    if target_ip:
        return str(target_ip).strip()
    return None


def agent_payload_to_entities(payload: dict[str, Any]) -> list[DiscoveredEntity]:
    """Convert host-agent JSON (processes, connections) into discovered entities."""
    entity_index: dict[str, dict[str, Any]] = {}

    host = payload.get("host") or {}
    host_hostname = str(host.get("hostname") or host.get("name") or "").strip()
    if host_hostname:
        entity_index[host_hostname] = {"entity_type": "Server", **host}

    for proc in payload.get("processes") or []:
        if not isinstance(proc, dict):
            continue
        match_key = str(proc.get("hostname") or proc.get("match_hostname") or proc.get("name") or "").strip()
        if not match_key:
            continue
        entity_type = str(proc.get("entity_type") or "Application")
        raw = entity_index.get(match_key, {"entity_type": entity_type, "hostname": match_key})
        for key, val in proc.items():
            if key in ("hostname", "match_hostname", "name", "entity_type", "pid") or val is None:
                continue
            raw[key] = val
        raw["entity_type"] = entity_type
        raw["hostname"] = match_key
        if proc.get("service_name"):
            raw["service_name"] = proc["service_name"]
        if proc.get("container_name"):
            raw["container_name"] = proc["container_name"]
        if host_hostname and entity_type != "Server":
            _append_relation(raw, "hosted_on", host_hostname)
        entity_index[match_key] = raw

    for conn in payload.get("connections") or []:
        if not isinstance(conn, dict):
            continue
        source = str(conn.get("source_hostname") or conn.get("source") or "").strip()
        target = _infer_target_hostname(conn)
        if not source or not target:
            continue
        rtype = str(conn.get("relation_type") or "depends_on")
        port = conn.get("target_port")
        if not conn.get("relation_type") and port in DB_PORTS:
            rtype = "depends_on"
        elif not conn.get("relation_type") and port in QUEUE_PORTS:
            rtype = "depends_on"
        raw = entity_index.get(source, {"entity_type": "Application", "hostname": source})
        rel_meta: dict[str, object] = {}
        if conn.get("source"):
            rel_meta["evidence"] = conn["source"]
        if conn.get("confidence") is not None:
            rel_meta["confidence"] = conn["confidence"]
        target_ip = conn.get("target_ip") or conn.get("ip")
        if target_ip:
            rel_meta["target_ip"] = str(target_ip).strip()
        _append_relation(raw, rtype, target, **rel_meta)
        entity_index[source] = raw

    entities: list[DiscoveredEntity] = []
    for match_key, raw in entity_index.items():
        entity_type = str(raw.get("entity_type") or "Application")
        fields = {
            k: v for k, v in raw.items() if k not in ("hostname", "name", "entity_type", "relations") and v is not None
        }
        entities.append(
            DiscoveredEntity(
                match_key=match_key,
                entity_type=entity_type,
                fields=fields,
                raw=raw,
            )
        )
    return entities
