"""Kubernetes workload and service collection."""

from __future__ import annotations

import json

from src.services.autodiscover.discovery.classify import classify_image
from src.services.autodiscover.discovery.commands import run_cmd


def kubernetes_workloads() -> tuple[list[dict] | None, str | None]:
    out, err = run_cmd(["kubectl", "get", "pods", "-A", "-o", "json"])
    if out is None:
        return None, err
    try:
        data = json.loads(out)
    except json.JSONDecodeError as exc:
        return None, f"invalid kubectl json: {exc}"
    items: list[dict] = []
    for pod in data.get("items") or []:
        if not isinstance(pod, dict):
            continue
        meta = pod.get("metadata") or {}
        status = pod.get("status") or {}
        phase = str(status.get("phase") or "")
        if phase and phase not in ("Running", "Pending"):
            continue
        pod_name = str(meta.get("name") or "").strip()
        if not pod_name:
            continue
        namespace = str(meta.get("namespace") or "default")
        pod_ip = status.get("podIP")
        hostname = pod_name
        labels = {str(k): str(v) for k, v in (meta.get("labels") or {}).items()}
        for container in (pod.get("spec") or {}).get("containers") or []:
            if not isinstance(container, dict):
                continue
            image = str(container.get("image") or "")
            cname = str(container.get("name") or pod_name)
            entity_type = classify_image(image)
            env_lines: list[str] = []
            for env_item in container.get("env") or []:
                if isinstance(env_item, dict):
                    ename = env_item.get("name")
                    evalue = env_item.get("value")
                    if ename and evalue is not None:
                        env_lines.append(f"{ename}={evalue}")
            for env_from in container.get("envFrom") or []:
                if isinstance(env_from, dict) and env_from.get("configMapRef"):
                    env_lines.append(f"CONFIG_MAP={env_from['configMapRef'].get('name', '')}")
            items.append(
                {
                    "name": cname,
                    "service_name": pod_name,
                    "hostname": hostname,
                    "match_hostname": hostname,
                    "k8s_namespace": namespace,
                    "k8s_pod": pod_name,
                    "k8s_container": cname,
                    "image": image,
                    "entity_type": entity_type,
                    "ip": pod_ip,
                    "runtime": "kubernetes",
                    "env": env_lines,
                    "labels": labels,
                }
            )
    return items, None


def kubernetes_services() -> tuple[dict[str, str], list[dict]]:
    out, err = run_cmd(["kubectl", "get", "svc", "-A", "-o", "json"])
    if out is None:
        return {}, []
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return {}, []
    index: dict[str, str] = {}
    services: list[dict] = []
    for svc in data.get("items") or []:
        if not isinstance(svc, dict):
            continue
        meta = svc.get("metadata") or {}
        spec = svc.get("spec") or {}
        name = str(meta.get("name") or "").strip()
        namespace = str(meta.get("namespace") or "default")
        if not name:
            continue
        hostname = f"{namespace}/{name}"
        cluster_ip = str(spec.get("clusterIP") or "")
        entity_type = "Network Element"
        lowered = name.lower()
        if any(x in lowered for x in ("postgres", "mysql", "mongo", "redis", "db")):
            entity_type = "Database"
        elif any(x in lowered for x in ("kafka", "rabbit", "queue", "zookeeper")):
            entity_type = "Queue"
        services.append(
            {
                "name": name,
                "hostname": hostname,
                "match_hostname": hostname,
                "service_name": name,
                "entity_type": entity_type,
                "ip": cluster_ip if cluster_ip not in ("", "None") else None,
                "runtime": "kubernetes",
                "k8s_namespace": namespace,
                "k8s_service": name,
            }
        )
        for alias in (
            name.lower(),
            f"{name}.{namespace}".lower(),
            f"{name}.{namespace}.svc".lower(),
            f"{name}.{namespace}.svc.cluster.local".lower(),
        ):
            index[alias] = hostname
    return index, services
