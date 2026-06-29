"""Docker container collection."""

from __future__ import annotations

from src.services.autodiscover.discovery.classify import classify_image, parse_ports
from src.services.autodiscover.discovery.commands import run_docker


def docker_containers() -> tuple[list[dict] | None, str | None]:
    fmt = "{{.Names}}\t{{.Image}}\t{{.Ports}}"
    out, err = run_docker(["ps", "--format", fmt])
    if out is None:
        return None, err
    items: list[dict] = []
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", 2)
        if len(parts) < 2:
            continue
        name, image = parts[0].strip(), parts[1].strip()
        ports_raw = parts[2].strip() if len(parts) > 2 else ""
        entity_type = classify_image(image)
        items.append(
            {
                "name": name,
                "service_name": name,
                "container_name": name,
                "image": image,
                "entity_type": entity_type,
                "hostname": name,
                "match_hostname": name,
                "ports": parse_ports(ports_raw),
                "listen": ports_raw,
            }
        )
    return items, None
