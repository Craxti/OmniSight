"""Workload classification helpers."""

from __future__ import annotations

import re

from src.services.autodiscover.port_constants import DB_PORTS as NATIVE_DB_PORTS
from src.services.autodiscover.port_constants import QUEUE_PORTS as NATIVE_QUEUE_PORTS


def classify_image(image: str) -> str:
    img = image.lower()
    if any(x in img for x in ("postgres", "mongo", "mysql", "mariadb", "clickhouse")):
        return "Database"
    if any(x in img for x in ("redis", "memcached")):
        return "Database"
    if any(x in img for x in ("kafka", "zookeeper", "rabbitmq", "redpanda")):
        return "Queue"
    if any(x in img for x in ("nginx", "haproxy", "traefik")):
        return "Network Element"
    if any(x in img for x in ("eureka", "consul", "etcd")):
        return "Technical Component"
    if "hazelcast" in img:
        return "Technical Component"
    if any(x in img for x in ("prometheus", "grafana", "alertmanager")):
        return "Network Element"
    return "Application"


def parse_ports(port_str: str) -> list[int]:
    ports: list[int] = []
    for chunk in (port_str or "").split(","):
        match = re.search(r":(\d+)->", chunk)
        if match:
            ports.append(int(match.group(1)))
            continue
        match = re.search(r":(\d+)(?:/|$)", chunk)
        if match:
            ports.append(int(match.group(1)))
    return ports


def classify_native_process(proc_name: str, port: int) -> str:
    if port in NATIVE_DB_PORTS:
        return "Database"
    if port in NATIVE_QUEUE_PORTS:
        return "Queue"
    lowered = proc_name.lower()
    if any(x in lowered for x in ("postgres", "mysql", "mongo", "redis", "mariadb")):
        return "Database"
    if any(x in lowered for x in ("kafka", "rabbitmq", "zookeeper")):
        return "Queue"
    if any(x in lowered for x in ("nginx", "haproxy", "traefik")):
        return "Network Element"
    return "Application"
