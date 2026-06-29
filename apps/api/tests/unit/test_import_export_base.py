"""Unit tests for shared import/export helpers."""

import io

from src.services.import_export.base import csv_streaming_response, xlsx_streaming_response


def test_csv_streaming_response_headers():
    resp = csv_streaming_response("a,b\n1,2", "test.csv")
    assert resp.media_type == "text/csv"
    assert 'filename="test.csv"' in resp.headers["Content-Disposition"]


def test_xlsx_streaming_response_headers():
    buf = io.BytesIO(b"fake-xlsx")
    resp = xlsx_streaming_response(buf, "test.xlsx")
    assert resp.media_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert 'filename="test.xlsx"' in resp.headers["Content-Disposition"]
