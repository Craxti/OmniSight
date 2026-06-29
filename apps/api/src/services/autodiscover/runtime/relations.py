"""Native async autodiscover relation mapping."""

from __future__ import annotations

from src.repositories.async_orm.ci_repository import AsyncCiRepository
from src.repositories.async_orm.relation_repository import AsyncRelationRepository
from src.repositories.async_orm.relation_type_repository import AsyncRelationTypeRepository
from src.services.autodiscover.connectors.base import DiscoveredEntity
from src.services.autodiscover.relations import (
    extract_relation_specs,
    relation_confidence,
)
from src.services.autodiscover.runtime.scope_helpers import resolve_relation_target_async
from src.services.rsm import normalize_relation_type


async def relation_exists_async(
    rel_repo: AsyncRelationRepository,
    *,
    source_ci_id: int,
    target_ci_id: int,
    relation_type: str,
) -> bool:
    return (await rel_repo.find_active(source_ci_id, target_ci_id, relation_type)) is not None


async def map_entity_relations_async(
    *,
    entity: DiscoveredEntity,
    source_ci_id: int | None,
    source_ci_name: str,
    rules: dict | None,
    source_server: str,
    source_connector: str,
    source_match_key: str | None = None,
    discovered_hosts: set[str] | None = None,
    ci_repo: AsyncCiRepository,
    rel_repo: AsyncRelationRepository,
    relation_type_repo: AsyncRelationTypeRepository,
) -> list[dict]:
    threshold_auto = float((rules or {}).get("auto_apply_threshold", 0.85))
    match_key = source_match_key or entity.match_key
    batch_hosts = discovered_hosts or set()
    allowed = frozenset(await relation_type_repo.list_keys())
    out: list[dict] = []
    for spec in extract_relation_specs(entity):
        raw_type = spec["relation_type"]
        target_hostname = spec["target_hostname"]
        target_ip = spec.get("target_ip")
        try:
            relation_type = normalize_relation_type(raw_type, allowed=allowed)
        except Exception:
            continue
        target = await resolve_relation_target_async(
            ci_repo,
            hostname=target_hostname,
            ip=target_ip,
        )
        exists = False
        if source_ci_id and target:
            exists = await relation_exists_async(
                rel_repo,
                source_ci_id=source_ci_id,
                target_ci_id=target.id,
                relation_type=relation_type,
            )
        if exists:
            continue
        in_batch = target_hostname.lower() in batch_hosts
        confidence, status = relation_confidence(
            target=target,
            target_ip=target_ip,
            evidence=str(spec.get("evidence")) if spec.get("evidence") else None,
            explicit=float(spec["confidence"]) if spec.get("confidence") is not None else None,
            in_discovered_batch=in_batch and not target,
            threshold_auto=threshold_auto,
        )
        out.append(
            {
                "mapping_kind": "relation",
                "ci_id": source_ci_id,
                "ci_name": source_ci_name,
                "target_ci_id": target.id if target else None,
                "target_ci_name": target.name if target else target_hostname,
                "relation_type": relation_type,
                "field": relation_type,
                "current_value": "—" if not exists else "exists",
                "discovered_value": target_hostname,
                "payload": {
                    "target_hostname": target_hostname,
                    "target_ip": target_ip,
                    "source_hostname": str(match_key),
                    "evidence": spec.get("evidence"),
                },
                "confidence": confidence,
                "status": status,
                "source_server": source_server,
                "source_connector": source_connector,
            }
        )
    return out


async def infer_hosted_on_for_entity_async(
    *,
    entity: DiscoveredEntity,
    source_ci_id: int | None,
    source_ci_name: str,
    server_ci_id: int | None,
    rules: dict | None,
    source_server: str,
    source_connector: str,
    ci_repo: AsyncCiRepository,
    rel_repo: AsyncRelationRepository,
) -> list[dict]:
    if not server_ci_id:
        return []
    if source_ci_id == server_ci_id:
        return []
    ci_type = entity.entity_type or ""
    if ci_type == "Server":
        return []
    if any(spec["relation_type"] == "hosted_on" for spec in extract_relation_specs(entity)):
        return []
    server = await ci_repo.get_active(server_ci_id)
    if not server:
        return []
    if source_ci_id and await relation_exists_async(
        rel_repo,
        source_ci_id=source_ci_id,
        target_ci_id=server.id,
        relation_type="hosted_on",
    ):
        return []
    threshold_auto = float((rules or {}).get("auto_apply_threshold", 0.85))
    confidence = 0.9
    status = "auto" if confidence >= threshold_auto else "needs_confirmation"
    host = (server.external_ids or {}).get("hostname") or server.name
    return [
        {
            "mapping_kind": "relation",
            "ci_id": source_ci_id,
            "ci_name": source_ci_name,
            "target_ci_id": server.id,
            "target_ci_name": server.name,
            "relation_type": "hosted_on",
            "field": "hosted_on",
            "current_value": "—",
            "discovered_value": str(host),
            "payload": {
                "target_hostname": str(host),
                "source_hostname": str(entity.match_key),
                "inferred": True,
            },
            "confidence": confidence,
            "status": status,
            "source_server": source_server,
            "source_connector": source_connector,
        }
    ]
