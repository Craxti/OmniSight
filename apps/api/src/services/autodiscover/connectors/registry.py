from __future__ import annotations

import time
from collections.abc import Callable

from src.models import SyncConnector
from src.services.autodiscover.connectors.base import ConnectorDiscoveryResult, DiscoveryConnector
from src.services.autodiscover.connectors.host_connector import HostConnector
from src.services.autodiscover.connectors.implementations import (
    ApiConnector,
    DbConnector,
    FileConnector,
    StreamConnector,
)

ConnectorFactory = Callable[[SyncConnector, str | None], DiscoveryConnector]

_REGISTRY: dict[str, ConnectorFactory] = {
    "host": lambda c, h: HostConnector(c, h),
    "file": lambda c, _: FileConnector(c),
    "api": lambda c, _: ApiConnector(c),
    "db": lambda c, _: DbConnector(c),
    "stream": lambda c, _: StreamConnector(c),
}

SUPPORTED_CONNECTOR_TYPES = tuple(_REGISTRY.keys())


def build_connector(connector: SyncConnector, server_hostname: str | None = None) -> DiscoveryConnector:
    factory = _REGISTRY.get(connector.connector_type)
    if not factory:
        raise ValueError(f"Unsupported connector type: {connector.connector_type}")
    return factory(connector, server_hostname)


def discover_with_retry(connector: SyncConnector, server_hostname: str | None = None) -> ConnectorDiscoveryResult:
    impl = build_connector(connector, server_hostname)
    last_error: str | None = None
    attempts = 0
    for attempt in range(1, max(connector.max_retries, 1) + 1):
        attempts = attempt
        try:
            result = impl.discover()
            result.attempts = attempt
            if result.ok:
                return result
            last_error = result.error
        except Exception as exc:  # noqa: BLE001 — connector boundary
            last_error = str(exc)
        if attempt < connector.max_retries:
            time.sleep(min(0.25 * attempt, 2.0))
    return ConnectorDiscoveryResult(ok=False, error=last_error or "Discovery failed", attempts=attempts)
