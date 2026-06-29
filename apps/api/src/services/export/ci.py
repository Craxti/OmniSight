import json

from src.models import CI
from src.services.export.tabular import build_csv, build_xlsx

CI_CSV_HEADERS = [
    "name",
    "status",
    "type_name",
    "criticality",
    "environment",
    "owner",
    "team",
    "attributes",
    "external_ids",
]


def _ci_row(ci: CI) -> list:
    return [
        ci.name,
        ci.status,
        ci.ci_type.name if ci.ci_type else "",
        ci.criticality or "",
        ci.environment or "",
        ci.owner or "",
        ci.team or "",
        json.dumps(ci.attributes or {}),
        json.dumps(ci.external_ids or {}),
    ]


def build_ci_csv(cis: list[CI]) -> str:
    return build_csv(CI_CSV_HEADERS, cis, _ci_row)


def build_ci_xlsx(cis: list[CI]):
    return build_xlsx("CI", CI_CSV_HEADERS, cis, _ci_row)
