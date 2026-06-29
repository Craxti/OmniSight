"""Unit tests for systemd service collector."""

from __future__ import annotations

from unittest.mock import patch

from src.services.autodiscover.discovery.collectors.systemd_collector import systemd_services


@patch("src.services.autodiscover.discovery.collectors.systemd_collector.run_cmd")
def test_systemd_services_parses_running_units(mock_run_cmd):
    mock_run_cmd.return_value = (
        "postgres.service loaded active running PostgreSQL\nnginx.service loaded active running Nginx\n",
        None,
    )

    items, err = systemd_services()

    assert err is None
    assert len(items) == 2
    assert items[0]["entity_type"] == "Database"
    assert items[1]["entity_type"] == "Network Element"


@patch("src.services.autodiscover.discovery.collectors.systemd_collector.run_cmd")
def test_systemd_services_returns_error_when_systemctl_missing(mock_run_cmd):
    mock_run_cmd.return_value = (None, "systemctl: command not found")

    items, err = systemd_services()

    assert items == []
    assert err == "systemctl: command not found"
