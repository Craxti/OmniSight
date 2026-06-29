"""Unit tests for autodiscover scan pipeline classes."""

from unittest.mock import MagicMock

from src.services.autodiscover.scan_finalizer import ScanRunFinalizer
from src.services.autodiscover.scan_models import CollectResult, ScanConfig


def test_scan_run_finalizer_marks_failed_when_no_sources_ok():
    run = MagicMock()
    config = ScanConfig(
        profile=None,
        connector_ids=None,
        server_ci_ids=[],
        source_types=None,
        scope_mode="all",
        scope_config={},
        mapping_rules={},
        connectors=[MagicMock(), MagicMock()],
        previous_schema=None,
    )
    collected = CollectResult(source_reports=[], all_mappings=[], schemas=[], sources_ok=0)
    ScanRunFinalizer().finalize(run, config=config, collected=collected)
    assert run.status == "failed"
    assert run.report["sources_processed"] == 2
