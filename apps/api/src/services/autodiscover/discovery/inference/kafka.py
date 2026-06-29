"""Kafka / Zookeeper pairing heuristics."""

from __future__ import annotations

from collections import defaultdict

from src.services.autodiscover.discovery.inference.compose import compose_project
from src.services.autodiscover.discovery.inference.core import make_connection
from src.services.autodiscover.discovery.models import ContainerMeta


def infer_kafka_zookeeper_links(
    processes: list[dict],
    metadata: dict[str, ContainerMeta],
) -> list[dict]:
    """Link kafka brokers to zookeeper within the same compose project, or when unambiguous."""
    kafkas = [p["hostname"] for p in processes if p.get("entity_type") == "Queue" and "kafka" in p["hostname"].lower()]
    zoos = [
        p["hostname"] for p in processes if p.get("entity_type") == "Queue" and "zookeeper" in p["hostname"].lower()
    ]
    if not kafkas or not zoos:
        return []
    connections: list[dict] = []

    def project_of(name: str) -> str | None:
        meta = metadata.get(name)
        return compose_project(meta.labels) if meta else None

    by_project: dict[str | None, list[str]] = defaultdict(list)
    for kafka in kafkas:
        by_project[project_of(kafka)].append(kafka)

    zoo_by_project: dict[str | None, list[str]] = defaultdict(list)
    for zoo in zoos:
        zoo_by_project[project_of(zoo)].append(zoo)

    for project, project_kafkas in by_project.items():
        project_zoos = zoo_by_project.get(project, [])
        if len(project_zoos) == 1:
            for kafka in project_kafkas:
                connections.append(
                    make_connection(
                        source_hostname=kafka,
                        target_hostname=project_zoos[0],
                        relation_type="linked_to",
                        source="infra",
                    )
                )
        elif project is None and len(kafkas) == 1 and len(zoos) == 1:
            connections.append(
                make_connection(
                    source_hostname=kafkas[0],
                    target_hostname=zoos[0],
                    relation_type="linked_to",
                    source="infra",
                )
            )
    return connections
