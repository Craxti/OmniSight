"""Host connector snapshot discovery tests."""

from src.core.fixture_paths import fixture_path
from src.models import SyncConnector
from src.services.autodiscover.connectors.host_connector import HostConnector


def test_host_connector_discovers_from_snapshot_file():
    connector = SyncConnector(
        name="snapshot-host",
        connector_type="host",
        config={
            "mode": "snapshot",
            "snapshot_path": str(fixture_path("host_snapshot_pay_srv.json")),
        },
    )

    result = HostConnector(connector, server_hostname="pay-srv-01").discover()

    assert result.ok is True
    assert result.entities
    assert result.schema is not None
    assert result.schema.fields


def test_host_connector_inline_snapshot():
    connector = SyncConnector(
        name="inline-host",
        connector_type="host",
        config={
            "mode": "snapshot",
            "snapshot": {
                "host": {"hostname": "inline-srv", "ip": "10.0.0.50", "os": "Linux"},
                "processes": [],
                "connections": [],
            },
        },
    )

    result = HostConnector(connector).discover()

    assert result.ok is True
    assert len(result.entities) >= 1
