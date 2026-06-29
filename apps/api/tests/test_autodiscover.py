"""Autodiscover API tests."""

from fastapi.testclient import TestClient
from src.core.fixture_paths import fixture_path

from tests.seed_helpers import create_relation, get_or_create_ci, get_type_map
from tests.v1_helpers import API_V1, ci, items, j

FIXTURE_HOST_SNAPSHOT = fixture_path("host_snapshot_pay_srv.json")


def _seed_autodiscover_chain(client: TestClient, headers: dict) -> dict[str, int]:
    types = get_type_map(client, headers)
    srv_id = get_or_create_ci(
        client, headers, types, "demo-pay-srv", "Server", hostname="pay-srv-01", ip="10.0.0.21", os="Ubuntu 24.04"
    )
    app_id = get_or_create_ci(
        client,
        headers,
        types,
        "demo-app",
        "Application",
        hostname="app-01",
        serviceCode="PAY",
        applicationCode="PAY-APP",
    )
    db_id = get_or_create_ci(
        client, headers, types, "demo-db", "Database", hostname="demo-db", ip="10.0.0.5", externalId="ext-db-1"
    )

    create_relation(client, headers, app_id, db_id)
    create_relation(client, headers, app_id, srv_id, "hosted_on")

    r = client.post(
        f"{API_V1}/autodiscover/connectors",
        json={
            "name": "test-host-pay-srv",
            "connector_type": "host",
            "server_ci_id": srv_id,
            "config": {"snapshot_path": str(FIXTURE_HOST_SNAPSHOT), "mode": "snapshot"},
        },
        headers=headers,
    )
    assert r.status_code == 200, r.text

    return {"srv": srv_id, "app": app_id, "db": db_id, "connector_id": j(r)["connector"]["id"]}


