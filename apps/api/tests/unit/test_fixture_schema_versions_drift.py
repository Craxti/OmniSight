"""Drift test — fixtures/schema-versions.json must mirror schemas/v1/versions.py."""

import json
from pathlib import Path

from src.schemas.v1.versions import SCHEMA_VERSIONS_V1

_FIXTURE = Path(__file__).resolve().parents[4] / "fixtures" / "schema-versions.json"


def test_fixture_schema_versions_match_core():
    body = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    assert body == SCHEMA_VERSIONS_V1
