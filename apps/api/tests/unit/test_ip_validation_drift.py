"""IP validation contract test — shared vectors with web."""

import json
from pathlib import Path

import pytest
from src.core.ip_validation import is_valid_ip_address

ROOT = Path(__file__).resolve().parents[4]
VECTORS_PATH = ROOT / "fixtures" / "ip-validation-vectors.json"
VECTORS = json.loads(VECTORS_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize("value", VECTORS["valid"])
def test_fixture_valid_ip_addresses(value: str) -> None:
    assert is_valid_ip_address(value) is True


@pytest.mark.parametrize("value", VECTORS["invalid"])
def test_fixture_invalid_ip_addresses(value: str) -> None:
    assert is_valid_ip_address(value) is False
