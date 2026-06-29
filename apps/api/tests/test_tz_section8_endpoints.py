"""HTTP smoke tests for §8 TZ API endpoints (resources + correlation)."""

from fastapi.testclient import TestClient

from tests.rsm_helpers import seed_chain
from tests.v1_helpers import API_V1, ci, items, search


def test_section8_resource_card(client: TestClient, auth_headers: dict):
    db_id, _, _ = seed_chain(client, auth_headers)
    r = client.get(f"{API_V1}/resources/{db_id}", headers=auth_headers)
    assert r.status_code == 200, r.text
    body = ci(r.json())
    for field in ("name", "type", "status", "criticality", "environment", "owner", "external_ids", "last_changed_at"):
        assert field in body, f"missing {field}"


def test_section8_resource_search(client: TestClient, auth_headers: dict):
    seed_chain(client, auth_headers)
    for params in (
        {"hostname": "app-01"},
        {"ip": "10.0.0.5"},
        {"externalId": "ext-db-1"},
        {"serviceCode": "PAY"},
        {"applicationCode": "PAY-APP"},
        {"owner": "ops"},
    ):
        r = client.get(f"{API_V1}/resources/search", params=params, headers=auth_headers)
        assert r.status_code == 200, r.text
        assert search(r.json())["total"] >= 1, params


def test_section8_resource_relations_and_graph(client: TestClient, auth_headers: dict):
    db_id, app_id, _ = seed_chain(client, auth_headers)
    rels = client.get(f"{API_V1}/resources/{db_id}/relations", headers=auth_headers)
    assert rels.status_code == 200, rels.text
    rel_items = items(rels.json())
    assert rel_items
    rel = next(item for item in rel_items if item["source_ci_id"] == app_id and item["target_ci_id"] == db_id)
    assert rel["relation_type"]
    assert rel.get("direction")

    graph = client.get(f"{API_V1}/resources/{db_id}/graph", params={"depth": 3}, headers=auth_headers)
    assert graph.status_code == 200, graph.text
    g = graph.json()["graph"]
    assert len(g["nodes"]) >= 3
    if g["edges"]:
        edge = g["edges"][0]
        assert edge.get("relation_type")
        assert edge.get("source_ci_id") is not None
        assert edge.get("target_ci_id") is not None


def test_section8_impact_and_components(client: TestClient, auth_headers: dict):
    db_id, _, biz_id = seed_chain(client, auth_headers)
    impact = client.get(f"{API_V1}/resources/{db_id}/impact", headers=auth_headers)
    assert impact.status_code == 200, impact.text
    imp = impact.json()["impact"]
    services = imp.get("impacted_business_services") or imp.get("business_services") or []
    assert len(services) >= 1

    components = client.get(f"{API_V1}/resources/{biz_id}/components", headers=auth_headers)
    assert components.status_code == 200, components.text
    comps = components.json()["components"].get("components", [])
    assert len(comps) >= 1


def test_section8_resolve_and_correlation_context(client: TestClient, auth_headers: dict):
    db_id, app_id, biz_id = seed_chain(client, auth_headers)
    alerts = [
        {"hostname": "app-01"},
        {"ip": "10.0.0.5"},
        {"externalId": "ext-db-1"},
        {"serviceCode": "PAY", "applicationCode": "PAY-APP"},
    ]
    resolve = client.post(f"{API_V1}/resources/resolve", json={"alerts": alerts}, headers=auth_headers)
    assert resolve.status_code == 200, resolve.text
    resolved = resolve.json()["resolved"]
    assert len(resolved) == 4
    assert all(item["resolved"] for item in resolved)

    context = client.post(
        f"{API_V1}/correlation/context",
        json={"resource_ids": [db_id, app_id, biz_id], "depth": 3},
        headers=auth_headers,
    )
    assert context.status_code == 200, context.text
    corr = context.json()["correlation"]
    assert corr["chain_related"] is True
    assert corr["graph"]["nodes"]
    assert "enrichment" in corr
