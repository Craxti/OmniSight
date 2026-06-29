"""Domain service dependency providers."""

from __future__ import annotations

from src.core.deps.read import (  # noqa: F401
    get_audit_read_port,
    get_autodiscover_read_port,
    get_ci_import_export_read_port,
    get_ci_read_port,
    get_ci_type_read_port,
    get_correlation_read_port,
    get_dashboard_read_port,
    get_graph_layout_read_port,
    get_relation_import_export_read_port,
    get_relation_read_port,
    get_relation_type_read_port,
    get_search_read_port,
    get_topology_read_port,
    get_user_read_port,
)
from src.core.deps.write import (  # noqa: F401
    get_autodiscover_write_port,
    get_ci_import_export_write_port,
    get_ci_type_write_port,
    get_ci_write_port,
    get_correlation_write_port,
    get_graph_layout_write_port,
    get_relation_import_export_write_port,
    get_relation_type_write_port,
    get_relation_write_port,
    get_transactional_autodiscover_write_port,
    get_transactional_ci_import_export_write_port,
    get_user_write_port,
)
