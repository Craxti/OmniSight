"""Docker network and workload metadata helpers."""

from __future__ import annotations

from collections import defaultdict

from src.services.autodiscover.discovery.inference.core import make_connection, relation_type_for_target
from src.services.autodiscover.discovery.models import ContainerMeta


def build_workload_metadata(
    processes: list[dict], docker_metadata: dict[str, ContainerMeta]
) -> dict[str, ContainerMeta]:
    """Merge docker inspect metadata with inline env from k8s/native workloads."""
    metadata = dict(docker_metadata)
    for proc in processes:
        hostname = str(proc.get("hostname") or "").strip()
        if not hostname:
            continue
        env = proc.get("env")
        labels = proc.get("labels")
        if isinstance(env, list) or isinstance(labels, dict):
            meta = metadata.get(hostname, ContainerMeta())
            if isinstance(env, list):
                meta.env = list(dict.fromkeys([*meta.env, *[str(item) for item in env]]))
            if isinstance(labels, dict):
                meta.labels = {**meta.labels, **{str(k): str(v) for k, v in labels.items()}}
            metadata[hostname] = meta
    return metadata


def infer_docker_network_connections(
    *,
    entity_types: dict[str, str],
    networks: dict[str, set[str]],
    existing: set[tuple[str, str, str]],
) -> list[dict]:
    """Link app containers to infra on the same custom Docker network."""
    by_network: dict[str, list[str]] = defaultdict(list)
    for container, nets in networks.items():
        for net in nets:
            by_network[net].append(container)
    connections: list[dict] = []
    for members in by_network.values():
        if len(members) < 2:
            continue
        apps = [m for m in members if entity_types.get(m) in ("Application", "Container")]
        infra = [
            m for m in members if entity_types.get(m) in ("Database", "Queue", "Technical Component", "Network Element")
        ]
        for app in apps:
            for target in infra:
                key = (app, target, "depends_on")
                if key in existing:
                    continue
                connections.append(
                    make_connection(
                        source_hostname=app,
                        target_hostname=target,
                        relation_type=relation_type_for_target(entity_types.get(target, ""), target),
                        source="docker_network",
                    )
                )
    return connections
