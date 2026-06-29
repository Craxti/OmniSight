"""Native async read dependency providers."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from src.core import database_async
from src.core.async_unit_of_work import AsyncDbSessionScope


def _read_port_dep(async_factory: str):
    async def provider() -> AsyncGenerator[object, None]:
        async with database_async.async_read_session() as session:
            scope = AsyncDbSessionScope.from_session(session)
            yield getattr(scope.services, async_factory)()

    return provider


get_ci_read_port = _read_port_dep("ci_read_service")
get_relation_read_port = _read_port_dep("relation_read_service")
get_topology_read_port = _read_port_dep("topology_service")
get_dashboard_read_port = _read_port_dep("dashboard_service")
get_search_read_port = _read_port_dep("search_service")
get_correlation_read_port = _read_port_dep("correlation_service")
get_graph_layout_read_port = _read_port_dep("graph_layout_service")
get_audit_read_port = _read_port_dep("audit_service")
get_user_read_port = _read_port_dep("user_service")
get_ci_type_read_port = _read_port_dep("ci_type_service")
get_relation_type_read_port = _read_port_dep("relation_type_service")
get_ci_import_export_read_port = _read_port_dep("ci_import_export_read_service")
get_relation_import_export_read_port = _read_port_dep("relation_import_export_read_service")
get_autodiscover_read_port = _read_port_dep("autodiscover_service")
