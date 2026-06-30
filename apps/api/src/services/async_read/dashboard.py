from __future__ import annotations

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.core.constants import CI_STATUSES
from src.schemas.audit import RelationValidationResponse
from src.schemas.resources import DashboardOverviewResponse
from src.services.async_read.audit import AsyncAuditReadService
from src.services.base.async_domain import AsyncDomainService
from src.services.domain.dashboard import build_dashboard_overview
from src.services.rsm.async_validation import validate_relations_async
from src.services.rsm.model_health import compute_model_health


class AsyncDashboardService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)

    async def overview(self) -> DashboardOverviewResponse:
        ci_repo = self._bundle.ci
        rel_repo = self._bundle.relations
        total_ci = await ci_repo.count_active()
        total_relations = await rel_repo.count_active()
        by_status = {status: await ci_repo.count_active_by_status(status) for status in CI_STATUSES}
        by_type = await ci_repo.count_active_by_type_name()
        validation = RelationValidationResponse.model_validate(
            await validate_relations_async(ci_repo=ci_repo, rel_repo=rel_repo),
        )
        model_health = await compute_model_health(
            ci_repo=ci_repo,
            rel_repo=rel_repo,
            relation_valid=validation.valid,
            relation_issue_count=validation.issue_count,
        )
        audit = await AsyncAuditReadService(self._bundle).list_logs(limit=8)
        return build_dashboard_overview(
            total_ci=total_ci,
            total_relations=total_relations,
            by_status=by_status,
            by_type=by_type,
            validation=validation,
            model_health=model_health,
            recent_audit=audit.items,
        )
