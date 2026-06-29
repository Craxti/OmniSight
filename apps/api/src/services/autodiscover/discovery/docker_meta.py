"""Docker container metadata and network inspection."""

from __future__ import annotations

import json
import re

from src.services.autodiscover.discovery.commands import run_docker
from src.services.autodiscover.discovery.constants import SKIP_DOCKER_NETWORKS
from src.services.autodiscover.discovery.models import ContainerMeta


def collect_container_metadata(container_names: list[str]) -> dict[str, ContainerMeta]:
    if not container_names:
        return {}
    fmt = "{{.Name}}\t{{json .Config.Env}}\t{{json .Config.Labels}}"
    out, _ = run_docker(["inspect", "--format", fmt, *container_names])
    if not out:
        return {}
    metadata: dict[str, ContainerMeta] = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        name_part, _, rest = line.partition("\t")
        env_part, _, labels_part = rest.partition("\t")
        name = name_part.lstrip("/").strip()
        try:
            env_list = json.loads(env_part) if env_part else []
            labels = json.loads(labels_part) if labels_part else {}
        except json.JSONDecodeError:
            continue
        if not isinstance(env_list, list):
            env_list = []
        if not isinstance(labels, dict):
            labels = {}
        metadata[name] = ContainerMeta(
            env=[str(item) for item in env_list],
            labels={str(k): str(v) for k, v in labels.items()},
        )
    return metadata


def _normalize_ip(ip: str) -> str:
    return ip.strip().strip("[]")


def collect_container_network_details(container_names: list[str]) -> dict[str, dict[str, object]]:
    """Container -> {ip, aliases, networks}."""
    if not container_names:
        return {}
    fmt = "{{.Name}}\t{{json .NetworkSettings.Networks}}"
    out, _ = run_docker(["inspect", "--format", fmt, *container_names])
    if not out:
        return {}
    details: dict[str, dict[str, object]] = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        name_part, _, networks_part = line.partition("\t")
        name = name_part.lstrip("/").strip()
        try:
            networks = json.loads(networks_part) if networks_part else {}
        except json.JSONDecodeError:
            continue
        if not isinstance(networks, dict):
            continue
        aliases: set[str] = set()
        ip = ""
        net_names: set[str] = set()
        for net_name, net_info in networks.items():
            if not isinstance(net_info, dict):
                continue
            net_names.add(str(net_name))
            if str(net_name) in SKIP_DOCKER_NETWORKS:
                continue
            if not ip and net_info.get("IPAddress"):
                ip = str(net_info["IPAddress"])
            for alias in net_info.get("Aliases") or []:
                aliases.add(str(alias))
        details[name] = {"ip": ip, "aliases": sorted(aliases), "networks": sorted(net_names)}
    return details


def enrich_docker_processes(processes: list[dict], details: dict[str, dict[str, object]]) -> None:
    for proc in processes:
        if str(proc.get("runtime") or "") != "docker":
            continue
        hostname = str(proc.get("hostname") or "")
        info = details.get(hostname) or {}
        if info.get("ip"):
            proc["ip"] = info["ip"]
        if info.get("aliases"):
            proc["network_aliases"] = info["aliases"]
        if info.get("networks"):
            proc["docker_networks"] = info["networks"]


def docker_container_networks(container_names: list[str]) -> dict[str, set[str]]:
    if not container_names:
        return {}
    fmt = "{{.Name}}\t{{json .NetworkSettings.Networks}}"
    out, _ = run_docker(["inspect", "--format", fmt, *container_names])
    if not out:
        return {}
    result: dict[str, set[str]] = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        name_part, _, networks_part = line.partition("\t")
        name = name_part.lstrip("/").strip()
        try:
            networks = json.loads(networks_part) if networks_part else {}
        except json.JSONDecodeError:
            continue
        if isinstance(networks, dict):
            result[name] = {str(net) for net in networks.keys() if str(net) not in SKIP_DOCKER_NETWORKS}
    return result


def _parse_ss_listener_line(line: str) -> tuple[str, int, str] | None:
    """Parse ss -tlnpH line → (process_name, port, listen_addr)."""
    match = re.search(r"([\d.]+|\[[\da-f:]+\]|\\*):(\d+)\s", line)
    if not match:
        return None
    port = int(match.group(2))
    if port < 1:
        return None
    proc = "unknown"
    proc_match = re.search(r'users:\(\("([^"]+)"', line)
    if proc_match:
        proc = proc_match.group(1)
    listen = match.group(0).strip()
    return proc, port, listen
