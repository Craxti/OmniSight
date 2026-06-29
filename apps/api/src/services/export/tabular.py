"""Shared CSV/XLSX builders for tabular export."""

from __future__ import annotations

import csv
import io
from collections.abc import Callable, Iterable
from typing import TypeVar

from openpyxl import Workbook

T = TypeVar("T")


def build_csv(headers: list[str], items: Iterable[T], row_fn: Callable[[T], list]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for item in items:
        writer.writerow(row_fn(item))
    output.seek(0)
    return output.getvalue()


def build_xlsx(sheet_title: str, headers: list[str], items: Iterable[T], row_fn: Callable[[T], list]) -> io.BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_title
    ws.append(headers)
    for item in items:
        ws.append(row_fn(item))
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
