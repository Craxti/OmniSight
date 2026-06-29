"""Pluggable tabular export formats (CSV, XLSX, RSM bundle)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from src.models import CI, Relation

TabularExportFn = Callable[..., Any]

_EXPORTERS: dict[str, TabularExportFn] = {}


def register_exporter(name: str, fn: TabularExportFn) -> None:
    _EXPORTERS[name] = fn


def get_exporter(name: str) -> TabularExportFn:
    if name not in _EXPORTERS:
        raise KeyError(f"Unknown export format: {name}")
    return _EXPORTERS[name]


def list_exporters() -> list[str]:
    _bootstrap()
    return sorted(_EXPORTERS)


def _bootstrap() -> None:
    if _EXPORTERS:
        return
    from src.services.export.ci import build_ci_csv, build_ci_xlsx
    from src.services.export.relations import build_relations_csv, build_relations_xlsx
    from src.services.export.rsm import build_rsm_csv_zip, build_rsm_xlsx

    register_exporter("ci_csv", build_ci_csv)
    register_exporter("ci_xlsx", build_ci_xlsx)
    register_exporter("relations_csv", build_relations_csv)
    register_exporter("relations_xlsx", build_relations_xlsx)
    register_exporter("rsm_csv", build_rsm_csv_zip)
    register_exporter("rsm_xlsx", build_rsm_xlsx)


def export_tabular(name: str, cis: list[CI], relations: list[Relation]) -> Any:
    _bootstrap()
    fn = get_exporter(name)
    if name.startswith("rsm_"):
        return fn(cis, relations)
    if name.startswith("relations_"):
        return fn(relations)
    return fn(cis)
