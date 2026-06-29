"""Shared dashboard overview assembly."""

from __future__ import annotations

from src.schemas.audit import AuditLogResponse, RelationValidationResponse
from src.schemas.resources import DashboardModelHealth, DashboardOverviewResponse


def build_dashboard_overview(
    *,
    total_ci: int,
    total_relations: int,
    by_status: dict[str, int],
    by_type: dict[str, int],
    validation: RelationValidationResponse,
    recent_audit: list[AuditLogResponse],
) -> DashboardOverviewResponse:
    return DashboardOverviewResponse(
        total_ci=total_ci,
        total_relations=total_relations,
        by_status=by_status,
        by_type=by_type,
        model_health=DashboardModelHealth(valid=validation.valid, issue_count=validation.issue_count),
        recent_audit=recent_audit,
    )
