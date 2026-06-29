"""Canonical resource routes mirror CI endpoints (§8 TZ)."""

from fastapi.testclient import TestClient
from tests.v1_helpers import API_V1, ci


def test_resource_detail_is_ci_alias(client: TestClient, auth_headers: dict):
    created = client.post(
        f"{API_V1}/ci",
        json={"name": "resource-alias-ci", "type_name": "Server", "status": "active"},
        headers=auth_headers,
    )
    assert created.status_code == 200, created.text
    ci_id = ci(created.json())["id"]

    r = client.get(f"{API_V1}/resources/{ci_id}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert ci(r.json())["name"] == "resource-alias-ci"


def test_resource_relations_is_ci_relations_alias(client: TestClient, auth_headers: dict):
    from tests.rsm_helpers import seed_chain

    db_id, app_id, _ = seed_chain(client, auth_headers)
    r = client.get(f"{API_V1}/resources/{app_id}/relations", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert any(item["target_ci_id"] == db_id for item in r.json()["items"])
