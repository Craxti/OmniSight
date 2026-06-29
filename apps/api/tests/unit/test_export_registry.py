"""Export registry smoke tests."""

from src.services.export.registry import export_tabular, list_exporters


def test_export_registry_lists_formats():
    names = list_exporters()
    assert "rsm_csv" in names
    assert "rsm_xlsx" in names


def test_export_registry_rsm_xlsx_empty():
    result = export_tabular("rsm_xlsx", [], [])
    assert result is not None
