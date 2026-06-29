"""Async relation model validation."""

from __future__ import annotations

from src.repositories.async_orm.ci_repository import AsyncCiRepository
from src.repositories.async_orm.relation_repository import AsyncRelationRepository
from src.services.rsm.depends_on_cycle import find_depends_on_cycle_start


async def validate_relations_async(
    *,
    ci_repo: AsyncCiRepository,
    rel_repo: AsyncRelationRepository,
) -> dict:
    issues: list[dict] = []
    relations = await rel_repo.list_active_non_archived()
    ci_ids = await ci_repo.list_active_ids()
    archived_ids = await ci_repo.archived_active_ids()

    for rel in relations:
        if rel.source_ci_id not in ci_ids or rel.target_ci_id not in ci_ids:
            issues.append({"relation_id": rel.id, "type": "broken_reference", "message": "Missing CI reference"})
        if rel.source_ci_id in archived_ids or rel.target_ci_id in archived_ids:
            issues.append({"relation_id": rel.id, "type": "archived_reference", "message": "Links archived CI"})

    adj: dict[int, list[int]] = {}
    for rel in relations:
        if rel.relation_type == "depends_on":
            adj.setdefault(rel.source_ci_id, []).append(rel.target_ci_id)

    cycle_start = find_depends_on_cycle_start(adj)
    if cycle_start is not None:
        issues.append({"relation_id": None, "type": "cycle", "message": f"Cycle detected from CI {cycle_start}"})

    return {"valid": len(issues) == 0, "issues": issues, "issue_count": len(issues)}
