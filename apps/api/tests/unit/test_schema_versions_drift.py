"""Ensure v1 schema_version strings stay aligned with web generated constants."""

from src.schemas.v1.versions import SCHEMA_VERSIONS_V1


def test_schema_versions_v1_registry():
    assert SCHEMA_VERSIONS_V1["inventory"] == "rsm-inventory-v1"
    assert SCHEMA_VERSIONS_V1["auth"] == "rsm-auth-v1"
    assert SCHEMA_VERSIONS_V1["topology"] == "rsm-topology-v1"
    assert len(SCHEMA_VERSIONS_V1) == 7
