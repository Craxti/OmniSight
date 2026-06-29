"""Shared autodiscover scan request for connector auto-sync."""

from __future__ import annotations

from src.schemas.autodiscover import AutodiscoverScanRequest


def connector_auto_sync_request(connector_id: int) -> AutodiscoverScanRequest:
    return AutodiscoverScanRequest(
        connector_ids=[connector_id],
        scope_mode="all",
        discover_relations=True,
        create_missing_ci=True,
        auto_apply=True,
    )
