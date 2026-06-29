"""Native listener collection via ss/netstat."""

from __future__ import annotations

from src.services.autodiscover.discovery.classify import classify_native_process
from src.services.autodiscover.discovery.commands import run_cmd
from src.services.autodiscover.discovery.docker_meta import _parse_ss_listener_line


def native_listeners() -> tuple[list[dict], str | None]:
    out, err = run_cmd(["ss", "-tlnpH"])
    if out is None:
        out, err = run_cmd(["ss", "-tlnp"])
    if out is None:
        out, err = run_cmd(["netstat", "-tlnp"])
    if out is None:
        return [], err
    seen_ports: set[int] = set()
    items: list[dict] = []
    for line in out.splitlines():
        parsed = _parse_ss_listener_line(line)
        if not parsed:
            continue
        proc, port, listen = parsed
        if port in seen_ports:
            continue
        seen_ports.add(port)
        hostname = proc if proc != "unknown" else f"listener-{port}"
        entity_type = classify_native_process(proc, port)
        items.append(
            {
                "name": proc,
                "service_name": hostname,
                "hostname": hostname,
                "match_hostname": hostname,
                "entity_type": entity_type,
                "ports": [port],
                "listen": listen,
                "runtime": "native",
                "pid": None,
            }
        )
    return items, None
