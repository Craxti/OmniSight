# Demo Guide for Judges

**English** · [Русская версия](DEMO_GUIDE.ru.md)

Step-by-step demo scenario for OmniSight RSM on PAY demo data.  
Cheat sheet with talking points: [`PRESENTATION.md`](./PRESENTATION.md)

## Prerequisites

```powershell
# From repository root — UI + API + Demo CE
.\scripts\start-all.ps1
```

| Service | URL | Credentials |
|---------|-----|-------------|
| Web UI | http://localhost:5173 | `admin@omnisight.local` / `admin123` |
| API / Swagger | http://localhost:8000/docs | X-API-Key: `omnisight-api-key-dev` |
| Demo CE | http://localhost:8090 | — |

Demo model: **11 CIs**, **10 relations** (payment contour PAY).

---

## Part 1 — Platform overview (3 min)

1. Log in → **Overview** (`/`) — show KPI: 11 CIs, 10 relations, green model health.
2. **Inventory** (`/inventory`) — CI registry with external IDs (hostname, IP, serviceCode).
3. **Relations** (`/relations`) — all 7 relation types from the spec; click **Validate model**.
4. **Graph** (`/graph`) — select `demo-biz` or `demo-db`; show business path and impact panel.

**Key message:** OmniSight is not monitoring or a correlation engine — it is the **source of truth** for IT dependencies.

---

## Part 2 — Correlation scenario A: merge alerts (5 min)

**Question answered:** *Four alerts in one minute — one incident or four?*

1. Open **Correlation** (`/correlation`).
2. Enter 4 rows (one field each):

| Row | Field | Value | Maps to |
|-----|-------|-------|---------|
| 1 | hostname | `app-01` | demo-app |
| 2 | ip | `10.0.0.5` | demo-db |
| 3 | externalId | `ext-db-1` | demo-db |
| 4 | serviceCode + applicationCode | `PAY` + `PAY-APP` | demo-biz |

3. Click **Process** (Ingest).

**Expected result:**
- **Resolved = 4**
- **Chain related = true** (green)
- **Root cause zone** — `demo-db`
- Graph with highlighted chain

**For CE:** `chain_related: true` → merge into one INC.

---

## Part 3 — Correlation scenario B: do not merge (3 min)

**Question answered:** *Two alerts in the same contour — always one incident?*

1. Clear input, enter 2 rows (hostname only):

| Row | hostname | CI | Layer |
|-----|----------|-----|-------|
| 1 | `pay-srv-01` | demo-pay-srv | infrastructure (`hosted_on`) |
| 2 | `app-01` | demo-app | application (`depends_on` → DB) |

2. Click **Process**.

**Expected result:**
- **Resolved = 2**
- **Chain related = false** (yellow)
- No root cause zone block

**For CE:** `chain_related: false` → two separate INCs.

---

## Part 4 — Autodiscover (3 min)

**Problem:** `demo-app` has hostname but **no IP** — IP-only alerts won't resolve.

1. **Inventory** → open `demo-app` — confirm no IP.
2. **Autodiscover** → check **`demo-pay-srv`** → **Manual mode** → **Scan**.
3. **Fields** tab: `demo-app` / `ip` / **`10.0.0.10`**
4. **Relations** tab: `depends_on` → `demo-db` (if suggested).
5. **Apply selected** → IP appears on `demo-app`.
6. **Audit** (`/audit`) — record with diff.

**Key message:** model stays current without manual CMDB — human confirms server data.

---

## Part 5 — Demo CE integration (optional, 2 min)

1. Open http://localhost:8090
2. Send 4 test alerts → watch ingest result from RSM.
3. Show **Settings → API** in UI for `X-API-Key` and Swagger link.

---

## Checklist

- [ ] `seed_demo.py` run (PAY fixtures only)
- [ ] Login → Overview: **11 CIs**, green health
- [ ] Inventory and relations visible (`demo_pay_*.import.json`)
- [ ] **A:** 4 rows → Resolved **4**, Chain related **true**, zone **`demo-db`**
- [ ] **B:** `pay-srv-01` + `app-01` → Resolved **2**, Chain related **false**
- [ ] **Autodiscover:** `demo-app.ip` = `10.0.0.10`

---

## Acceptance verification

```powershell
cd apps\api
python scripts\verify_demo_acceptance.py   # expected 20/20 PASS
```

See also: [`../docs/REQUIREMENTS_MAPPING.md`](../docs/REQUIREMENTS_MAPPING.md) · [`WINDOWS_SETUP.md`](./WINDOWS_SETUP.md)
