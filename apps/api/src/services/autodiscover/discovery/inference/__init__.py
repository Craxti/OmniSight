"""Connection inference for host discovery — public API."""

from src.services.autodiscover.discovery.inference.compose import (
    build_compose_service_index,
    compose_project,
    compose_service,
    discover_compose_file_paths,
    infer_compose_connections,
    infer_compose_file_connections,
    parse_compose_depends_on,
    parse_compose_file,
)
from src.services.autodiscover.discovery.inference.core import (
    connection_confidence,
    dedupe_connections,
    make_connection,
    relation_type_for_target,
)
from src.services.autodiscover.discovery.inference.docker_network import (
    build_workload_metadata,
    infer_docker_network_connections,
)
from src.services.autodiscover.discovery.inference.env_hosts import (
    hosts_from_env,
    hosts_from_known_names,
    hosts_from_urls,
    infer_env_connections,
)
from src.services.autodiscover.discovery.inference.indexes import (
    build_ip_index,
    build_name_index,
    build_proc_to_host_map,
    known_name_tokens,
    resolve_target_host,
)
from src.services.autodiscover.discovery.inference.kafka import infer_kafka_zookeeper_links
from src.services.autodiscover.discovery.inference.name_matching import (
    app_stem,
    best_name_db_matches,
    db_stem,
    infer_name_fallback_connections,
    score_app_db_match,
)
from src.services.autodiscover.discovery.inference.orchestrator import infer_connections
from src.services.autodiscover.discovery.inference.tcp import infer_tcp_connections

__all__ = [
    "app_stem",
    "best_name_db_matches",
    "build_compose_service_index",
    "build_ip_index",
    "build_name_index",
    "build_proc_to_host_map",
    "build_workload_metadata",
    "compose_project",
    "compose_service",
    "connection_confidence",
    "db_stem",
    "dedupe_connections",
    "discover_compose_file_paths",
    "hosts_from_env",
    "hosts_from_known_names",
    "hosts_from_urls",
    "infer_compose_connections",
    "infer_compose_file_connections",
    "infer_connections",
    "infer_docker_network_connections",
    "infer_env_connections",
    "infer_kafka_zookeeper_links",
    "infer_name_fallback_connections",
    "infer_tcp_connections",
    "known_name_tokens",
    "make_connection",
    "parse_compose_depends_on",
    "parse_compose_file",
    "relation_type_for_target",
    "resolve_target_host",
    "score_app_db_match",
]
