"""Tests for host discovery relation inference."""

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "host_discover.py"
_spec = importlib.util.spec_from_file_location("host_discover", SCRIPT)
assert _spec and _spec.loader
host_discover = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(host_discover)


def _processes(*items: dict) -> list[dict]:
    return list(items)


def test_clustering_api_links_only_matching_db_by_name():
    processes = _processes(
        {"hostname": "artimate-clustering-api", "entity_type": "Application"},
        {"hostname": "artimate-clustering-db", "entity_type": "Database"},
        {"hostname": "artimate-anomaly-db", "entity_type": "Database"},
        {"hostname": "artimate-correlation-db", "entity_type": "Database"},
    )
    connections = host_discover.infer_connections(processes, "host-01")
    depends = {(c["source_hostname"], c["target_hostname"]) for c in connections if c["relation_type"] == "depends_on"}
    assert ("artimate-clustering-api", "artimate-clustering-db") in depends
    assert ("artimate-clustering-api", "artimate-anomaly-db") not in depends
    assert ("artimate-clustering-api", "artimate-correlation-db") not in depends


def test_env_reference_links_database():
    processes = _processes(
        {"hostname": "billing-api", "entity_type": "Application"},
        {"hostname": "billing-db", "entity_type": "Database"},
        {"hostname": "orders-db", "entity_type": "Database"},
    )
    metadata = {
        "billing-api": host_discover.ContainerMeta(
            env=["DATABASE_URL=jdbc:postgresql://billing-db:5432/billing"],
        ),
    }
    name_index = host_discover.build_name_index(processes)
    entity_types = {p["hostname"]: p["entity_type"] for p in processes}
    connections = host_discover.infer_env_connections(
        metadata,
        name_index=name_index,
        ip_index={},
        entity_types=entity_types,
        name_tokens=host_discover.known_name_tokens(name_index),
    )
    assert any(
        c["source_hostname"] == "billing-api" and c["target_hostname"] == "billing-db" and c["source"] == "env"
        for c in connections
    )


def test_env_kafka_bootstrap_links_queue():
    processes = _processes(
        {"hostname": "worker-service", "entity_type": "Application"},
        {"hostname": "event-bus", "entity_type": "Queue"},
        {"hostname": "other-bus", "entity_type": "Queue"},
    )
    metadata = {
        "worker-service": host_discover.ContainerMeta(
            env=["KAFKA_BOOTSTRAP_SERVERS=event-bus:9092,other-bus:9092"],
        ),
    }
    name_index = host_discover.build_name_index(processes)
    entity_types = {p["hostname"]: p["entity_type"] for p in processes}
    connections = host_discover.infer_env_connections(
        metadata,
        name_index=name_index,
        ip_index={},
        entity_types=entity_types,
        name_tokens=host_discover.known_name_tokens(name_index),
    )
    targets = {c["target_hostname"] for c in connections if c["source_hostname"] == "worker-service"}
    assert targets == {"event-bus", "other-bus"}


def test_compose_depends_on_links_services():
    processes = _processes(
        {"hostname": "shop-api", "entity_type": "Application"},
        {"hostname": "shop-db", "entity_type": "Database"},
    )
    metadata = {
        "shop-api": host_discover.ContainerMeta(
            labels={
                "com.docker.compose.project": "shop",
                "com.docker.compose.service": "api",
                "com.docker.compose.depends_on": '{"db":{"condition":"service_started"}}',
            },
        ),
        "shop-db": host_discover.ContainerMeta(
            labels={
                "com.docker.compose.project": "shop",
                "com.docker.compose.service": "db",
            },
        ),
    }
    compose_index = host_discover.build_compose_service_index(metadata)
    entity_types = {p["hostname"]: p["entity_type"] for p in processes}
    connections = host_discover.infer_compose_connections(
        metadata,
        entity_types=entity_types,
        compose_index=compose_index,
    )
    assert ("shop-api", "shop-db", "depends_on") in {
        (c["source_hostname"], c["target_hostname"], c["relation_type"]) for c in connections
    }


def test_name_fallback_skipped_when_env_evidence_exists():
    processes = _processes(
        {"hostname": "payments-api", "entity_type": "Application"},
        {"hostname": "payments-db", "entity_type": "Database"},
        {"hostname": "shared-db", "entity_type": "Database"},
    )
    metadata = {
        "payments-api": host_discover.ContainerMeta(
            env=["DB_HOST=shared-db"],
        ),
    }
    name_index = host_discover.build_name_index(processes)
    entity_types = {p["hostname"]: p["entity_type"] for p in processes}
    env_links = host_discover.infer_env_connections(
        metadata,
        name_index=name_index,
        ip_index={},
        entity_types=entity_types,
        name_tokens=host_discover.known_name_tokens(name_index),
    )
    apps_with_evidence = {c["source_hostname"] for c in env_links}
    fallback = host_discover.infer_name_fallback_connections(
        processes,
        apps_with_evidence=apps_with_evidence,
        existing={(c["source_hostname"], c["target_hostname"], c["relation_type"]) for c in env_links},
    )
    assert not any(c["target_hostname"] == "payments-db" for c in fallback)


