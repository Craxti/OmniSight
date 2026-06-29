"""Factory for async read domain services."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.async_repository_bundle import AsyncRepositoryBundle


@dataclass(slots=True)
class AsyncServiceFactory:
    bundle: AsyncRepositoryBundle

    def dashboard_service(self):
        from src.services.async_read.dashboard import AsyncDashboardService

        return AsyncDashboardService(self.bundle)

    def ci_read_service(self):
        from src.services.async_read.ci import AsyncCiReadService

        return AsyncCiReadService(self.bundle)

    def relation_read_service(self):
        from src.services.async_read.relations import AsyncRelationReadService

        return AsyncRelationReadService(self.bundle)

    def audit_service(self):
        from src.services.async_read.audit import AsyncAuditReadService

        return AsyncAuditReadService(self.bundle)

    def search_service(self):
        from src.services.async_read.search import AsyncSearchService

        return AsyncSearchService(self.bundle)

    def topology_service(self):
        from src.services.async_read.topology import AsyncTopologyService

        return AsyncTopologyService(self.bundle)

    def correlation_service(self):
        from src.services.async_read.correlation import AsyncCorrelationReadService

        return AsyncCorrelationReadService(self.bundle)

    def user_service(self):
        from src.services.async_read.users import AsyncUserReadService

        return AsyncUserReadService(self.bundle)

    def ci_type_service(self):
        from src.services.async_read.ci_types import AsyncCiTypeReadService

        return AsyncCiTypeReadService(self.bundle)

    def relation_type_service(self):
        from src.services.async_read.relation_types import AsyncRelationTypeReadService

        return AsyncRelationTypeReadService(self.bundle)

    def graph_layout_service(self):
        from src.services.async_read.graph_layout import AsyncGraphLayoutReadService

        return AsyncGraphLayoutReadService(self.bundle)

    def autodiscover_service(self):
        from src.services.async_read.autodiscover import AsyncAutodiscoverReadService

        return AsyncAutodiscoverReadService(self.bundle)

    def ci_import_export_read_service(self):
        from src.services.async_read.import_export import AsyncCiImportExportReadService

        return AsyncCiImportExportReadService(self.bundle)

    def relation_import_export_read_service(self):
        from src.services.async_read.import_export import AsyncRelationImportExportReadService

        return AsyncRelationImportExportReadService(self.bundle)
