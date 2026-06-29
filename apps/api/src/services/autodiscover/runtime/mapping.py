"""Native async autodiscover entity → mapping conversion."""

from __future__ import annotations

from src.models import CI
from src.repositories.async_orm.ci_repository import AsyncCiRepository
from src.repositories.async_orm.ci_type_repository import AsyncCITypeRepository
from src.repositories.async_orm.relation_type_repository import AsyncRelationTypeRepository
from src.services.async_import_validate import find_external_id_conflict_async
from src.services.autodiscover.connectors.base import DiscoveredEntity
from src.services.autodiscover.mapping_helpers import proposed_ci_name, rules_flag, template_fields_for_type
from src.services.autodiscover.normalize import (
    EXTERNAL_ID_FIELDS,
    TOP_LEVEL_FIELDS,
    normalize_field_key,
    normalize_value,
)
from src.services.autodiscover.runtime.relations import infer_hosted_on_for_entity_async, map_entity_relations_async
from src.services.autodiscover.scope import current_field_value
from src.services.rsm.indexed_ids import merge_external_ids


async def _resolve_type_id_async(type_repo: AsyncCITypeRepository, entity_type: str | None) -> int | None:
    if not entity_type:
        return None
    row = await type_repo.get_by_name(entity_type)
    return row.id if row else None


async def classify_mapping_async(
    ci_repo: AsyncCiRepository,
    *,
    ci: CI,
    field: str,
    current: str | None,
    discovered: str,
    rules: dict | None = None,
) -> tuple[float, str]:
    threshold_auto = float((rules or {}).get("auto_apply_threshold", 0.85))
    if current and current == discovered:
        return 1.0, "unchanged"
    if field in EXTERNAL_ID_FIELDS:
        probe = dict(merge_external_ids(ci.attributes, ci.external_ids))
        probe[field] = discovered
        conflict_msg = await find_external_id_conflict_async(ci_repo, probe, exclude_ci_id=ci.id)
        if conflict_msg:
            return 0.35, "conflict"
    if current and current != discovered:
        return 0.4, "needs_confirmation"
    confidence = 0.92
    return (confidence, "auto") if confidence >= threshold_auto else (confidence, "needs_confirmation")


async def map_entity_to_ci_fields_async(
    ci_repo: AsyncCiRepository,
    *,
    ci: CI,
    entity: DiscoveredEntity,
    rules: dict | None,
) -> list[dict]:
    allowed = template_fields_for_type(ci, rules)
    mappings: list[dict] = []
    for raw_key, raw_val in entity.fields.items():
        field = normalize_field_key(str(raw_key), rules)
        if field == "hostname":
            continue
        if field not in allowed and not field.startswith("attributes."):
            if field not in (ci.attributes or {}) and field not in EXTERNAL_ID_FIELDS and field not in TOP_LEVEL_FIELDS:
                continue
        discovered = normalize_value(raw_val, field)
        if not discovered:
            continue
        current = current_field_value(ci, field)
        confidence, status = await classify_mapping_async(
            ci_repo,
            ci=ci,
            field=field,
            current=current,
            discovered=discovered,
            rules=rules,
        )
        if status == "unchanged":
            continue
        mappings.append(
            {
                "ci_id": ci.id,
                "ci_name": ci.name,
                "field": field,
                "current_value": current,
                "discovered_value": discovered,
                "confidence": confidence,
                "status": status,
            }
        )
    return mappings


