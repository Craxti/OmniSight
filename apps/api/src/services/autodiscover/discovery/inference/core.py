"""Connection primitives shared by inference strategies."""

from __future__ import annotations

from src.services.autodiscover.discovery.constants import EVIDENCE_CONFIDENCE


def relation_type_for_target(target_type: str, target_name: str) -> str:
    lowered = target_name.lower()
    if target_type == "Queue" and "zookeeper" in lowered:
        return "linked_to"
    if target_type == "Database" and any(x in lowered for x in ("redis", "memcached")):
        return "uses"
    if target_type == "Queue":
        return "uses"
    if target_type == "Network Element":
        return "linked_to"
    if target_type == "Technical Component":
        return "linked_to"
    return "depends_on"


def connection_confidence(source: str) -> float:
    return EVIDENCE_CONFIDENCE.get(source, 0.85)


def make_connection(
    *,
    source_hostname: str,
    target_hostname: str,
    relation_type: str,
    source: str,
    target_ip: str | None = None,
    target_port: int | None = None,
) -> dict:
    conn: dict = {
        "source_hostname": source_hostname,
        "target_hostname": target_hostname,
        "relation_type": relation_type,
        "source": source,
        "confidence": connection_confidence(source),
    }
    if target_ip:
        conn["target_ip"] = target_ip
    if target_port:
        conn["target_port"] = target_port
    return conn


def dedupe_connections(connections: list[dict]) -> list[dict]:
    seen: set[tuple[str, str, str]] = set()
    unique: list[dict] = []
    for conn in connections:
        key = (conn["source_hostname"], conn["target_hostname"], conn["relation_type"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(conn)
    return unique
