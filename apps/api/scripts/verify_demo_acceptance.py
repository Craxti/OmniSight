#!/usr/bin/env python3
"""Acceptance checklist against running API (FR 1–54, §8)."""

import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"
API = "/api/v1"


def req(method: str, path: str, body: dict | None = None, token: str | None = None) -> tuple[int, object]:
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(f"{BASE}{path}", data=data, method=method)
    if body is not None:
        request.add_header("Content-Type", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=15) as resp:
        return resp.status, json.loads(resp.read())


def main() -> int:
    results: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        results.append((name, ok, detail))
        status = "PASS" if ok else "FAIL"
        suffix = f" | {detail}" if detail else ""
        print(f"{status} | {name}{suffix}")

    status, health = req("GET", "/health")
    check("Health", status == 200 and health.get("status") == "ok", str(health))

    _, login = req("POST", f"{API}/auth/login", {"email": "admin@omnisight.local", "password": "admin123"})
    token = login["session"]["access_token"]

    _, ci_page = req("GET", f"{API}/ci?page=1&page_size=100", token=token)
    ci_list = ci_page["items"]
    names = {c["name"] for c in ci_list}
    check("FR1-10 demo CIs", {"demo-db", "demo-app", "demo-biz"}.issubset(names), f"count={len(ci_list)}")

    demo_db = next(c for c in ci_list if c["name"] == "demo-db")
    _, card = req("GET", f"{API}/resources/{demo_db['id']}", token=token)
    card_ci = card["ci"]
    check("FR10 card (§8 resources)", card_ci["name"] == "demo-db" and "external_ids" in card_ci)

    _, direct_rels = req("GET", f"{API}/resources/{demo_db['id']}/relations", token=token)
    check("FR33 relations (§8 resources)", len(direct_rels.get("items", [])) >= 1)

    _, types = req("GET", f"{API}/ci/types", token=token)
    check("FR2 eleven types", len(types["items"]) >= 11, f"types={len(types['items'])}")

    _, rels = req("GET", f"{API}/relations", token=token)
    check("FR11-14 relations", len(rels["items"]) >= 2)

    _, val = req("GET", f"{API}/relations/validate", token=token)
    validation = val["validation"]
    check("FR19 validate seed", validation.get("valid") is True, str(validation.get("issues", [])))

    _, graph = req("GET", f"{API}/resources/{demo_db['id']}/graph?depth=3", token=token)
    graph_data = graph["graph"]
    check("FR15-16 graph", len(graph_data.get("nodes", [])) >= 3, f"nodes={len(graph_data.get('nodes', []))}")

    _, impact = req("GET", f"{API}/resources/{demo_db['id']}/impact", token=token)
    impact_data = impact["impact"]
    impacted = impact_data.get("impacted_business_services") or impact_data.get("business_services") or []
    check("FR17 impact", len(impacted) >= 1, f"count={len(impacted)}")

    demo_biz = next(c for c in ci_list if c["name"] == "demo-biz")
    _, components = req("GET", f"{API}/resources/{demo_biz['id']}/components", token=token)
    comps = components["components"].get("components", [])
    check("FR36 components API", len(comps) >= 1, f"count={len(comps)}")

    _, full = req("GET", f"{API}/ci/export/full", token=token)
    export = full["export"]
    check(
        "FR25 export full",
        "elements" in export and "relations" in export,
        f"el={len(export['elements'])} rel={len(export['relations'])}",
    )

    import io
    import json
    import urllib.request as ur
    import zipfile

    xlsx_req = urllib.request.Request(f"{BASE}{API}/ci/export/xlsx?environment=production", method="GET")
    xlsx_req.add_header("Authorization", f"Bearer {token}")
    with ur.urlopen(xlsx_req, timeout=15) as resp:
        check("FR26-28 XLSX filtered", resp.status == 200 and "spreadsheet" in resp.headers.get("Content-Type", ""))

    zip_req = urllib.request.Request(f"{BASE}{API}/ci/export/csv", method="GET")
    zip_req.add_header("Authorization", f"Bearer {token}")
    with ur.urlopen(zip_req, timeout=15) as resp:
        data = resp.read()
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            manifest = json.loads(zf.read("manifest.json"))
            check(
                "FR28 CSV zip relations",
                "elements.csv" in zf.namelist() and manifest.get("relation_count", 0) >= 1,
                f"relations={manifest.get('relation_count')}",
            )

    alerts = [
        {"hostname": "app-01"},
        {"ip": "10.0.0.5"},
        {"externalId": "ext-db-1"},
        {"serviceCode": "PAY", "applicationCode": "PAY-APP"},
    ]
    _, ingest = req("POST", f"{API}/correlation/ingest", {"alerts": alerts, "source": "acceptance"}, token=token)
    check(
        "FR37-39 ingest",
        len(ingest["resolve"]["resolved"]) == 4 and ingest["correlation"]["chain_related"] is True,
    )

    _, search = req("GET", f"{API}/resources/search?hostname=app-01", token=token)
    check("FR31 search hostname", search["search"].get("total", 0) >= 1)

    _, search_owner = req("GET", f"{API}/resources/search?owner=ops", token=token)
    check("FR31 search owner", search_owner["search"].get("total", 0) >= 1)

    db_id = demo_db["id"]
    app_id = next(c["id"] for c in ci_list if c["name"] == "demo-app")
    pay_it_id = next(c["id"] for c in ci_list if c["name"] == "demo-pay-it")
    biz_id = demo_biz["id"]
    _, chain = req(
        "POST",
        f"{API}/correlation/chain-check",
        {"resource_ids": [db_id, app_id, pay_it_id, biz_id]},
        token=token,
    )
    check("FR39 chain-check", chain.get("chain_related") is True, f"ids={[db_id, app_id, pay_it_id, biz_id]}")

    editor_email = "accept-editor@test.local"
    try:
        req(
            "POST", f"{API}/auth/users", {"email": editor_email, "password": "editor123", "role": "editor"}, token=token
        )
    except urllib.error.HTTPError as e:
        if e.code != 409:
            raise
    _, elogin = req("POST", f"{API}/auth/login", {"email": editor_email, "password": "editor123"})
    editor_token = elogin["session"]["access_token"]
    try:
        req("POST", f"{API}/ci/import", [{"name": "blocked-import", "type_name": "Server"}], token=editor_token)
        check("FR54 editor import 403", False, "expected 403")
    except urllib.error.HTTPError as e:
        check("FR54 editor import 403", e.code == 403, f"code={e.code}")

    _, audit_page = req("GET", f"{API}/audit?page=1&page_size=5", token=token)
    audit_len = audit_page["pagination"].get("total_items", len(audit_page.get("items", [])))
    check("FR44-49 audit", audit_len >= 1, f"entries={audit_len}")

    viewer_email = "accept-viewer@test.local"
    try:
        req(
            "POST", f"{API}/auth/users", {"email": viewer_email, "password": "viewer123", "role": "viewer"}, token=token
        )
    except urllib.error.HTTPError as e:
        if e.code != 409:
            raise
    _, vlogin = req("POST", f"{API}/auth/login", {"email": viewer_email, "password": "viewer123"})
    viewer_token = vlogin["session"]["access_token"]
    try:
        req("POST", f"{API}/ci", {"name": "blocked-ci", "type_name": "Server"}, token=viewer_token)
        check("FR52 viewer 403", False, "expected 403")
    except urllib.error.HTTPError as e:
        check("FR52 viewer 403", e.code == 403, f"code={e.code}")

    with urllib.request.urlopen(f"{BASE}/openapi.json", timeout=10) as resp:
        check("FR43 OpenAPI", resp.status == 200)

    failed = [r for r in results if not r[1]]
    print("---")
    print(f"Total: {len(results)}, passed: {len(results) - len(failed)}, failed: {len(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
