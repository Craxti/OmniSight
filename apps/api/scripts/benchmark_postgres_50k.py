#!/usr/bin/env python3
"""NFR benchmark on PostgreSQL with 50k CIs (§9). Run after seed_scale_50k.py."""

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


BASE = "http://127.0.0.1:8000"
LIMIT_MS = 200
MIN_CI = 45_000


def _login() -> str:
    req = urllib.request.Request(
        f"{BASE}/api/v1/auth/login",
        data=json.dumps({"email": "admin@omnisight.local", "password": "admin123"}).encode(),
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["session"]["access_token"]


def _timed(method: str, path: str, token: str, body: dict | None = None) -> tuple[dict, float]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {token}")
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.loads(resp.read())
    return payload, (time.perf_counter() - t0) * 1000


def main() -> int:
    from src.core.database import SessionLocal
    from src.models import CI

    db = SessionLocal()
    count = db.query(CI).filter(CI.is_deleted.is_(False)).count()
    db.close()
    print(f"CI count: {count}")
    if count < MIN_CI:
        print(f"WARN: expected ≥{MIN_CI} CIs — run: python scripts/seed_scale_50k.py")
        return 1

    token = _login()
    alerts = [{"hostname": "app-01"}, {"ip": "10.0.0.5"}]
    _, resolve_ms = _timed("POST", "/api/v1/resources/resolve", token, {"alerts": alerts, "page": 1, "page_size": 100})
    search_q = "/api/v1/resources/search?" + urllib.parse.urlencode({"hostname": "app-01"})
    _, search_ms = _timed("GET", search_q, token)

    ok = True
    for label, ms in [("resolve_v1", resolve_ms), ("search_indexed", search_ms)]:
        status = "OK" if ms < LIMIT_MS else "FAIL"
        print(f"{label}: {ms:.1f}ms [{status}] (limit {LIMIT_MS}ms, n={count})")
        if ms >= LIMIT_MS:
            ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