def test_kafka_zookeeper_linked_within_compose_project():
    processes = _processes(
        {"hostname": "stack-kafka", "entity_type": "Queue"},
        {"hostname": "stack-zookeeper", "entity_type": "Queue"},
        {"hostname": "other-kafka", "entity_type": "Queue"},
        {"hostname": "other-zookeeper", "entity_type": "Queue"},
    )
    metadata = {
        "stack-kafka": host_discover.ContainerMeta(
            labels={"com.docker.compose.project": "stack", "com.docker.compose.service": "kafka"},
        ),
        "stack-zookeeper": host_discover.ContainerMeta(
            labels={"com.docker.compose.project": "stack", "com.docker.compose.service": "zookeeper"},
        ),
        "other-kafka": host_discover.ContainerMeta(
            labels={"com.docker.compose.project": "other", "com.docker.compose.service": "kafka"},
        ),
        "other-zookeeper": host_discover.ContainerMeta(
            labels={"com.docker.compose.project": "other", "com.docker.compose.service": "zookeeper"},
        ),
    }
    connections = host_discover.infer_kafka_zookeeper_links(processes, metadata)
    pairs = {(c["source_hostname"], c["target_hostname"]) for c in connections}
    assert ("stack-kafka", "stack-zookeeper") in pairs
    assert ("other-kafka", "other-zookeeper") in pairs
    assert ("stack-kafka", "other-zookeeper") not in pairs


def test_score_app_db_match_exact_stem():
    assert host_discover.score_app_db_match("billing-api", "billing-db") == 100
    assert host_discover.score_app_db_match("billing-api", "orders-db") == 0


def test_parse_compose_file_depends_on():
    import tempfile

    content = """
services:
  api:
    image: api:latest
    depends_on:
      - db
      - cache
  db:
    image: postgres:16
"""
    with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False, encoding="utf-8") as tmp:
        tmp.write(content)
        path = host_discover.Path(tmp.name)
    parsed = host_discover.parse_compose_file(path)
    assert parsed["api"] == ["db", "cache"]
    path.unlink(missing_ok=True)


def test_infer_compose_file_connections():
    processes = _processes(
        {"hostname": "shop-api", "entity_type": "Application", "container_name": "shop-api"},
        {"hostname": "shop-db", "entity_type": "Database", "container_name": "shop-db"},
    )
    metadata = {
        "shop-api": host_discover.ContainerMeta(
            labels={"com.docker.compose.project": "shop", "com.docker.compose.service": "api"},
        ),
        "shop-db": host_discover.ContainerMeta(
            labels={"com.docker.compose.project": "shop", "com.docker.compose.service": "db"},
        ),
    }
    compose_index = host_discover.build_compose_service_index(metadata)
    entity_types = {p["hostname"]: p["entity_type"] for p in processes}

    import tempfile

    content = "services:\n  api:\n    depends_on:\n      - db\n  db:\n    image: postgres\n"
    with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False, encoding="utf-8") as tmp:
        tmp.write(content)
        compose_path = host_discover.Path(tmp.name)

    original = host_discover.discover_compose_file_paths
    host_discover.discover_compose_file_paths = lambda _meta: [compose_path]
    try:
        connections = host_discover.infer_compose_file_connections(
            processes,
            metadata,
            entity_types=entity_types,
            compose_index=compose_index,
        )
    finally:
        host_discover.discover_compose_file_paths = original
        compose_path.unlink(missing_ok=True)

    assert ("shop-api", "shop-db", "depends_on") in {
        (c["source_hostname"], c["target_hostname"], c["relation_type"]) for c in connections
    }


def test_infer_docker_network_connections():
    entity_types = {
        "billing-api": "Application",
        "billing-db": "Database",
        "billing-cache": "Database",
    }
    networks = {
        "billing-api": {"app_net"},
        "billing-db": {"app_net"},
        "billing-cache": {"other_net"},
    }
    connections = host_discover.infer_docker_network_connections(
        entity_types=entity_types,
        networks=networks,
        existing=set(),
    )
    pairs = {(c["source_hostname"], c["target_hostname"]) for c in connections}
    assert ("billing-api", "billing-db") in pairs
    assert ("billing-api", "billing-cache") not in pairs


def test_parse_ss_listener_line():
    line = 'LISTEN 0 128 0.0.0.0:8080 0.0.0.0:* users:(("java",pid=4821,fd=4))'
    parsed = host_discover._parse_ss_listener_line(line)
    assert parsed == ("java", 8080, "0.0.0.0:8080")


def test_classify_native_process_by_port():
    assert host_discover.classify_native_process("unknown", 5432) == "Database"
    assert host_discover.classify_native_process("unknown", 9092) == "Queue"
    assert host_discover.classify_native_process("myapp", 8080) == "Application"


def test_dedupe_processes_prefers_docker():
    processes = [
        {"hostname": "api", "runtime": "native", "ports": [8080]},
        {"hostname": "api", "runtime": "docker", "ports": [8080]},
    ]
    deduped = host_discover.dedupe_processes(processes)
    assert len(deduped) == 1
    assert deduped[0]["runtime"] == "docker"


def test_relation_type_queue_uses():
    assert host_discover.relation_type_for_target("Queue", "billing-kafka") == "uses"
    assert host_discover.relation_type_for_target("Database", "billing-redis") == "uses"
    assert host_discover.relation_type_for_target("Network Element", "ingress-nginx") == "linked_to"


def test_env_db_host_key():
    hosts = host_discover.hosts_from_env(["DB_HOST=billing-db"], ["billing-db", "billing-api"])
    assert "billing-db" in hosts


def test_resolve_target_by_ip():
    name_index = {"billing-db": "billing-db"}
    ip_index = {"10.0.0.5": "billing-db"}
    assert host_discover.resolve_target_host("10.0.0.5", name_index, ip_index) == "billing-db"


def test_make_connection_includes_confidence():
    conn = host_discover.make_connection(
        source_hostname="api",
        target_hostname="db",
        relation_type="depends_on",
        source="env",
    )
    assert conn["confidence"] == host_discover.EVIDENCE_CONFIDENCE["env"]
