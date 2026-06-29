"""Host agent discovery tests."""

import json

from src.core.fixture_paths import fixture_path
from src.services.autodiscover.connectors.host_connector import HostConnector
from src.services.autodiscover.host_agent import agent_payload_to_entities

FIXTURE = fixture_path("host_snapshot_pay_srv.json")


def test_agent_payload_builds_entities_and_relations():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    entities = agent_payload_to_entities(payload)
    keys = {e.match_key for e in entities}
    assert "pay-srv-01" in keys
    assert "app-01" in keys
    app = next(e for e in entities if e.match_key == "app-01")
    relations = app.raw.get("relations") or []
    types = {(r.get("type"), r.get("target_hostname")) for r in relations if isinstance(r, dict)}
    assert ("hosted_on", "pay-srv-01") in types
    assert ("depends_on", "demo-db") in types


def test_agent_payload_infers_docker_relations():
    payload = {
        "host": {"hostname": "ARTIMATE", "ip": "10.0.0.1", "os": "Ubuntu"},
        "processes": [
            {
                "name": "artimate-main-api",
                "hostname": "artimate-main-api",
                "entity_type": "Application",
                "container_name": "artimate-main-api",
                "image": "artimate-main-api:dev",
            },
            {
                "name": "backend-agent-db",
                "hostname": "backend-agent-db",
                "entity_type": "Database",
                "container_name": "backend-agent-db",
                "image": "postgres:latest",
            },
            {
                "name": "llm_kafka",
                "hostname": "llm_kafka",
                "entity_type": "Queue",
                "image": "confluentinc/cp-kafka:7.5.0",
            },
        ],
        "connections": [
            {
                "source_hostname": "artimate-main-api",
                "target_hostname": "backend-agent-db",
                "relation_type": "depends_on",
            },
            {
                "source_hostname": "artimate-main-api",
                "target_hostname": "ARTIMATE",
                "relation_type": "hosted_on",
            },
        ],
    }
    entities = agent_payload_to_entities(payload)
    app = next(e for e in entities if e.match_key == "artimate-main-api")
    rels = {(r.get("type"), r.get("target_hostname")) for r in app.raw.get("relations", [])}
    assert ("hosted_on", "ARTIMATE") in rels
    assert ("depends_on", "backend-agent-db") in rels


def test_host_connector_reads_snapshot():
    from types import SimpleNamespace

    connector = SimpleNamespace(
        connector_type="host",
        config={"snapshot_path": str(FIXTURE), "mode": "snapshot"},
        credentials=None,
        timeout_seconds=10,
        schema_version="1",
    )
    result = HostConnector(connector, "pay-srv-01").discover()
    assert result.ok, result.error
    assert len(result.entities) >= 2
    assert any(e.match_key == "app-01" for e in result.entities)
