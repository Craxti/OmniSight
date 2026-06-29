"""Combined RSM export builders (FR 26–28): elements + relations in CSV/XLSX."""

import csv
import io
import json
import zipfile

from openpyxl import Workbook
from src.models import CI, Relation

from .ci import CI_CSV_HEADERS, _ci_row
from .relations import RELATION_CSV_HEADERS, _relation_row


def build_rsm_xlsx(cis: list[CI], relations: list[Relation]) -> io.BytesIO:
    wb = Workbook()
    ws_ci = wb.active
    ws_ci.title = "Elements"
    ws_ci.append(CI_CSV_HEADERS)
    for ci in cis:
        ws_ci.append(_ci_row(ci))

    ws_rel = wb.create_sheet("Relations")
    ws_rel.append(RELATION_CSV_HEADERS)
    for rel in relations:
        ws_rel.append(_relation_row(rel))

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def build_rsm_csv_zip(cis: list[CI], relations: list[Relation]) -> io.BytesIO:
    elements = io.StringIO()
    writer = csv.writer(elements)
    writer.writerow(CI_CSV_HEADERS)
    for ci in cis:
        writer.writerow(_ci_row(ci))

    rels = io.StringIO()
    rel_writer = csv.writer(rels)
    rel_writer.writerow(RELATION_CSV_HEADERS)
    for rel in relations:
        rel_writer.writerow(_relation_row(rel))

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("elements.csv", elements.getvalue())
        zf.writestr("relations.csv", rels.getvalue())
        zf.writestr(
            "manifest.json",
            json.dumps(
                {
                    "format": "rsm-csv-v1",
                    "element_count": len(cis),
                    "relation_count": len(relations),
                },
                indent=2,
            ),
        )
    buf.seek(0)
    return buf
