from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any

from src.models import SyncConnector
from src.services.autodiscover.credentials import resolve_credentials


def _script_path() -> Path:
    scripts = Path(__file__).resolve().parents[3] / "scripts"
    py_script = scripts / "host_discover.py"
    if py_script.is_file():
        return py_script
    return scripts / "host_discover.sh"


def _ssh_target(connector: SyncConnector, server_hostname: str | None) -> tuple[str, int]:
    config = connector.config or {}
    host = str(config.get("ssh_host") or server_hostname or "").strip()
    if not host:
        raise ValueError("Укажите IP/hostname в поле «Адрес SSH» или в external ID Server CI (hostname/ip)")
    port = int(config.get("ssh_port") or 22)
    return host, port


def _ssh_username(connector: SyncConnector) -> str:
    creds = resolve_credentials(connector)
    config = connector.config or {}
    return str(creds.get("username") or config.get("ssh_user") or "root")


def _resolve_pkey(creds: dict[str, Any], config: dict[str, Any]):
    import paramiko

    key_body = creds.get("private_key")
    if key_body:
        for loader in (
            paramiko.RSAKey.from_private_key,
            paramiko.ECDSAKey.from_private_key,
            paramiko.Ed25519Key.from_private_key,
        ):
            try:
                return loader(io.StringIO(str(key_body)))
            except Exception:  # noqa: BLE001
                continue
        raise ValueError("Invalid SSH private key text")
    key_path = creds.get("private_key_path") or config.get("ssh_key_path")
    if not key_path:
        raise ValueError("SSH key auth: укажите путь к ключу")
    path = Path(str(key_path)).expanduser()
    if not path.is_file():
        raise ValueError(f"SSH key file not found: {path}")
    for loader in (
        paramiko.RSAKey.from_private_key_file,
        paramiko.ECDSAKey.from_private_key_file,
        paramiko.Ed25519Key.from_private_key_file,
    ):
        try:
            return loader(str(path))
        except Exception:  # noqa: BLE001
            continue
    raise ValueError(f"Cannot read SSH private key: {path}")


def discover_via_ssh(connector: SyncConnector, server_hostname: str | None) -> dict[str, Any]:
    """Run host_discover.sh on remote host via Paramiko (password or key)."""
    try:
        import paramiko
    except ImportError as exc:
        raise ValueError("SSH discovery requires paramiko. Install: pip install paramiko") from exc

    host, port = _ssh_target(connector, server_hostname)
    username = _ssh_username(connector)
    creds = resolve_credentials(connector)
    config = connector.config or {}
    script = _script_path()
    if not script.is_file():
        raise ValueError(f"Discovery script not found: {script}")
    script_body = script.read_text(encoding="utf-8")
    remote_cmd = "python3 -" if script.suffix == ".py" else "bash -s"

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    connect_kwargs: dict[str, Any] = {
        "hostname": host,
        "port": port,
        "username": username,
        "timeout": connector.timeout_seconds,
        "allow_agent": True,
        "look_for_keys": False,
    }

    auth_type = str(creds.get("auth_type") or "none").lower()
    if auth_type == "basic" and creds.get("password"):
        connect_kwargs["password"] = creds["password"]
    elif auth_type == "ssh_key":
        connect_kwargs["pkey"] = _resolve_pkey(creds, config)
    elif auth_type == "none":
        connect_kwargs["look_for_keys"] = True

    try:
        client.connect(**connect_kwargs)
        _, stdout, stderr = client.exec_command(remote_cmd, timeout=connector.timeout_seconds)
        assert stdout.channel is not None
        stdout.channel.send(script_body.encode("utf-8"))
        stdout.channel.shutdown_write()
        out = stdout.read().decode("utf-8", errors="replace").strip()
        err = stderr.read().decode("utf-8", errors="replace").strip()
        exit_code = stdout.channel.recv_exit_status()
    except (TimeoutError, paramiko.SSHException, OSError) as exc:
        raise ValueError(f"SSH failed ({host}:{port}): {exc}") from exc
    finally:
        client.close()

    if exit_code != 0:
        raise ValueError(err or out or f"SSH discovery script failed (exit {exit_code})")
    try:
        payload = json.loads(out)
    except json.JSONDecodeError as exc:
        raise ValueError(f"SSH discovery returned invalid JSON: {out[:200]}") from exc
    if not isinstance(payload, dict):
        raise ValueError("SSH discovery returned invalid payload")
    return payload
