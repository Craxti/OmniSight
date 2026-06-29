"""Drift test — fixtures/domain-constants.json must mirror core/constants.py."""

import json
from pathlib import Path

from src.core.constants import (
    CI_STATUSES,
    CRITICALITY_LEVELS,
    ENVIRONMENTS,
    EXTERNAL_ID_FIELDS,
    FIELD_ALIASES,
    RELATION_STATUSES,
    RELATION_TYPES,
    ROLES,
    RSM_OFFICIAL_TYPE_NAMES,
)

_FIXTURE = Path(__file__).resolve().parents[4] / "fixtures" / "domain-constants.json"


def test_fixture_domain_constants_match_core():
    body = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    assert body["relation_types"] == RELATION_TYPES
    assert body["relation_statuses"] == RELATION_STATUSES
    assert body["ci_statuses"] == CI_STATUSES
    assert body["criticality_levels"] == CRITICALITY_LEVELS
    assert body["environments"] == ENVIRONMENTS
    assert body["external_id_fields"] == EXTERNAL_ID_FIELDS
    assert body["field_aliases"] == FIELD_ALIASES
    assert body["roles"] == ROLES
    assert body["rsm_official_type_names"] == RSM_OFFICIAL_TYPE_NAMES