async def map_discovered_entities_async(
    *,
    entities: list[DiscoveredEntity],
    scope_ids: set[int],
    rules: dict | None,
    source_server: str,
    source_connector: str,
    scope_mode: str = "all",
    server_ci_id: int | None = None,
    ci_repo: AsyncCiRepository,
    rel_repo: AsyncRelationRepository,
    type_repo: AsyncCITypeRepository,
    relation_type_repo: AsyncRelationTypeRepository,
) -> list[dict]:
    discover_relations = rules_flag(rules, "discover_relations", True)
    create_missing_ci = rules_flag(rules, "create_missing_ci", True)
    scope_all = scope_mode == "all"
    discovered_hosts = {str(e.match_key).strip().lower() for e in entities if str(e.match_key).strip()}

    seen: set[tuple[str, ...]] = set()
    dedupe_key: tuple[str, ...]
    out: list[dict] = []
    entity_context: list[dict] = []

    for entity in entities:
        hostname = str(entity.match_key).strip()
        if not hostname:
            continue
        target = await ci_repo.find_by_identifier(hostname)
        if not target and entity.fields.get("ip"):
            target = await ci_repo.find_by_identifier(str(entity.fields["ip"]))
        if not target:
            alt_name = entity.fields.get("name")
            if alt_name:
                target = await ci_repo.find_by_identifier(str(alt_name))
        if not target and entity.entity_type == "Server" and server_ci_id:
            target = await ci_repo.get_active(server_ci_id)

        source_ci_id: int | None = target.id if target else None
        source_ci_name = target.name if target else proposed_ci_name(hostname, entity)

        if not target and create_missing_ci:
            type_name = entity.entity_type or "Application"
            if not (type_name == "Server" and server_ci_id):
                type_id = await _resolve_type_id_async(type_repo, type_name)
                threshold_auto = float((rules or {}).get("auto_apply_threshold", 0.85))
                confidence = 0.9 if type_id else 0.55
                status = "auto" if type_id and confidence >= threshold_auto else "needs_confirmation"
                dedupe_key = ("ci_create", hostname)
                if dedupe_key not in seen:
                    seen.add(dedupe_key)
                    out.append(
                        {
                            "mapping_kind": "ci_create",
                            "ci_id": None,
                            "ci_name": source_ci_name,
                            "field": type_name,
                            "current_value": None,
                            "discovered_value": hostname,
                            "payload": {
                                "hostname": hostname,
                                "entity_type": type_name,
                                "type_id": type_id,
                                "fields": dict(entity.fields),
                            },
                            "confidence": confidence,
                            "status": status,
                            "source_server": source_server,
                            "source_connector": source_connector,
                        }
                    )
        in_scope = scope_all or (source_ci_id is not None and source_ci_id in scope_ids) or source_ci_id is None
        if in_scope and target:
            for item in await map_entity_to_ci_fields_async(ci_repo, ci=target, entity=entity, rules=rules):
                dedupe_key = ("field", item["ci_id"], item["field"])
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                out.append(
                    {
                        **item,
                        "mapping_kind": "field",
                        "source_server": source_server,
                        "source_connector": source_connector,
                    }
                )

        entity_context.append(
            {
                "entity": entity,
                "hostname": hostname,
                "source_ci_id": source_ci_id,
                "source_ci_name": source_ci_name,
                "target": target,
                "in_scope": in_scope,
            }
        )

    if discover_relations:
        for ctx in entity_context:
            entity = ctx["entity"]
            hostname = ctx["hostname"]
            for item in await map_entity_relations_async(
                entity=entity,
                source_ci_id=ctx["source_ci_id"],
                source_ci_name=ctx["source_ci_name"],
                rules=rules,
                source_server=source_server,
                source_connector=source_connector,
                source_match_key=hostname,
                discovered_hosts=discovered_hosts,
                ci_repo=ci_repo,
                rel_repo=rel_repo,
                relation_type_repo=relation_type_repo,
            ):
                dedupe_key = (
                    "relation",
                    item.get("payload", {}).get("source_hostname"),
                    item["relation_type"],
                    item["discovered_value"],
                )
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                out.append(item)
            for item in await infer_hosted_on_for_entity_async(
                entity=entity,
                source_ci_id=ctx["source_ci_id"],
                source_ci_name=ctx["source_ci_name"],
                server_ci_id=server_ci_id,
                rules=rules,
                source_server=source_server,
                source_connector=source_connector,
                ci_repo=ci_repo,
                rel_repo=rel_repo,
            ):
                dedupe_key = (
                    "relation",
                    item.get("payload", {}).get("source_hostname"),
                    item["relation_type"],
                    item["discovered_value"],
                )
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                out.append(item)

    return out
