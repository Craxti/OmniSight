"""Host/name indexes for resolving connection endpoints."""

from __future__ import annotations

from src.services.autodiscover.discovery.constants import SKIP_HOSTS
from src.services.autodiscover.discovery.docker_meta import _normalize_ip


def build_ip_index(processes: list[dict], network_details: dict[str, dict[str, object]]) -> dict[str, str]:
    index: dict[str, str] = {}
    for proc in processes:
        hostname = str(proc.get("hostname") or "").strip()
        if not hostname:
            continue
        for key in ("ip",):
            ip = proc.get(key)
            if ip:
                index[_normalize_ip(str(ip))] = hostname
        info = network_details.get(hostname) or {}
        ip = info.get("ip")
        if ip:
            index[_normalize_ip(str(ip))] = hostname
    return index


def build_name_index(processes: list[dict], k8s_service_index: dict[str, str] | None = None) -> dict[str, str]:
    index: dict[str, str] = {}
    for proc in processes:
        hostname = str(proc.get("hostname") or "").strip()
        if not hostname:
            continue
        index[hostname.lower()] = hostname
        for alias in (proc.get("container_name"), proc.get("name"), proc.get("service_name")):
            if alias:
                index[str(alias).lower()] = hostname
        for alias in proc.get("network_aliases") or []:
            index[str(alias).lower()] = hostname
        ns = proc.get("k8s_namespace")
        pod = proc.get("k8s_pod")
        if ns and pod:
            index[f"{pod}.{ns}".lower()] = hostname
            index[f"{pod}.{ns}.svc.cluster.local".lower()] = hostname
    if k8s_service_index:
        index.update(k8s_service_index)
    return index


def known_name_tokens(name_index: dict[str, str]) -> list[str]:
    """Longest first so 'artimate-clustering-db' wins over 'artimate'."""
    return sorted(name_index.keys(), key=len, reverse=True)


def resolve_target_host(host: str, name_index: dict[str, str], ip_index: dict[str, str] | None = None) -> str | None:
    normalized = host.lower().strip().split(":")[0]
    if normalized in SKIP_HOSTS:
        return None
    if normalized in name_index:
        return name_index[normalized]
    if ip_index and normalized in ip_index:
        return ip_index[normalized]
    short = normalized.split(".")[0]
    if short in name_index:
        return name_index[short]
    for key, canonical in name_index.items():
        if key.split(".")[0] == short:
            return canonical
    return None


def build_proc_to_host_map(
    processes: list[dict],
    ip_index: dict[str, str],
    network_details: dict[str, dict[str, object]],
) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for proc in processes:
        hostname = str(proc.get("hostname") or "")
        if not hostname:
            continue
        for key in (proc.get("name"), proc.get("service_name"), proc.get("container_name")):
            if key:
                mapping[str(key).lower()] = hostname
        ip = proc.get("ip")
        if ip:
            mapping[_normalize_ip(str(ip))] = hostname
        info = network_details.get(hostname) or {}
        if info.get("ip"):
            mapping[_normalize_ip(str(info["ip"]))] = hostname
    mapping.update(ip_index)
    return mapping
