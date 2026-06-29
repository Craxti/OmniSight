"""Unit tests for SSH host discovery (mocked Paramiko)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from src.models import SyncConnector
from src.services.autodiscover.ssh_collect import _ssh_target, _ssh_username, discover_via_ssh


def test_ssh_target_prefers_connector_config():
    connector = SyncConnector(
        name="host-1",
        connector_type="host",
        config={"ssh_host": "10.0.0.5", "ssh_port": 2222},
    )
    host, port = _ssh_target(connector, "fallback.local")
    assert host == "10.0.0.5"
    assert port == 2222


def test_ssh_target_falls_back_to_server_hostname():
    connector = SyncConnector(name="host-1", connector_type="host", config={})
    host, port = _ssh_target(connector, "pay-srv-01")
    assert host == "pay-srv-01"
    assert port == 22


def test_ssh_target_requires_host():
    connector = SyncConnector(name="host-1", connector_type="host", config={})
    with pytest.raises(ValueError, match="SSH"):
        _ssh_target(connector, None)


def test_ssh_username_prefers_config_ssh_user_when_auth_none():
    connector = SyncConnector(
        name="host-1",
        connector_type="host",
        config={"ssh_user": "deploy"},
        credentials={"username": "ops"},
    )
    assert _ssh_username(connector) == "deploy"


def test_ssh_username_from_basic_credentials():
    connector = SyncConnector(
        name="host-1",
        connector_type="host",
        config={},
        credentials={"auth_type": "basic", "username": "ops", "password": "secret"},
    )
    assert _ssh_username(connector) == "ops"


@patch("src.services.autodiscover.ssh_collect._script_path")
@patch("paramiko.SSHClient")
def test_discover_via_ssh_returns_json_payload(mock_ssh_client_cls, mock_script_path, tmp_path):
    script = tmp_path / "host_discover.py"
    script.write_text("print('{}')", encoding="utf-8")
    mock_script_path.return_value = script

    connector = SyncConnector(
        name="host-1",
        connector_type="host",
        config={"ssh_host": "10.0.0.9"},
        credentials={"auth_type": "basic", "password": "secret"},
        timeout_seconds=15,
    )

    payload = {"hostname": "srv-01", "ip": "10.0.0.9", "services": []}
    stdout = MagicMock()
    stdout.read.return_value = json.dumps(payload).encode("utf-8")
    stderr = MagicMock()
    stderr.read.return_value = b""
    channel = MagicMock()
    channel.recv_exit_status.return_value = 0
    stdout.channel = channel

    client = MagicMock()
    client.exec_command.return_value = (None, stdout, stderr)
    mock_ssh_client_cls.return_value = client

    result = discover_via_ssh(connector, None)
    assert result == payload
    client.connect.assert_called_once()
    client.close.assert_called_once()


@patch("src.services.autodiscover.ssh_collect._script_path")
@patch("paramiko.SSHClient")
def test_discover_via_ssh_raises_on_nonzero_exit(mock_ssh_client_cls, mock_script_path, tmp_path):
    script = tmp_path / "host_discover.sh"
    script.write_text("#!/bin/bash", encoding="utf-8")
    mock_script_path.return_value = script

    connector = SyncConnector(
        name="host-1",
        connector_type="host",
        config={"ssh_host": "10.0.0.9"},
        credentials={"auth_type": "none"},
        timeout_seconds=10,
    )

    stdout = MagicMock()
    stdout.read.return_value = b""
    stderr = MagicMock()
    stderr.read.return_value = b"permission denied"
    channel = MagicMock()
    channel.recv_exit_status.return_value = 1
    stdout.channel = channel

    client = MagicMock()
    client.exec_command.return_value = (None, stdout, stderr)
    mock_ssh_client_cls.return_value = client

    with pytest.raises(ValueError, match="permission denied"):
        discover_via_ssh(connector, "srv.local")
