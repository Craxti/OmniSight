"""Unit tests for native listener collector (mocked ss/netstat)."""

from __future__ import annotations

from unittest.mock import patch

from src.services.autodiscover.discovery.collectors.native_collector import native_listeners


@patch("src.services.autodiscover.discovery.collectors.native_collector.run_cmd")
def test_native_listeners_parses_ss_output(mock_run_cmd):
    mock_run_cmd.return_value = (
        'LISTEN 0 128 0.0.0.0:5432 0.0.0.0:* users:(("postgres",pid=99,fd=3))\n',
        None,
    )

    items, err = native_listeners()

    assert err is None
    assert len(items) == 1
    assert items[0]["ports"] == [5432]
    assert items[0]["entity_type"] == "Database"


@patch("src.services.autodiscover.discovery.collectors.native_collector.run_cmd")
def test_native_listeners_returns_error_when_no_tools(mock_run_cmd):
    mock_run_cmd.side_effect = [
        (None, "ss: not found"),
        (None, "ss: not found"),
        (None, "netstat: not found"),
    ]

    items, err = native_listeners()

    assert items == []
    assert err == "netstat: not found"
