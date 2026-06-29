"""Workload collection from Docker, Kubernetes, systemd, and native listeners."""

from src.services.autodiscover.discovery.collectors.docker_collector import docker_containers
from src.services.autodiscover.discovery.collectors.host_info import host_info
from src.services.autodiscover.discovery.collectors.kubernetes_collector import (
    kubernetes_services,
    kubernetes_workloads,
)
from src.services.autodiscover.discovery.collectors.native_collector import native_listeners
from src.services.autodiscover.discovery.collectors.orchestrator import collect_all_processes, dedupe_processes
from src.services.autodiscover.discovery.collectors.systemd_collector import systemd_services

__all__ = [
    "collect_all_processes",
    "dedupe_processes",
    "docker_containers",
    "host_info",
    "kubernetes_services",
    "kubernetes_workloads",
    "native_listeners",
    "systemd_services",
]
