from src.models import AutodiscoverRun, SyncConnector
from src.schemas.autodiscover import (
    AutodiscoverApplyResponse,
    AutodiscoverFieldMapping,
    AutodiscoverScanResponse,
    AutodiscoverSourceReport,
    SyncConnectorResponse,
)
from src.services.autodiscover.credentials import credentials_configured


def connector_to_response(connector: SyncConnector) -> SyncConnectorResponse:
    safe_config = dict(connector.config or {})
    if "auth" in safe_config:
        safe_config = {**safe_config, "auth": {"auth_type": safe_config["auth"].get("auth_type", "none")}}
    if "database_url" in safe_config:
        safe_config = {k: v for k, v in safe_config.items() if k != "database_url"}
    return SyncConnectorResponse(
        id=connector.id,
        name=connector.name,
        connector_type=connector.connector_type,
        server_ci_id=connector.server_ci_id,
        config=safe_config,
        has_credentials=credentials_configured(connector),
        timeout_seconds=connector.timeout_seconds,
        max_retries=connector.max_retries,
        read_only=connector.read_only,
        enabled=connector.enabled,
        auto_sync=bool(getattr(connector, "auto_sync", False)),
        schema_version=connector.schema_version,
    )


def run_to_scan_response(run: AutodiscoverRun) -> AutodiscoverScanResponse:
    report = run.report or {}
    apply_raw = report.get("apply_result")
    apply_result = AutodiscoverApplyResponse(**apply_raw) if apply_raw else None
    return AutodiscoverScanResponse(
        run_id=run.id,
        status=run.status,
        sources_processed=report.get("sources_processed", 0),
        sources_ok=report.get("sources_ok", 0),
        fields_found=report.get("fields_found", 0),
        auto_count=report.get("auto_count", 0),
        needs_confirmation_count=report.get("needs_confirmation_count", 0),
        conflict_count=report.get("conflict_count", 0),
        relation_count=report.get("relation_count", 0),
        ci_create_count=report.get("ci_create_count", 0),
        sources=[AutodiscoverSourceReport(**s) for s in report.get("sources", [])],
        mappings=[
            AutodiscoverFieldMapping(
                mapping_id=m.mapping_id,
                mapping_kind=m.mapping_kind or "field",  # type: ignore[arg-type]
                ci_id=m.ci_id,
                ci_name=m.ci_name,
                target_ci_id=m.target_ci_id,
                target_ci_name=m.target_ci_name,
                relation_type=m.relation_type,
                field=m.field,
                current_value=m.current_value,
                discovered_value=m.discovered_value,
                source_server=m.source_server,
                source_connector=m.source_connector,
                confidence=m.confidence,
                status=m.status,  # type: ignore[arg-type]
                selected=m.selected,
            )
            for m in run.mappings
            if m.status != "unchanged"
        ],
        discovered_schema=run.discovered_schema or {},
        schema_diff=run.schema_diff,
        apply_result=apply_result,
    )
