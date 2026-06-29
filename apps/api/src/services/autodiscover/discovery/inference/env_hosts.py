"""Environment and URL based host resolution."""

from __future__ import annotations

import re

from src.services.autodiscover.discovery.constants import HOST_ENV_KEY_RE, SKIP_HOSTS, URL_HOST_RE
from src.services.autodiscover.discovery.inference.core import make_connection, relation_type_for_target
from src.services.autodiscover.discovery.inference.indexes import resolve_target_host
from src.services.autodiscover.discovery.models import ContainerMeta


def hosts_from_urls(value: str) -> set[str]:
    hosts: set[str] = set()
    for match in URL_HOST_RE.finditer(value):
        host = match.group(1).split(":")[0].lower()
        if host not in SKIP_HOSTS:
            hosts.add(host)
    return hosts


def hosts_from_known_names(value: str, name_tokens: list[str]) -> set[str]:
    """Match env/config values against discovered container names (universal)."""
    lowered = value.lower()
    found: set[str] = set()
    for token in name_tokens:
        if len(token) < 3:
            continue
        if re.search(rf"(?<![a-z0-9._-]){re.escape(token)}(?![a-z0-9._-])", lowered):
            found.add(token)
    return found


def hosts_from_env(env_lines: list[str], name_tokens: list[str]) -> set[str]:
    hosts: set[str] = set()
    for line in env_lines:
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not value:
            continue
        hosts |= hosts_from_urls(value)
        hosts |= hosts_from_known_names(value, name_tokens)
        if HOST_ENV_KEY_RE.match(key) or key.upper().endswith(("_HOST", "_HOSTNAME", "_ADDR", "_SERVER")):
            for chunk in re.split(r"[,;\s]+", value):
                chunk = chunk.strip()
                if not chunk:
                    continue
                host = chunk.split(":")[0].lower()
                if host not in SKIP_HOSTS:
                    hosts.add(host)
        if any(sep in value for sep in (",", ";")):
            for chunk in re.split(r"[,;]", value):
                chunk = chunk.strip()
                if not chunk:
                    continue
                host = chunk.split(":")[0].lower()
                if host not in SKIP_HOSTS:
                    hosts.add(host)
    return hosts


def infer_env_connections(
    metadata: dict[str, ContainerMeta],
    *,
    name_index: dict[str, str],
    ip_index: dict[str, str],
    entity_types: dict[str, str],
    name_tokens: list[str],
) -> list[dict]:
    connections: list[dict] = []
    for container, meta in metadata.items():
        source_type = entity_types.get(container, "")
        if source_type not in ("Application", "Container"):
            continue
        for host in hosts_from_env(meta.env, name_tokens):
            target = resolve_target_host(host, name_index, ip_index)
            if not target or target == container:
                continue
            target_type = entity_types.get(target, "")
            if target_type not in ("Database", "Queue", "Technical Component", "Network Element"):
                continue
            connections.append(
                make_connection(
                    source_hostname=container,
                    target_hostname=target,
                    relation_type=relation_type_for_target(target_type, target),
                    source="env",
                )
            )
    return connections
