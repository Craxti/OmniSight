"""Resolve connector credentials from DB + environment variables."""

from __future__ import annotations

import base64
import os
from typing import Any

from src.models import SyncConnector

SECRET_ENV_SUFFIXES = ("_env", "_env_var")


def _resolve_env(value: str | None) -> str | None:
    if not value:
        return None
    return os.environ.get(value) or None


def resolve_secret(value: str | None, *, env_key: str | None = None) -> str | None:
    """Return inline secret or value from env var name."""
    if env_key:
        from_env = _resolve_env(env_key)
        if from_env:
            return from_env
    return value


def resolve_credentials(connector: SyncConnector) -> dict[str, Any]:
    """Merged auth settings for connector implementations (never log return value)."""
    creds = dict(connector.credentials or {})
    config_auth = (connector.config or {}).get("auth") or {}
    merged = {**config_auth, **creds}

    auth_type = str(merged.get("auth_type") or merged.get("type") or "none").lower()
    out: dict[str, Any] = {"auth_type": auth_type}

    if auth_type == "basic":
        username = merged.get("username") or resolve_secret(None, env_key=merged.get("username_env"))
        password = merged.get("password") or resolve_secret(None, env_key=merged.get("password_env"))
        if username:
            out["username"] = username
        if password:
            out["password"] = password
    elif auth_type == "bearer":
        token = merged.get("token") or resolve_secret(None, env_key=merged.get("token_env"))
        if token:
            out["token"] = token
    elif auth_type == "api_key":
        header = merged.get("api_key_header") or "X-API-Key"
        api_key = merged.get("api_key") or resolve_secret(None, env_key=merged.get("api_key_env"))
        out["api_key_header"] = header
        if api_key:
            out["api_key"] = api_key
    elif auth_type == "ssh_key":
        username = merged.get("username") or resolve_secret(None, env_key=merged.get("username_env"))
        if username:
            out["username"] = username
        if merged.get("private_key"):
            out["private_key"] = merged["private_key"]
        key_path = merged.get("private_key_path") or resolve_secret(None, env_key=merged.get("private_key_path_env"))
        if key_path:
            out["private_key_path"] = key_path

    return out


def auth_headers(connector: SyncConnector) -> dict[str, str]:
    creds = resolve_credentials(connector)
    auth_type = creds.get("auth_type", "none")
    headers: dict[str, str] = {}

    if auth_type == "basic" and creds.get("username") and creds.get("password"):
        token = base64.b64encode(f"{creds['username']}:{creds['password']}".encode()).decode()
        headers["Authorization"] = f"Basic {token}"
    elif auth_type == "bearer" and creds.get("token"):
        headers["Authorization"] = f"Bearer {creds['token']}"
    elif auth_type == "api_key" and creds.get("api_key"):
        headers[str(creds.get("api_key_header", "X-API-Key"))] = str(creds["api_key"])

    extra = (connector.config or {}).get("headers") or {}
    for key, value in extra.items():
        if str(key).lower() not in {h.lower() for h in headers}:
            headers[str(key)] = str(value)
    return headers


def resolve_database_url(connector: SyncConnector) -> str | None:
    config = connector.config or {}
    creds = connector.credentials or {}
    inline = config.get("database_url") or creds.get("database_url")
    if inline:
        return str(inline)
    env_key = config.get("database_url_env") or creds.get("database_url_env")
    if env_key:
        return _resolve_env(str(env_key))
    return None


def credentials_configured(connector: SyncConnector) -> bool:
    creds = connector.credentials or {}
    config_auth = (connector.config or {}).get("auth") or {}
    merged = {**config_auth, **creds}
    auth_type = str(merged.get("auth_type") or merged.get("type") or "none").lower()
    if auth_type == "none":
        return bool(merged.get("database_url") or merged.get("database_url_env") or config_auth)
    keys = (
        "password",
        "password_env",
        "private_key",
        "private_key_path",
        "private_key_path_env",
        "token",
        "token_env",
        "api_key",
        "api_key_env",
        "username_env",
        "database_url",
        "database_url_env",
    )
    return any(merged.get(k) for k in keys)
