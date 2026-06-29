"""systemd service collection."""

from __future__ import annotations

from src.services.autodiscover.discovery.commands import run_cmd


def systemd_services() -> tuple[list[dict], str | None]:
    out, err = run_cmd(["systemctl", "list-units", "--type=service", "--state=running", "--no-pager", "--no-legend"])
    if out is None:
        return [], err
    items: list[dict] = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        unit = line.split()[0]
        if not unit.endswith(".service"):
            continue
        name = unit[: -len(".service")]
        lowered = name.lower()
        entity_type = "Application"
        if any(x in lowered for x in ("postgres", "mysql", "mongo", "redis", "mariadb")):
            entity_type = "Database"
        elif any(x in lowered for x in ("kafka", "rabbitmq", "zookeeper")):
            entity_type = "Queue"
        elif any(x in lowered for x in ("nginx", "haproxy", "traefik")):
            entity_type = "Network Element"
        items.append(
            {
                "name": name,
                "hostname": name,
                "match_hostname": name,
                "service_name": name,
                "entity_type": entity_type,
                "runtime": "systemd",
            }
        )
    return items, None
