"""Orchestrate all workload collectors."""

from __future__ import annotations

from src.services.autodiscover.discovery.collectors.docker_collector import docker_containers
from src.services.autodiscover.discovery.collectors.kubernetes_collector import (
    kubernetes_services,
    kubernetes_workloads,
)
from src.services.autodiscover.discovery.collectors.native_collector import native_listeners
from src.services.autodiscover.discovery.collectors.systemd_collector import systemd_services
from src.services.autodiscover.discovery.docker_meta import (
    collect_container_network_details,
    enrich_docker_processes,
)


def dedupe_processes(processes: list[dict]) -> list[dict]:
    runtime_rank = {"docker": 4, "kubernetes": 3, "systemd": 2, "native": 1}
    by_key: dict[str, dict] = {}
    for proc in processes:
        hostname = str(proc.get("hostname") or proc.get("name") or "").strip()
        if not hostname:
            continue
        key = hostname.lower()
        runtime = str(proc.get("runtime") or "docker")
        rank = runtime_rank.get(runtime, 0)
        existing = by_key.get(key)
        if existing is None or rank > runtime_rank.get(str(existing.get("runtime") or "docker"), 0):
            by_key[key] = proc
    return list(by_key.values())


def collect_all_processes() -> tuple[list[dict], list[str], dict[str, bool], dict[str, str]]:
    warnings: list[str] = []
    runtimes = {"docker": False, "kubernetes": False, "native": False, "systemd": False}
    processes: list[dict] = []
    k8s_service_index: dict[str, str] = {}

    docker_procs, docker_err = docker_containers()
    if docker_procs:
        runtimes["docker"] = True
        for proc in docker_procs:
            proc.setdefault("runtime", "docker")
        container_names = [str(p["hostname"]) for p in docker_procs if p.get("hostname")]
        network_details = collect_container_network_details(container_names)
        enrich_docker_processes(docker_procs, network_details)
        processes.extend(docker_procs)
    elif docker_err and "not installed" not in (docker_err or "").lower():
        warnings.append(f"docker: {docker_err}")

    k8s_procs, k8s_err = kubernetes_workloads()
    if k8s_procs:
        runtimes["kubernetes"] = True
        processes.extend(k8s_procs)
    elif k8s_err and "command not found" not in (k8s_err or "").lower():
        warnings.append(f"kubernetes: {k8s_err}")

    svc_index, svc_entities = kubernetes_services()
    if svc_entities:
        runtimes["kubernetes"] = True
        k8s_service_index = svc_index
        processes.extend(svc_entities)

    native_procs, native_err = native_listeners()
    if native_procs:
        runtimes["native"] = True
        docker_ports = {port for proc in processes for port in (proc.get("ports") or [])}
        for proc in native_procs:
            ports = proc.get("ports") or []
            if ports and all(p in docker_ports for p in ports):
                continue
            processes.append(proc)
    elif native_err and "command not found" not in (native_err or "").lower():
        warnings.append(f"native: {native_err}")

    systemd_procs, systemd_err = systemd_services()
    if systemd_procs:
        runtimes["systemd"] = True
        known = {str(p.get("hostname", "")).lower() for p in processes}
        for proc in systemd_procs:
            if str(proc.get("hostname", "")).lower() not in known:
                processes.append(proc)
    elif systemd_err and "command not found" not in (systemd_err or "").lower():
        warnings.append(f"systemd: {systemd_err}")

    return dedupe_processes(processes), warnings, runtimes, k8s_service_index
