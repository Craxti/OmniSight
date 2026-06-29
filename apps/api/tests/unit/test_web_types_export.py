"""Web TypeScript types must match Pydantic export."""

from scripts.export_web_types import OUT, render


def test_web_types_export_is_current() -> None:
    expected = render()
    assert OUT.is_file(), f"Missing generated types at {OUT}"
    actual = OUT.read_text(encoding="utf-8")
    assert actual == expected, f"{OUT} is out of date — run: cd apps/api && python scripts/export_web_types.py"
