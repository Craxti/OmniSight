#!/usr/bin/env python3
"""NFR benchmark: resolve + search should complete within 200ms (§9, local API)."""

import json
import sys
import time
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8000"
API = "/api/v1"
LIMIT_MS = 200


def post(path: str, body: dict, token: str) -> tuple[dict, float]:
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {token}")
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=10) as resp:
        payload = json.loads(resp.read())
    return payload, (time.perf_counter() - t0) * 1000


def get(path: str, token: str) -> tuple[dict, float]:
    req = urllib.request.Request(f"{BASE}{path}")
    req.add_header("Authorization", f"Bearer {token}")
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=10) as resp:
        payload = json.loads(resp.read())
    return payload, (time.perf_counter() - t0) * 1000


def main() -> int:
    login_req = urllib.request.Request(
        f"{BASE}{API}/auth/login",
        data=json.dumps({"email": "admin@omnisight.local", "password": "admin123"}).encode(),
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(login_req, timeout=10) as resp:
        token = json.loads(resp.read())["session"]["access_token"]
    alerts = [{"hostname": "app-01"}, {"ip": "10.0.0.5"}]

    _, resolve_ms = post(f"{API}/resources/resolve", {"alerts": alerts}, token)
    search_path = f"{API}/resources/search?" + urllib.parse.urlencode({"hostname": "app-01"})
    body, search_ms = get(search_path, token)

    ok = True
    for label, ms in [("resolve", resolve_ms), ("search", search_ms)]:
        status = "OK" if ms < LIMIT_MS else "FAIL"
        print(f"{label}: {ms:.1f}ms [{status}] (limit {LIMIT_MS}ms)")
        if ms >= LIMIT_MS:
            ok = False

    if body.get("search", {}).get("total", 0) < 1:
        print("WARN: no CI matched hostname=app-01 — run seed_demo.py first")
        return 1
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
