"""Domain constants drift test — API meta must include official relation types from DB."""

from src.core.constants import (
    CI_STATUSES,
    CRITICALITY_LEVELS,
    ENVIRONMENTS,
    EXTERNAL_ID_FIELDS,
    RELATION_STATUSES,
    RELATION_TYPE_ALIASES,
    RELATION_TYPES,
    ROLES,
    RSM_OFFICIAL_TYPE_NAMES,
)
from tests.v1_helpers import API_V1


def test_v1_meta_constants_match_core(client, auth_headers):
    response = client.get(f"{API_V1}/meta/constants", headers=auth_headers)
    assert response.status_code == 200, response.text
    body = response.json()
    constants = body["constants"]

    assert body["api_version"] == "v1"
    for official in RELATION_TYPES:
        assert official in constants["relation_types"]
    assert constants["relation_type_aliases"] == RELATION_TYPE_ALIASES
    assert constants["relation_statuses"] == RELATION_STATUSES
    assert constants["ci_statuses"] == CI_STATUSES
    assert constants["criticality_levels"] == CRITICALITY_LEVELS
    assert constants["environments"] == ENVIRONMENTS
    assert constants["external_id_fields"] == EXTERNAL_ID_FIELDS
    assert constants["roles"] == ROLES
    assert constants["rsm_official_type_names"] == RSM_OFFICIAL_TYPE_NAMES
