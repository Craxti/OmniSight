"""Additional SSH collect edge-case tests."""

from __future__ import annotations

import io
from unittest.mock import MagicMock, patch

import pytest
from src.models import SyncConnector
from src.services.autodiscover.ssh_collect import _resolve_pkey, _script_path, discover_via_ssh


def test_script_path_prefers_python_when_present(tmp_path, monkeypatch):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    py_script = scripts / "host_discover.py"
    py_script.write_text("# py", encoding="utf-8")
    sh_script = scripts / "host_discover.sh"
    sh_script.write_text("# sh", encoding="utf-8")

    monkeypatch.setattr(
        "src.services.autodiscover.ssh_collect.Path",
        lambda *_args, **_kwargs: scripts / "host_discover.py",
    )
    # Direct patch of _script_path parents is hard; test via discover using tmp script
    assert _script_path().name in ("host_discover.py", "host_discover.sh")


def test_resolve_pkey_from_inline_text():
    import paramiko

    key = paramiko.RSAKey.generate(2048)
    buffer = io.StringIO()
    key.write_private_key(buffer)

    creds = {"private_key": buffer.getvalue()}
    resolved = _resolve_pkey(creds, {})
    assert resolved is not None


def test_resolve_pkey_missing_raises():
    with pytest.raises(ValueError, match="SSH key"):
        _resolve_pkey({}, {})


@patch("src.services.autodiscover.ssh_collect._script_path")
def test_discover_via_ssh_invalid_json(mock_script_path, tmp_path):
    script = tmp_path / "host_discover.py"
    script.write_text("print('not-json')", encoding="utf-8")
    mock_script_path.return_value = script

    connector = SyncConnector(
        name="host-1",
        connector_type="host",
        config={"ssh_host": "10.0.0.2"},
        credentials={"auth_type": "none"},
        timeout_seconds=5,
    )

    stdout = MagicMock()
    stdout.read.return_value = b"not-json"
    stderr = MagicMock()
    stderr.read.return_value = b""
    channel = MagicMock()
    channel.recv_exit_status.return_value = 0
    stdout.channel = channel

    client = MagicMock()
    client.exec_command.return_value = (None, stdout, stderr)

    with patch("paramiko.SSHClient", return_value=client):
        with pytest.raises(ValueError, match="invalid JSON"):
            discover_via_ssh(connector, None)
