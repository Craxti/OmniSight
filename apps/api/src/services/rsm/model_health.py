"""Model quality metrics and non-blocking warnings for the dashboard."""

from __future__ import annotations

from sqlalchemy import func, or_, select
from src.core.constants import EXTERNAL_ID_FIELDS, FIELD_TO_SEARCH_COLUMN
from src.models import CI, CIType, Relation
from src.repositories.async_orm.ci_repository import AsyncCiRepository
from src.repositories.async_orm.relation_repository import AsyncRelationRepository
from src.schemas.resources import DashboardModelHealth, DashboardModelWarning

_WARNING_MESSAGES: dict[str, str] = {
    "no_external_id": "CI without external identifiers (hostname, IP, serviceCode…)",
    "orphan_ci": "CI with no active relations",
    "critical_no_owner": "Critical CI without owner",
    "duplicate_external_id": "Duplicate external identifier values in the model",
    "business_service_isolated": "Business Service without depends_on relations",
}


async def compute_model_health(
    *,
    ci_repo: AsyncCiRepository,
    rel_repo: AsyncRelationRepository,
    relation_valid: bool,
    relation_issue_count: int,
) -> DashboardModelHealth:
    total_ci = await ci_repo.count_active()
    no_ext_id = await _count_without_external_id(ci_repo)
    orphan_count = await _count_orphan_cis(ci_repo, rel_repo)
    critical_no_owner = await _count_critical_without_owner(ci_repo)
    duplicate_ext = await _count_duplicate_external_ids(ci_repo)
    isolated_bs = await _count_isolated_business_services(ci_repo, rel_repo)

    warnings: list[DashboardModelWarning] = []
    for warning_type, count in (
        ("no_external_id", no_ext_id),
        ("orphan_ci", orphan_count),
        ("critical_no_owner", critical_no_owner),
        ("duplicate_external_id", duplicate_ext),
        ("business_service_isolated", isolated_bs),
    ):
        if count > 0:
            warnings.append(
                DashboardModelWarning(
                    type=warning_type,
                    message=_WARNING_MESSAGES[warning_type],
                    count=count,
                ),
            )

    with_ext_id = max(0, total_ci - no_ext_id)
    coverage = round(100.0 * with_ext_id / total_ci, 1) if total_ci else 100.0

    return DashboardModelHealth(
        valid=relation_valid,
        issue_count=relation_issue_count,
        warning_count=len(warnings),
        warnings=warnings,
        external_id_coverage_pct=coverage,
        correlation_ready=coverage >= 80.0 and duplicate_ext == 0,
    )


async def _count_without_external_id(ci_repo: AsyncCiRepository) -> int:
    db = ci_repo._db
    has_id = or_(
        CI.search_hostname.isnot(None),
        CI.search_ip.isnot(None),
        CI.search_service_code.isnot(None),
        CI.search_application_code.isnot(None),
        CI.search_external_id.isnot(None),
    )
    stmt = select(func.count()).select_from(CI).where(CI.is_deleted.is_(False), ~has_id)
    return int((await db.execute(stmt)).scalar_one())


async def _count_orphan_cis(ci_repo: AsyncCiRepository, rel_repo: AsyncRelationRepository) -> int:
    ci_ids = await ci_repo.list_active_ids()
    if not ci_ids:
        return 0
    relations = await rel_repo.list_active_non_archived()
    connected: set[int] = set()
    for rel in relations:
        connected.add(rel.source_ci_id)
        connected.add(rel.target_ci_id)
    return len(ci_ids - connected)


async def _count_critical_without_owner(ci_repo: AsyncCiRepository) -> int:
    db = ci_repo._db
    stmt = (
        select(func.count())
        .select_from(CI)
        .where(
            CI.is_deleted.is_(False),
            CI.criticality == "critical",
            or_(CI.owner.is_(None), CI.owner == ""),
        )
    )
    return int((await db.execute(stmt)).scalar_one())


async def _count_duplicate_external_ids(ci_repo: AsyncCiRepository) -> int:
    db = ci_repo._db
    duplicate_values = 0
    for field in EXTERNAL_ID_FIELDS:
        col_name = FIELD_TO_SEARCH_COLUMN.get(field)
        if not col_name:
            continue
        col = getattr(CI, col_name)
        groups = (
            select(func.count().label("cnt"))
            .select_from(CI)
            .where(CI.is_deleted.is_(False), col.isnot(None), col != "")
            .group_by(col)
            .having(func.count() > 1)
            .subquery()
        )
        dup_stmt = select(func.coalesce(func.sum(groups.c.cnt - 1), 0))
        duplicate_values += int((await db.execute(dup_stmt)).scalar_one())
    return duplicate_values


async def _count_isolated_business_services(
    ci_repo: AsyncCiRepository,
    rel_repo: AsyncRelationRepository,
) -> int:
    db = ci_repo._db
    bs_stmt = (
        select(CI.id)
        .join(CIType, CI.type_id == CIType.id)
        .where(CI.is_deleted.is_(False), CIType.name == "Business Service")
    )
    bs_ids = {row[0] for row in (await db.execute(bs_stmt)).all()}
    if not bs_ids:
        return 0

    rel_stmt = select(Relation.source_ci_id, Relation.target_ci_id).where(
        Relation.is_deleted.is_(False),
        Relation.relation_type == "depends_on",
        Relation.status != "archived",
        or_(
            Relation.source_ci_id.in_(bs_ids),
            Relation.target_ci_id.in_(bs_ids),
        ),
    )
    linked: set[int] = set()
    for source_id, target_id in (await db.execute(rel_stmt)).all():
        if source_id in bs_ids:
            linked.add(source_id)
        if target_id in bs_ids:
            linked.add(target_id)
    return len(bs_ids - linked)
