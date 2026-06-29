"""TCP socket based connection inference."""

from __future__ import annotations

from src.services.autodiscover.discovery.commands import run_cmd
from src.services.autodiscover.discovery.constants import TCP_LINE_RE, TCP_PROC_RE
from src.services.autodiscover.discovery.docker_meta import _normalize_ip
from src.services.autodiscover.discovery.inference.core import make_connection, relation_type_for_target
from src.services.autodiscover.discovery.inference.indexes import resolve_target_host
from src.services.autodiscover.port_constants import INFRA_PORTS


def _parse_tcp_line(line: str) -> tuple[str, int, str, int, str] | None:
    match = TCP_LINE_RE.search(line)
    if not match:
        return None
    src_ip, src_port, dst_ip, dst_port = match.groups()
    proc_match = TCP_PROC_RE.search(line)
    proc = proc_match.group(1) if proc_match else "unknown"
    return _normalize_ip(src_ip), int(src_port), _normalize_ip(dst_ip), int(dst_port), proc


def infer_tcp_connections(
    *,
    name_index: dict[str, str],
    ip_index: dict[str, str],
    entity_types: dict[str, str],
    proc_to_host: dict[str, str],
) -> list[dict]:
    out, _ = run_cmd(["ss", "-H", "-tn", "state", "established"])
    if out is None:
        out, _ = run_cmd(["ss", "-tn", "state", "established"])
    if not out:
        return []
    infra_ports = INFRA_PORTS
    connections: list[dict] = []
    for line in out.splitlines():
        parsed = _parse_tcp_line(line)
        if not parsed:
            continue
        src_ip, _src_port, dst_ip, dst_port, proc = parsed
        if dst_port not in infra_ports:
            continue
        target = resolve_target_host(dst_ip, name_index, ip_index)
        if not target:
            continue
        target_type = entity_types.get(target, "")
        if target_type not in ("Database", "Queue", "Technical Component", "Network Element"):
            continue
        source = proc_to_host.get(src_ip) or proc_to_host.get(proc.lower()) or proc_to_host.get(proc)
        if not source or source == target:
            continue
        if entity_types.get(source, "Application") not in ("Application", "Container"):
            continue
        connections.append(
            make_connection(
                source_hostname=source,
                target_hostname=target,
                relation_type=relation_type_for_target(target_type, target),
                source="tcp",
                target_ip=dst_ip,
                target_port=dst_port,
            )
        )
    return connections
