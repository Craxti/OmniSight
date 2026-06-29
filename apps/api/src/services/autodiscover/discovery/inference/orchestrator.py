"""Orchestrates all connection inference strategies."""

from __future__ import annotations

from src.services.autodiscover.discovery.docker_meta import (
    collect_container_metadata,
    collect_container_network_details,
    docker_container_networks,
    enrich_docker_processes,
)
from src.services.autodiscover.discovery.inference.compose import (
    build_compose_service_index,
    infer_compose_connections,
    infer_compose_file_connections,
)
from src.services.autodiscover.discovery.inference.core import dedupe_connections
from src.services.autodiscover.discovery.inference.docker_network import (
    build_workload_metadata,
    infer_docker_network_connections,
)
from src.services.autodiscover.discovery.inference.env_hosts import infer_env_connections
from src.services.autodiscover.discovery.inference.indexes import (
    build_ip_index,
    build_name_index,
    build_proc_to_host_map,
    known_name_tokens,
)
from src.services.autodiscover.discovery.inference.kafka import infer_kafka_zookeeper_links
from src.services.autodiscover.discovery.inference.name_matching import infer_name_fallback_connections
from src.services.autodiscover.discovery.inference.tcp import infer_tcp_connections


def infer_connections(
    processes: list[dict],
    host_hostname: str,
    k8s_service_index: dict[str, str] | None = None,
) -> list[dict]:
    del host_hostname  # hosted_on is resolved in OmniSight from connector Server CI

    container_names = [
        str(p["hostname"]) for p in processes if p.get("hostname") and str(p.get("runtime") or "docker") == "docker"
    ]
    network_details = collect_container_network_details(container_names)
    enrich_docker_processes(processes, network_details)
    docker_metadata = collect_container_metadata(container_names)
    metadata = build_workload_metadata(processes, docker_metadata)
    ip_index = build_ip_index(processes, network_details)
    name_index = build_name_index(processes, k8s_service_index)
    name_tokens = known_name_tokens(name_index)
    entity_types = {str(p["hostname"]): str(p.get("entity_type") or "") for p in processes if p.get("hostname")}
    compose_index = build_compose_service_index(docker_metadata)
    networks = docker_container_networks(container_names)
    proc_to_host = build_proc_to_host_map(processes, ip_index, network_details)

    connections: list[dict] = []
    connections.extend(
        infer_env_connections(
            metadata,
            name_index=name_index,
            ip_index=ip_index,
            entity_types=entity_types,
            name_tokens=name_tokens,
        )
    )
    connections.extend(
        infer_tcp_connections(
            name_index=name_index,
            ip_index=ip_index,
            entity_types=entity_types,
            proc_to_host=proc_to_host,
        )
    )
    connections.extend(infer_compose_connections(metadata, entity_types=entity_types, compose_index=compose_index))
    connections.extend(
        infer_compose_file_connections(
            processes,
            metadata,
            entity_types=entity_types,
            compose_index=compose_index,
        )
    )
    connections.extend(infer_kafka_zookeeper_links(processes, metadata))

    existing = {(c["source_hostname"], c["target_hostname"], c["relation_type"]) for c in connections}
    connections.extend(
        infer_docker_network_connections(
            entity_types=entity_types,
            networks=networks,
            existing=existing,
        )
    )
    existing = {(c["source_hostname"], c["target_hostname"], c["relation_type"]) for c in connections}
    evidence_sources = ("env", "tcp", "compose", "compose_file", "docker_network", "infra", "k8s_service")
    apps_with_evidence = {c["source_hostname"] for c in connections if c.get("source") in evidence_sources}
    connections.extend(
        infer_name_fallback_connections(processes, apps_with_evidence=apps_with_evidence, existing=existing)
    )
    return dedupe_connections(connections)