def test_autodiscover_scan_persists_draft_run(client: TestClient, auth_headers: dict):
    ids = _seed_autodiscover_chain(client, auth_headers)
    r = client.post(
        f"{API_V1}/autodiscover/scan",
        json={"server_ci_ids": [ids["srv"]], "scope_depth": 2, "scope_mode": "graph", "auto_apply": False},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    data = j(r)["scan"]
    assert data["run_id"] > 0
    assert data["status"] in ("completed", "partial")
    assert data["sources_ok"] >= 1
    assert data["fields_found"] >= 1
    assert data["discovered_schema"]["fields"]
    ip_mapping = next((m for m in data["mappings"] if m["field"] == "ip" and m["ci_id"] == ids["app"]), None)
    assert ip_mapping is not None
    assert ip_mapping["discovered_value"] == "10.0.0.10"
    assert ip_mapping["status"] == "auto"

    draft = client.get(f"{API_V1}/autodiscover/runs/{data['run_id']}", headers=auth_headers)
    assert draft.status_code == 200
    assert j(draft)["scan"]["run_id"] == data["run_id"]


def test_autodiscover_scan_without_connector_fails(client: TestClient, auth_headers: dict):
    types = get_type_map(client, auth_headers)
    r = client.post(
        f"{API_V1}/ci",
        json={
            "name": "orphan-srv",
            "type_id": types["Server"],
            "status": "active",
            "criticality": "high",
            "environment": "production",
            "owner": "ops",
            "external_ids": {"hostname": "orphan-srv"},
        },
        headers=auth_headers,
    )
    srv_id = ci(r.json())["id"]
    r = client.post(
        f"{API_V1}/autodiscover/scan",
        json={"server_ci_ids": [srv_id]},
        headers=auth_headers,
    )
    assert r.status_code == 400
    assert "No sync connectors" in r.json()["detail"]


def test_autodiscover_apply_writes_field_with_audit(client: TestClient, auth_headers: dict):
    ids = _seed_autodiscover_chain(client, auth_headers)
    scan = j(
        client.post(
            f"{API_V1}/autodiscover/scan",
            json={"server_ci_ids": [ids["srv"]], "scope_depth": 2, "scope_mode": "all", "auto_apply": False},
            headers=auth_headers,
        )
    )["scan"]
    ip_mapping = next(m for m in scan["mappings"] if m["field"] == "ip" and m["ci_id"] == ids["app"])
    r = client.post(
        f"{API_V1}/autodiscover/runs/{scan['run_id']}/apply",
        json={"mapping_ids": [ip_mapping["mapping_id"]]},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    assert j(r)["apply"]["applied"] == 1
    ci_data = ci(client.get(f"{API_V1}/ci/{ids['app']}", headers=auth_headers).json())
    assert ci_data["external_ids"].get("ip") == "10.0.0.10"


def test_autodiscover_discovers_relations(client: TestClient, auth_headers: dict):
    ids = _seed_autodiscover_chain(client, auth_headers)
    # Remove pre-created relations — autodiscover should propose them from inventory
    rels = items(client.get(f"{API_V1}/relations", headers=auth_headers).json())
    for rel in rels:
        if rel["source_ci_id"] == ids["app"]:
            client.delete(f"{API_V1}/relations/{rel['id']}", headers=auth_headers)

    scan = client.post(
        f"{API_V1}/autodiscover/scan",
        json={"server_ci_ids": [ids["srv"]], "scope_mode": "all", "discover_relations": True, "auto_apply": False},
        headers=auth_headers,
    )
    assert scan.status_code == 200, scan.text
    data = j(scan)["scan"]
    rel_mappings = [m for m in data["mappings"] if m["mapping_kind"] == "relation"]
    assert len(rel_mappings) >= 1
    hosted = next((m for m in rel_mappings if m["relation_type"] == "hosted_on"), None)
    assert hosted is not None
    assert hosted["discovered_value"] == "pay-srv-01"


def test_autodiscover_auto_applies_relations_on_first_run(client: TestClient, auth_headers: dict):
    types = get_type_map(client, auth_headers)

    def create_local_ci(name, type_name, **attrs):
        body = {
            "name": name,
            "type_id": types[type_name],
            "status": "active",
            "criticality": "high",
            "environment": "production",
            "owner": "ops",
            "attributes": attrs,
            "external_ids": {k: v for k, v in attrs.items() if k in ("hostname", "ip")},
        }
        r = client.post(f"{API_V1}/ci", json=body, headers=auth_headers)
        assert r.status_code == 200, r.text
        return ci(r.json())["id"]

    srv_id = create_local_ci("disc-srv", "Server", hostname="disc-srv", ip="10.0.0.99")
    client.post(
        f"{API_V1}/autodiscover/connectors",
        json={
            "name": "disc-host-inline",
            "connector_type": "host",
            "server_ci_id": srv_id,
            "config": {
                "mode": "snapshot",
                "snapshot": {
                    "host": {"hostname": "disc-srv", "ip": "10.0.0.99"},
                    "processes": [
                        {"hostname": "new-app", "entity_type": "Application", "container_name": "new-app"},
                        {"hostname": "new-db", "entity_type": "Database", "container_name": "new-db"},
                    ],
                    "connections": [
                        {
                            "source_hostname": "new-app",
                            "target_hostname": "new-db",
                            "relation_type": "depends_on",
                        }
                    ],
                },
            },
        },
        headers=auth_headers,
    )
    scan = client.post(
        f"{API_V1}/autodiscover/scan",
        json={"server_ci_ids": [srv_id], "scope_mode": "all", "auto_apply": True, "source_types": ["host"]},
        headers=auth_headers,
    )
    assert scan.status_code == 200, scan.text
    data = j(scan)["scan"]
    assert data["apply_result"]["applied_relations"] >= 1
    rels = items(client.get(f"{API_V1}/relations", headers=auth_headers).json())
    app = next(
        c for c in items(client.get(f"{API_V1}/ci?name=new-app", headers=auth_headers).json()) if c["name"] == "new-app"
    )
    db = next(
        c for c in items(client.get(f"{API_V1}/ci?name=new-db", headers=auth_headers).json()) if c["name"] == "new-db"
    )
    depends = [r for r in rels if r["source_ci_id"] == app["id"] and r["relation_type"] == "depends_on"]
    assert len(depends) == 1
    assert depends[0]["target_ci_id"] == db["id"]


def test_autodiscover_auto_apply_on_scan(client: TestClient, auth_headers: dict):
    ids = _seed_autodiscover_chain(client, auth_headers)
    scan = client.post(
        f"{API_V1}/autodiscover/scan",
        json={"server_ci_ids": [ids["srv"]], "scope_mode": "all", "auto_apply": True},
        headers=auth_headers,
    )
    assert scan.status_code == 200, scan.text
    data = j(scan)["scan"]
    assert data["apply_result"] is not None
    assert data["apply_result"]["applied"] >= 1
    ci_data = ci(client.get(f"{API_V1}/ci/{ids['app']}", headers=auth_headers).json())
    assert ci_data["external_ids"].get("ip") == "10.0.0.10"


def test_autodiscover_resolves_relation_target_by_ci_name(client: TestClient, auth_headers: dict):
    ids = _seed_autodiscover_chain(client, auth_headers)
    rels = items(client.get(f"{API_V1}/relations", headers=auth_headers).json())
    for rel in rels:
        if rel["source_ci_id"] == ids["app"] and rel["relation_type"] == "depends_on":
            client.delete(f"{API_V1}/relations/{rel['id']}", headers=auth_headers)

    scan = client.post(
        f"{API_V1}/autodiscover/scan",
        json={"server_ci_ids": [ids["srv"]], "scope_mode": "all", "auto_apply": True, "discover_relations": True},
        headers=auth_headers,
    )
    assert scan.status_code == 200, scan.text
    rels = items(client.get(f"{API_V1}/relations", headers=auth_headers).json())
    depends = [r for r in rels if r["source_ci_id"] == ids["app"] and r["relation_type"] == "depends_on"]
    assert len(depends) == 1
    assert depends[0]["target_ci_id"] == ids["db"]


def test_autodiscover_profiles_list(client: TestClient, auth_headers: dict):
    r = client.get(f"{API_V1}/autodiscover/profiles", headers=auth_headers)
    assert r.status_code == 200
    assert any(p["name"] == "default-sync" for p in items(r.json()))


def test_connector_auto_sync_and_sync_endpoint(client: TestClient, auth_headers: dict):
    ids = _seed_autodiscover_chain(client, auth_headers)
    r = client.post(
        f"{API_V1}/autodiscover/connectors",
        json={
            "name": "auto-sync-test-conn",
            "connector_type": "host",
            "server_ci_id": ids["srv"],
            "config": {"mode": "snapshot", "snapshot_path": str(FIXTURE_HOST_SNAPSHOT)},
            "enabled": True,
            "auto_sync": True,
        },
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    connector = j(r)["connector"]
    assert connector["auto_sync"] is True

    sync = client.post(f"{API_V1}/autodiscover/connectors/{connector['id']}/sync", headers=auth_headers)
    assert sync.status_code == 200, sync.text
    sync_data = j(sync)["sync"]
    assert sync_data["run_id"] > 0
    assert sync_data["status"] in ("completed", "partial", "failed")


def test_autodiscover_requires_editor(client: TestClient, auth_headers: dict):
    r = client.post(
        f"{API_V1}/auth/users",
        json={"email": "viewer@test.local", "password": "viewer123", "role": "viewer"},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    login = client.post(f"{API_V1}/auth/login", json={"email": "viewer@test.local", "password": "viewer123"})
    viewer_headers = {"Authorization": f"Bearer {j(login)['session']['access_token']}"}

    r = client.post(
        f"{API_V1}/autodiscover/scan",
        json={"server_ci_ids": [1]},
        headers=viewer_headers,
    )
    assert r.status_code == 403
