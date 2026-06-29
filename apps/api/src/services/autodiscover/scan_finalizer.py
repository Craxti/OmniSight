"""Finalize autodiscover run status, schema, and report."""

from __future__ import annotations

from datetime import UTC, datetime

from src.models import AutodiscoverRun
from src.services.autodiscover.scan_models import CollectResult, ScanConfig
from src.services.autodiscover.schema_diff import diff_schemas, merge_schema


class ScanRunFinalizer:
    def finalize(self, run: AutodiscoverRun, *, config: ScanConfig, collected: CollectResult) -> None:
        discovered_schema = merge_schema(collected.schemas)
        schema_diff = diff_schemas(config.previous_schema, discovered_schema) if config.previous_schema else None
        all_mappings = collected.all_mappings

        auto_count = sum(1 for m in all_mappings if m["status"] == "auto")
        needs_confirmation_count = sum(1 for m in all_mappings if m["status"] == "needs_confirmation")
        conflict_count = sum(1 for m in all_mappings if m["status"] == "conflict")
        relation_count = sum(1 for m in all_mappings if m.get("mapping_kind") == "relation")
        ci_create_count = sum(1 for m in all_mappings if m.get("mapping_kind") == "ci_create")

        status = "completed"
        if collected.sources_ok == 0:
            status = "failed"
        elif collected.sources_ok < len(config.connectors):
            status = "partial"

        run.status = status
        run.completed_at = datetime.now(UTC).replace(tzinfo=None)
        run.discovered_schema = discovered_schema
        run.schema_diff = schema_diff
        run.report = {
            "sources_processed": len(config.connectors),
            "sources_ok": collected.sources_ok,
            "fields_found": len(all_mappings),
            "auto_count": auto_count,
            "needs_confirmation_count": needs_confirmation_count,
            "conflict_count": conflict_count,
            "relation_count": relation_count,
            "ci_create_count": ci_create_count,
            "sources": collected.source_reports,
        }

        if config.profile:
            config.profile.last_run_id = run.id
            config.profile.schema_version = discovered_schema.get("version", config.profile.schema_version)
