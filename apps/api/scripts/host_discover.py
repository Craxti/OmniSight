#!/usr/bin/env python3
"""OmniSight host discovery: Docker containers → JSON for host_agent."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow `python3 apps/api/scripts/host_discover.py` without installing the package.
_API_ROOT = Path(__file__).resolve().parents[1]
if str(_API_ROOT) not in sys.path:
    sys.path.insert(0, str(_API_ROOT))

from src.services.autodiscover.discovery import inference as _inference
from src.services.autodiscover.discovery.collectors import (
    collect_all_processes,
    host_info,
)
from src.services.autodiscover.discovery.inference import (
    discover_compose_file_paths,
    infer_connections,
)


def infer_compose_file_connections(*args, **kwargs):
    if "discover_paths" not in kwargs:
        kwargs["discover_paths"] = discover_compose_file_paths
    return _inference.infer_compose_file_connections(*args, **kwargs)


def main() -> None:
    host = host_info()
    processes, warnings, runtimes, k8s_service_index = collect_all_processes()
    payload: dict = {
        "host": host,
        "processes": processes,
        "connections": [],
        "runtime": runtimes,
    }
    if warnings:
        payload["warnings"] = warnings
    if not processes:
        payload["error"] = "no workloads found (docker, kubernetes, systemd, or native listeners)"
        print(json.dumps(payload, ensure_ascii=False))
        return
    payload["connections"] = infer_connections(processes, host["hostname"], k8s_service_index)
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
