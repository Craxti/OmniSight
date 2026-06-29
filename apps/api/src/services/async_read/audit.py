from __future__ import annotations

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.repositories.protocols import AsyncAuditRepositoryProtocol
from src.schemas.audit import AuditListResponse, AuditLogResponse
from src.services.base.async_domain import AsyncDomainService
from src.services.domain.audit import build_audit_list, build_entity_history, fetch_entity_history_async


class AsyncAuditReadService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)

    async def list_logs(self, **kwargs) -> AuditListResponse:
        skip = kwargs.pop("skip", 0)
        limit = kwargs.pop("limit", 50)
        items, total = await self._bundle.audit.search(skip=skip, limit=limit, **kwargs)
        return build_audit_list(items, total, skip, limit)

    async def entity_history(self, entity_type: str, entity_id: int) -> list[AuditLogResponse]:
        audit_repo: AsyncAuditRepositoryProtocol = self._bundle.audit
        items = await fetch_entity_history_async(audit_repo, entity_type, entity_id)
        return build_entity_history(items)
