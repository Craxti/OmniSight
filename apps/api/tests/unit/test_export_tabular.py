from src.services.export.ci import build_ci_csv, build_ci_xlsx
from src.services.export.tabular import build_csv


def test_build_csv_roundtrip():
    rows = [["a", "1"], ["b", "2"]]
    headers = ["name", "value"]

    def row_fn(item: list[str]) -> list[str]:
        return item

    csv_text = build_csv(headers, rows, row_fn)
    assert "name,value" in csv_text
    assert "a,1" in csv_text


def test_build_ci_csv_headers():
    from src.models import CI, CIType

    t = CIType(name="Server", attribute_schema={"properties": {}})
    ci = CI(name="test-ci", type_id=1, status="active", ci_type=t)
    csv_text = build_ci_csv([ci])
    assert "name,status,type_name" in csv_text
    assert "test-ci,active,Server" in csv_text


def test_build_ci_xlsx_sheet_title():
    from openpyxl import load_workbook
    from src.models import CI, CIType

    t = CIType(name="Server", attribute_schema={"properties": {}})
    ci = CI(name="xlsx-ci", type_id=1, status="active", ci_type=t)
    buf = build_ci_xlsx([ci])
    wb = load_workbook(buf)
    assert wb.active.title == "CI"
