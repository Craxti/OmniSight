from fastapi.testclient import TestClient

from tests.seed_helpers import find_ci_id_by_name
from tests.test_rsm_api import _seed_chain
from tests.v1_helpers import API_V1, ci, items


def test_v1_resolve_pagination(client: TestClient, auth_headers: dict):
    _seed_chain(client, auth_headers)
    alerts = [{"hostname": "app-01"}, {"ip": "10.0.0.5"}, {"externalId": "ext-db-1"}]
    r = client.post(
        f"{API_V1}/resources/resolve",
        json={"alerts": alerts, "page": 1, "page_size": 2},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["api_version"] == "v1"
    assert body["pagination"]["page"] == 1
    assert body["pagination"]["page_size"] == 2
    assert body["pagination"]["total_items"] == 3
    assert len(body["resolved"]) + len(body["unresolved"]) == 2


def test_v1_ingest_chain_algorithm(client: TestClient, auth_headers: dict):
    _seed_chain(client, auth_headers)
    r = client.post(
        f"{API_V1}/correlation/ingest",
        json={
            "alerts": [
                {"hostname": "app-01"},
                {"ip": "10.0.0.5"},
                {"externalId": "ext-db-1"},
                {"serviceCode": "PAY", "applicationCode": "PAY-APP"},
            ],
            "source": "test",
            "page": 1,
            "page_size": 100,
        },
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["api_version"] == "v1"
    assert body["correlation"]["chain_related"] is True
    assert body["correlation"]["chain_algorithm"] == "depends_on_directed"
    assert body.get("ingest_log_id") is not None

    logs = client.get(f"{API_V1}/correlation/ingest-logs", headers=auth_headers)
    assert logs.status_code == 200, logs.text
    logs_body = logs.json()
    assert logs_body["pagination"]["total_items"] >= 1
    assert any(item["source"] == "test" for item in logs_body["items"])

    log_id = body["ingest_log_id"]
    detail = client.get(f"{API_V1}/correlation/ingest-logs/{log_id}", headers=auth_headers)
    assert detail.status_code == 200, detail.text
    detail_body = detail.json()
    assert detail_body["ingest_log"]["id"] == log_id
    assert len(detail_body["ingest_log"]["alerts"]) == 4
    assert detail_body["ingest_log"]["result"]["correlation"]["chain_related"] is True


def test_v1_ci_list_pagination(client: TestClient, auth_headers: dict):
    r = client.get(f"{API_V1}/ci", params={"page": 1, "page_size": 5}, headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["api_version"] == "v1"
    assert body["schema_version"] == "rsm-inventory-v1"
    assert "items" in body
    assert body["pagination"]["page"] == 1
    assert body["pagination"]["page_size"] == 5


def test_v1_relations_list_pagination(client: TestClient, auth_headers: dict):
    _seed_chain(client, auth_headers)
    r = client.get(f"{API_V1}/relations", params={"page": 1, "page_size": 2}, headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["api_version"] == "v1"
    assert body["pagination"]["total_items"] >= 2
    assert len(body["items"]) <= 2


def test_v1_ci_detail_envelope(client: TestClient, auth_headers: dict):
    ci_id = find_ci_id_by_name(client, auth_headers, "v1-detail-ci")
    if ci_id is None:
        created = client.post(
            f"{API_V1}/ci",
            json={"name": "v1-detail-ci", "type_name": "Server", "status": "active"},
            headers=auth_headers,
        )
        assert created.status_code == 200, created.text
        ci_id = ci(created.json())["id"]

    r = client.get(f"{API_V1}/ci/{ci_id}", headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["api_version"] == "v1"
    assert body["schema_version"] == "rsm-inventory-v1"
    assert body["ci"]["name"] == "v1-detail-ci"


def test_v1_relation_detail_envelope(client: TestClient, auth_headers: dict):
    _seed_chain(client, auth_headers)
    listed = client.get(f"{API_V1}/relations", headers=auth_headers)
    assert listed.status_code == 200, listed.text
    relation_id = items(listed.json())[0]["id"]

    r = client.get(f"{API_V1}/relations/{relation_id}", headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["api_version"] == "v1"
    assert body["relation"]["id"] == relation_id


def test_v1_ci_crud_envelopes(client: TestClient, auth_headers: dict):
    created = client.post(
        f"{API_V1}/ci",
        json={"name": "v1-crud-ci", "type_name": "Server", "status": "active"},
        headers=auth_headers,
    )
    assert created.status_code == 200, created.text
    body = created.json()
    assert body["api_version"] == "v1"
    ci_id = body["ci"]["id"]

    updated = client.patch(
        f"{API_V1}/ci/{ci_id}",
        json={"owner": "v1-team"},
        headers=auth_headers,
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["ci"]["owner"] == "v1-team"

    deleted = client.delete(f"{API_V1}/ci/{ci_id}", headers=auth_headers)
    assert deleted.status_code == 200, deleted.text
    assert deleted.json()["result"]["ok"] is True


def test_v1_relations_validate_and_mutations(client: TestClient, auth_headers: dict):
    _seed_chain(client, auth_headers)

    validate = client.get(f"{API_V1}/relations/validate", headers=auth_headers)
    assert validate.status_code == 200, validate.text
    vbody = validate.json()
    assert vbody["api_version"] == "v1"
    assert "validation" in vbody
    assert "valid" in vbody["validation"]

    source_id = find_ci_id_by_name(client, auth_headers, "demo-app")
    target_id = find_ci_id_by_name(client, auth_headers, "demo-db")
    assert source_id is not None and target_id is not None

    created = client.post(
        f"{API_V1}/relations",
        json={
            "source_ci_id": source_id,
            "target_ci_id": target_id,
            "relation_type": "uses",
            "status": "active",
        },
        headers=auth_headers,
    )
    assert created.status_code == 200, created.text
    relation_id = created.json()["relation"]["id"]

    patched = client.patch(
        f"{API_V1}/relations/{relation_id}",
        json={"status": "inactive"},
        headers=auth_headers,
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["relation"]["status"] == "inactive"

    deleted = client.delete(f"{API_V1}/relations/{relation_id}", headers=auth_headers)
    assert deleted.status_code == 200, deleted.text
    assert deleted.json()["result"]["ok"] is True


def test_v1_ci_recycle_bin_restore_purge_bulk(client: TestClient, auth_headers: dict):
    created = client.post(
        f"{API_V1}/ci",
        json={"name": "v1-recycle-ci", "type_name": "Server", "status": "active"},
        headers=auth_headers,
    )
    ci_id = created.json()["ci"]["id"]

    deleted = client.delete(f"{API_V1}/ci/{ci_id}", headers=auth_headers)
    assert deleted.status_code == 200, deleted.text

    recycle = client.get(f"{API_V1}/ci/recycle-bin", headers=auth_headers)
    assert recycle.status_code == 200, recycle.text
    rbody = recycle.json()
    assert rbody["api_version"] == "v1"
    assert any(item["id"] == ci_id for item in rbody["items"])

    restored = client.post(f"{API_V1}/ci/{ci_id}/restore", headers=auth_headers)
    assert restored.status_code == 200, restored.text
    assert restored.json()["ci"]["status"] == "active"

    bulk = client.post(
        f"{API_V1}/ci/bulk/status",
        json={"ci_ids": [ci_id], "status": "temporarily_disabled"},
        headers=auth_headers,
    )
    assert bulk.status_code == 200, bulk.text
    assert bulk.json()["result"]["updated"] == 1

    client.delete(f"{API_V1}/ci/{ci_id}", headers=auth_headers)
    purged = client.delete(f"{API_V1}/ci/{ci_id}/purge", headers=auth_headers)
    assert purged.status_code == 200, purged.text
    assert purged.json()["result"]["ok"] is True


def test_v1_relations_list_filters_by_source_name(client: TestClient, auth_headers: dict):
    _seed_chain(client, auth_headers)
    r = client.get(
        f"{API_V1}/relations",
        params={"page": 1, "page_size": 10, "source_name": "demo-app"},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["pagination"]["total_items"] >= 1
    assert all(item["source_name"] == "demo-app" for item in body["items"])


def test_v1_ci_relations_envelope(client: TestClient, auth_headers: dict):
    _seed_chain(client, auth_headers)
    app_id = find_ci_id_by_name(client, auth_headers, "demo-app")
    assert app_id is not None

    r = client.get(f"{API_V1}/ci/{app_id}/relations", headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["api_version"] == "v1"
    assert len(body["items"]) >= 1


def test_v1_ci_import_preview_envelope(client: TestClient, auth_headers: dict):
    r = client.post(f"{API_V1}/ci/import/preview", json=[], headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["api_version"] == "v1"
    assert body["schema_version"] == "rsm-inventory-v1"
    assert "export" in body
    assert "needs_mapping" in body["export"]


def test_v1_ci_export_full_envelope(client: TestClient, auth_headers: dict):
    r = client.get(f"{API_V1}/ci/export/full", headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["api_version"] == "v1"
    assert "export" in body


def test_v1_ci_types_list_envelope(client: TestClient, auth_headers: dict):
    r = client.get(f"{API_V1}/ci/types", headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["api_version"] == "v1"
    assert body["schema_version"] == "rsm-inventory-v1"
    assert isinstance(body["items"], list)
    assert body["pagination"]["total_items"] >= 1


def test_v1_ci_type_crud_envelope(client: TestClient, auth_headers: dict):
    created = client.post(
        f"{API_V1}/ci/types",
        json={"name": "v1-type-test", "description": "test"},
        headers=auth_headers,
    )
    assert created.status_code == 200, created.text
    body = created.json()
    assert body["api_version"] == "v1"
    type_id = body["ci_type"]["id"]

    patched = client.patch(
        f"{API_V1}/ci/types/{type_id}",
        json={"description": "updated"},
        headers=auth_headers,
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["ci_type"]["description"] == "updated"

    deleted = client.delete(f"{API_V1}/ci/types/{type_id}", headers=auth_headers)
    assert deleted.status_code == 200, deleted.text
    assert deleted.json()["result"]["ok"] is True


def test_v1_relation_types_list_envelope(client: TestClient, auth_headers: dict):
    r = client.get(f"{API_V1}/relation/types", headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["api_version"] == "v1"
    assert body["schema_version"] == "rsm-inventory-v1"
    assert isinstance(body["items"], list)
    assert body["pagination"]["total_items"] >= 1
    assert any(item["name"] == "depends_on" for item in body["items"])


def test_v1_relation_type_crud_envelope(client: TestClient, auth_headers: dict):
    created = client.post(
        f"{API_V1}/relation/types",
        json={"name": "custom_monitors", "description": "Monitors dependency"},
        headers=auth_headers,
    )
    assert created.status_code == 200, created.text
    body = created.json()
    assert body["api_version"] == "v1"
    type_id = body["relation_type"]["id"]

    patched = client.patch(
        f"{API_V1}/relation/types/{type_id}",
        json={"description": "updated"},
        headers=auth_headers,
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["relation_type"]["description"] == "updated"

    meta = client.get(f"{API_V1}/meta/constants", headers=auth_headers)
    assert "custom_monitors" in meta.json()["constants"]["relation_types"]

    deleted = client.delete(f"{API_V1}/relation/types/{type_id}", headers=auth_headers)
    assert deleted.status_code == 200, deleted.text
    assert deleted.json()["result"]["ok"] is True


def test_v1_resource_graph_envelope(client: TestClient, auth_headers: dict):
    _seed_chain(client, auth_headers)
    root_id = find_ci_id_by_name(client, auth_headers, "demo-app")
    assert root_id is not None

    r = client.get(f"{API_V1}/resources/{root_id}/graph", params={"depth": 2}, headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["api_version"] == "v1"
    assert body["schema_version"] == "rsm-topology-v1"
    assert body["graph"]["root_id"] == root_id
    assert len(body["graph"]["nodes"]) >= 1


def test_v1_resource_search_envelope(client: TestClient, auth_headers: dict):
    _seed_chain(client, auth_headers)
    r = client.get(f"{API_V1}/resources/search", params={"hostname": "app-01"}, headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["api_version"] == "v1"
    assert body["schema_version"] == "rsm-inventory-v1"
    assert body["search"]["total"] >= 1
    assert body["search"]["items"][0]["name"] == "demo-app"


def test_v1_meta_constants_envelope(client: TestClient, auth_headers: dict):
    r = client.get(f"{API_V1}/meta/constants", headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["api_version"] == "v1"
    assert body["schema_version"] == "rsm-meta-v1"
    assert "relation_types" in body["constants"]
    assert "depends_on" in body["constants"]["relation_types"]


def test_v1_dashboard_envelope(client: TestClient, auth_headers: dict):
    r = client.get(f"{API_V1}/dashboard/overview", headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["api_version"] == "v1"
    assert body["schema_version"] == "rsm-ops-v1"
    assert "model_health" in body["dashboard"]
    assert "recent_audit" in body["dashboard"]


def test_v1_audit_list_envelope(client: TestClient, auth_headers: dict):
    r = client.get(f"{API_V1}/audit", params={"page": 1, "page_size": 10}, headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["api_version"] == "v1"
    assert body["schema_version"] == "rsm-ops-v1"
    assert "items" in body
    assert body["pagination"]["page"] == 1


def test_api_key_uses_integration_user_not_admin(client: TestClient, auth_headers: dict):
    from src.core.config import settings

    r = client.get(f"{API_V1}/auth/me", headers={"X-API-Key": settings.api_key})
    assert r.status_code == 200, r.text
    user = r.json()["user"]
    assert user["email"] == "integration@omnisight.local"
    assert user["role"] == "viewer"


def test_v1_autodiscover_profiles_envelope(client: TestClient, auth_headers: dict):
    r = client.get(f"{API_V1}/autodiscover/profiles", headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["api_version"] == "v1"
    assert body["schema_version"] == "rsm-autodiscover-v1"
    assert isinstance(body["items"], list)
    assert body["pagination"]["total_items"] >= 1


def test_v1_auth_me_envelope(client: TestClient, auth_headers: dict):
    r = client.get(f"{API_V1}/auth/me", headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["api_version"] == "v1"
    assert body["schema_version"] == "rsm-auth-v1"
    assert body["user"]["email"] == "admin@omnisight.local"


def test_v1_auth_login_envelope(client: TestClient):
    r = client.post(
        f"{API_V1}/auth/login",
        json={"email": "admin@omnisight.local", "password": "admin123"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["api_version"] == "v1"
    assert body["schema_version"] == "rsm-auth-v1"
    assert body["session"]["access_token"]


def test_v1_ci_export_csv(client: TestClient, auth_headers: dict):
    r = client.get(f"{API_V1}/ci/export/csv", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert "zip" in r.headers.get("content-type", "").lower() or r.content[:2] == b"PK"


def test_v1_routes_no_deprecation_headers(client: TestClient, auth_headers: dict):
    for path in (f"{API_V1}/ci", f"{API_V1}/meta/constants", f"{API_V1}/dashboard/overview"):
        r = client.get(path, headers=auth_headers)
        assert r.status_code == 200, r.text
        assert r.headers.get("Deprecation") is None
        assert r.headers.get("Sunset") is None
