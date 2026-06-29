from src.models import SyncConnector
from src.services.autodiscover.credentials import auth_headers, resolve_secret


def test_resolve_secret_from_env(monkeypatch):
    monkeypatch.setenv("SYNC_TEST_PASSWORD", "s3cret")
    assert resolve_secret(None, env_key="SYNC_TEST_PASSWORD") == "s3cret"


def test_api_key_auth_header():
    connector = SyncConnector(
        name="t",
        connector_type="api",
        config={"url": "http://example"},
        credentials={"auth_type": "api_key", "api_key": "abc", "api_key_header": "X-Custom-Key"},
    )
    headers = auth_headers(connector)
    assert headers["X-Custom-Key"] == "abc"
