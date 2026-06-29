#!/usr/bin/env python3
"""Verify RSM correlation flow against running API (default http://127.0.0.1:8000)."""

import json
import sys
import urllib.request

BASE = "http://127.0.0.1:8000"
API = "/api/v1"


def post(path: str, body: dict, token: str | None = None) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def get_token() -> str:
    body = post(f"{API}/auth/login", {"email": "admin@omnisight.local", "password": "admin123"})
    return body["session"]["access_token"]


def main() -> int:
    token = get_token()
    alerts = [
        {"hostname": "app-01"},
        {"ip": "10.0.0.5"},
        {"externalId": "ext-db-1"},
        {"serviceCode": "PAY", "applicationCode": "PAY-APP"},
    ]
    result = post(f"{API}/correlation/ingest", {"alerts": alerts, "source": "verify-script"}, token)
    resolved = len(result.get("resolve", {}).get("resolved", []))
    chain = result.get("correlation", {}).get("chain_related")
    print(f"resolved={resolved} chain_related={chain}")
    if resolved < 4:
        print("FAIL: expected 4 resolved alerts (run seed_demo.py first)")
        return 1
    if not chain:
        print("FAIL: expected chain_related=True")
        return 1
    print("OK: correlation flow verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
