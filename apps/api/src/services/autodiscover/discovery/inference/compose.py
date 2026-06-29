"""Docker Compose label and file based connection inference."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path

from src.services.autodiscover.discovery.constants import COMPOSE_FILENAMES, COMPOSE_SEARCH_ROOTS
from src.services.autodiscover.discovery.inference.core import make_connection, relation_type_for_target
from src.services.autodiscover.discovery.models import ContainerMeta


def compose_project(labels: dict[str, str]) -> str | None:
    return labels.get("com.docker.compose.project") or labels.get("com.docker.compose.project.working_dir")


def compose_service(labels: dict[str, str]) -> str | None:
    return labels.get("com.docker.compose.service")


def parse_compose_depends_on(labels: dict[str, str]) -> list[str]:
    raw = labels.get("com.docker.compose.depends_on")
    if not raw:
        return []
    try:
        parsed = json.loads(raw) if raw.startswith("{") or raw.startswith("[") else raw
    except json.JSONDecodeError:
        return []
    if isinstance(parsed, dict):
        return [str(k) for k in parsed.keys()]
    if isinstance(parsed, list):
        return [str(item) for item in parsed]
    if isinstance(parsed, str):
        return [part.strip() for part in parsed.split(",") if part.strip()]
    return []


def build_compose_service_index(metadata: dict[str, ContainerMeta]) -> dict[str, dict[str, str]]:
    """project -> compose service name -> container hostname."""
    index: dict[str, dict[str, str]] = defaultdict(dict)
    for container, meta in metadata.items():
        project = compose_project(meta.labels)
        service = compose_service(meta.labels)
        if project and service:
            index[project][service] = container
            index[project][service.replace("_", "-")] = container
    return index


def discover_compose_file_paths(metadata: dict[str, ContainerMeta]) -> list[Path]:
    paths: list[Path] = []
    seen: set[str] = set()
    for meta in metadata.values():
        for key in ("com.docker.compose.project.working_dir", "com.docker.compose.project.config_files"):
            raw = meta.labels.get(key)
            if not raw:
                continue
            for part in re.split(r"[,;]", raw):
                part = part.strip()
                if not part:
                    continue
                path = Path(part)
                if path.is_file() and str(path) not in seen:
                    seen.add(str(path))
                    paths.append(path)
                elif path.is_dir():
                    for name in COMPOSE_FILENAMES:
                        candidate = path / name
                        if candidate.is_file() and str(candidate) not in seen:
                            seen.add(str(candidate))
                            paths.append(candidate)
    for root in COMPOSE_SEARCH_ROOTS:
        base = Path(root)
        if not base.is_dir():
            continue
        try:
            for name in COMPOSE_FILENAMES:
                for candidate in base.glob(f"**/{name}"):
                    if candidate.is_file() and str(candidate) not in seen:
                        seen.add(str(candidate))
                        paths.append(candidate)
        except OSError:
            continue
    return paths[:20]


def parse_compose_file(path: Path) -> dict[str, list[str]]:
    """Parse docker-compose service depends_on without PyYAML."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    services: dict[str, list[str]] = {}
    current: str | None = None
    in_depends = False
    for line in text.splitlines():
        if re.match(r"^services:\s*$", line):
            current = None
            in_depends = False
            continue
        service_match = re.match(r"^  ([A-Za-z0-9][\w-]*):\s*$", line)
        if service_match:
            current = service_match.group(1)
            services.setdefault(current, [])
            in_depends = False
            continue
        if current and re.match(r"^    depends_on:\s*$", line):
            in_depends = True
            continue
        if in_depends and current:
            dep_match = re.match(r"^      - ([\w-]+)\s*$", line)
            if dep_match:
                services[current].append(dep_match.group(1))
                continue
            dep_key = re.match(r"^      ([\w-]+):\s*$", line)
            if dep_key:
                services[current].append(dep_key.group(1))
                continue
            if re.match(r"^    \w", line):
                in_depends = False
    return {name: deps for name, deps in services.items() if deps}


def infer_compose_file_connections(
    processes: list[dict],
    metadata: dict[str, ContainerMeta],
    *,
    entity_types: dict[str, str],
    compose_index: dict[str, dict[str, str]],
    discover_paths: Callable[[dict[str, ContainerMeta]], list[Path]] | None = None,
) -> list[dict]:
    discover = discover_paths or discover_compose_file_paths
    connections: list[dict] = []
    compose_files = discover(metadata)
    if not compose_files:
        return connections
    service_to_host: dict[str, str] = {}
    for project_services in compose_index.values():
        service_to_host.update(project_services)
    for proc in processes:
        cname = str(proc.get("container_name") or proc.get("hostname") or "")
        service = compose_service((metadata.get(cname) or ContainerMeta()).labels)
        if service:
            service_to_host.setdefault(service, cname)
            service_to_host.setdefault(service.replace("_", "-"), cname)
    for path in compose_files:
        for service, deps in parse_compose_file(path).items():
            source = service_to_host.get(service) or service_to_host.get(service.replace("-", "_"))
            if not source:
                continue
            for dep in deps:
                target = service_to_host.get(dep) or service_to_host.get(dep.replace("-", "_")) or dep
                if not target or target == source:
                    continue
                target_type = entity_types.get(target, "")
                if target_type in ("Database", "Queue", "Technical Component", "Application", ""):
                    connections.append(
                        make_connection(
                            source_hostname=source,
                            target_hostname=target,
                            relation_type=relation_type_for_target(target_type or "Database", target),
                            source="compose_file",
                        )
                    )
    return connections


def infer_compose_connections(
    metadata: dict[str, ContainerMeta],
    *,
    entity_types: dict[str, str],
    compose_index: dict[str, dict[str, str]],
) -> list[dict]:
    connections: list[dict] = []
    for container, meta in metadata.items():
        project = compose_project(meta.labels)
        if not project:
            continue
        services = compose_index.get(project, {})
        for dep_service in parse_compose_depends_on(meta.labels):
            target = services.get(dep_service) or services.get(dep_service.replace("-", "_"))
            if not target or target == container:
                continue
            target_type = entity_types.get(target, "")
            if target_type in ("Database", "Queue", "Technical Component", "Application"):
                connections.append(
                    make_connection(
                        source_hostname=container,
                        target_hostname=target,
                        relation_type=relation_type_for_target(target_type, target),
                        source="compose",
                    )
                )
    return connections
