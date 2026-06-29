"""NFR scale tests — PostgreSQL 50k (§9)."""

import time

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.usefixtures("scale_database_seeded")

NFR_MAX_MS = 200


def test_nfr_resolve_search_50k_postgres(client: TestClient, auth_headers: dict):
    from src.core.database import SessionLocal
    from src.models import CI

    db = SessionLocal()
    count = db.query(CI).filter(CI.is_deleted.is_(False)).count()
    db.close()
    assert count >= 45_000, f"Run seed_scale_50k.py first (got {count} CIs)"

    t0 = time.perf_counter()
    r = client.post(
        "/api/v1/resources/resolve",
        json={"alerts": [{"hostname": "app-01"}], "page": 1, "page_size": 50},
        headers=auth_headers,
    )
    resolve_ms = (time.perf_counter() - t0) * 1000
    assert r.status_code == 200, r.text
    assert resolve_ms < NFR_MAX_MS, f"resolve {resolve_ms:.1f}ms on {count} CIs"

    t0 = time.perf_counter()
    r = client.get("/api/v1/resources/search", params={"hostname": "app-01"}, headers=auth_headers)
    search_ms = (time.perf_counter() - t0) * 1000
    assert r.status_code == 200, r.text
    assert search_ms < NFR_MAX_MS, f"search {search_ms:.1f}ms on {count} CIs"
