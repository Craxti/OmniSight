"""Auth and user-management integration tests."""

from fastapi.testclient import TestClient

from tests.v1_helpers import API_V1, items, j


def test_auth_token_issues_jwt(client: TestClient):
    r = client.post(
        f"{API_V1}/auth/token",
        json={"email": "admin@omnisight.local", "password": "admin123"},
    )
    assert r.status_code == 200, r.text
    token = j(r)["session"]["access_token"]
    me = client.get(f"{API_V1}/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert j(me)["user"]["email"] == "admin@omnisight.local"


def test_viewer_cannot_create_ci(client: TestClient, auth_headers: dict):
    client.post(
        f"{API_V1}/auth/users",
        json={"email": "viewer@test.local", "password": "viewer123", "role": "viewer"},
        headers=auth_headers,
    )
    r = client.post(f"{API_V1}/auth/login", json={"email": "viewer@test.local", "password": "viewer123"})
    viewer_headers = {"Authorization": f"Bearer {j(r)['session']['access_token']}"}
    r = client.post(f"{API_V1}/ci", json={"name": "blocked", "type_name": "Server"}, headers=viewer_headers)
    assert r.status_code == 403


def test_create_user_and_reset_set_must_change_password(client: TestClient, auth_headers: dict):
    r = client.post(
        f"{API_V1}/auth/users",
        json={"email": "pwuser@test.local", "password": "tempPass1", "role": "viewer"},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    assert j(r)["user"]["must_change_password"] is True

    r = client.post(f"{API_V1}/auth/login", json={"email": "pwuser@test.local", "password": "tempPass1"})
    assert r.status_code == 200, r.text
    session = j(r)["session"]
    assert session["must_change_password"] is True
    user_headers = {"Authorization": f"Bearer {session['access_token']}"}

    r = client.get(f"{API_V1}/auth/me", headers=user_headers)
    assert r.status_code == 200
    assert j(r)["user"]["must_change_password"] is True

    r = client.post(
        f"{API_V1}/auth/change-password",
        json={"current_password": "tempPass1", "new_password": "newPass99"},
        headers=user_headers,
    )
    assert r.status_code == 200, r.text

    r = client.get(f"{API_V1}/auth/me", headers=user_headers)
    assert j(r)["user"]["must_change_password"] is False

    r = client.post(f"{API_V1}/auth/login", json={"email": "pwuser@test.local", "password": "newPass99"})
    assert r.status_code == 200
    assert j(r)["session"]["must_change_password"] is False

    r = client.post(
        f"{API_V1}/auth/users/pwuser@test.local/reset-password",
        json={"password": "resetPass1"},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text

    r = client.post(f"{API_V1}/auth/login", json={"email": "pwuser@test.local", "password": "resetPass1"})
    assert r.status_code == 200
    assert j(r)["session"]["must_change_password"] is True


def test_deactivate_and_delete_user(client: TestClient, auth_headers: dict):
    r = client.post(
        f"{API_V1}/auth/users",
        json={"email": "todelete@test.local", "password": "tempPass1", "role": "viewer"},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text

    r = client.patch(
        f"{API_V1}/auth/users/todelete@test.local/active",
        json={"is_active": False},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    assert j(r)["user"]["is_active"] is False

    r = client.post(f"{API_V1}/auth/login", json={"email": "todelete@test.local", "password": "tempPass1"})
    assert r.status_code == 401

    r = client.patch(
        f"{API_V1}/auth/users/todelete@test.local/active",
        json={"is_active": True},
        headers=auth_headers,
    )
    assert r.status_code == 200
    login = client.post(f"{API_V1}/auth/login", json={"email": "todelete@test.local", "password": "tempPass1"})
    assert login.status_code == 200
    user_headers = {"Authorization": f"Bearer {j(login)['session']['access_token']}"}

    r = client.patch(
        f"{API_V1}/auth/users/todelete@test.local/active",
        json={"is_active": False},
        headers=auth_headers,
    )
    assert r.status_code == 200

    r = client.get(f"{API_V1}/auth/me", headers=user_headers)
    assert r.status_code == 401

    r = client.patch(
        f"{API_V1}/auth/users/todelete@test.local/active",
        json={"is_active": True},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert j(r)["user"]["is_active"] is True

    r = client.delete(f"{API_V1}/auth/users/todelete@test.local", headers=auth_headers)
    assert r.status_code == 200, r.text

    r = client.get(f"{API_V1}/auth/users", headers=auth_headers)
    emails = [u["email"] for u in items(r.json())]
    assert "todelete@test.local" not in emails


def test_cannot_delete_or_deactivate_self(client: TestClient, auth_headers: dict):
    r = client.patch(
        f"{API_V1}/auth/users/admin@omnisight.local/active",
        json={"is_active": False},
        headers=auth_headers,
    )
    assert r.status_code == 400

    r = client.delete(f"{API_V1}/auth/users/admin@omnisight.local", headers=auth_headers)
    assert r.status_code == 400


def test_editor_cannot_manage_users_or_types(client: TestClient, auth_headers: dict):
    client.post(
        f"{API_V1}/auth/users",
        json={"email": "editor@test.local", "password": "editor123", "role": "editor"},
        headers=auth_headers,
    )
    r = client.post(f"{API_V1}/auth/login", json={"email": "editor@test.local", "password": "editor123"})
    editor_headers = {"Authorization": f"Bearer {j(r)['session']['access_token']}"}

    r = client.post(
        f"{API_V1}/auth/users",
        json={"email": "blocked@test.local", "password": "x", "role": "viewer"},
        headers=editor_headers,
    )
    assert r.status_code == 403

    r = client.post(
        f"{API_V1}/ci/types",
        json={"name": "CustomType", "description": "test"},
        headers=editor_headers,
    )
    assert r.status_code == 403


def test_editor_cannot_import(client: TestClient, auth_headers: dict):
    client.post(
        f"{API_V1}/auth/users",
        json={"email": "editor-import@test.local", "password": "editor123", "role": "editor"},
        headers=auth_headers,
    )
    r = client.post(f"{API_V1}/auth/login", json={"email": "editor-import@test.local", "password": "editor123"})
    editor_headers = {"Authorization": f"Bearer {j(r)['session']['access_token']}"}
    r = client.post(
        f"{API_V1}/ci/import",
        json=[{"name": "import-blocked", "type_name": "Server"}],
        headers=editor_headers,
    )
    assert r.status_code == 403
