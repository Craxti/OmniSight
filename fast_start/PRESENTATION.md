# OmniSight RSM — Demo Cheat Sheet (on demo data)

**English** · [Русская версия](ПРЕЗЕНТАЦИЯ.md)

## 1. What the system is and how it differs from "the other one"

**OmniSight RSM** (Resource-Service Model) — **a living map of the IT landscape**: a catalog of configuration items (CIs) — servers, DBs, applications, business services, etc. — and directed relationships between them (`depends_on`, `hosted_on`, etc.). On the map you can see **who depends on whom** and how a node failure affects the business. Each CI has external identifiers (hostname, IP, serviceCode) that alerts from different monitoring systems use to find the same node.

This is **not** Zabbix/Prometheus (they send metrics) and **not** a correlation engine (it decides whether to merge tickets). RSM answers different questions:

- Alert with hostname and alert with IP — **the same node**?
- DB went down — **which business service** is affected?
- Four alerts in a minute — **one incident** or four?

**How it beats a classic CMDB / Excel:**

| Excel / CMDB | OmniSight |
|---|---|
| Everything entered and edited by hand | **Correlation** — a batch of alerts is immediately checked against a ready-made map |
| Map goes stale (IP changed — model lies) | **Autodiscover** — IP and relationships are pulled from the server, a person confirms |
| CE and on-call engineer match fields themselves | One current model for everyone via **API** |

**Main value:** not a pretty UI, but **confidence during an incident** — faster to understand "one failure or several", where to escalate, what's affected in the business.

---

## 2. Tabs — what's there and why

| Tab | Path | Purpose |
|---|---|---|
| **Overview** | `/` | KPI: **11 CIs**, **10 relationships**, Model health. Scale of the ready-made payment contour model |
| **Elements** | `/inventory` | CI registry — already from `demo_pay_elements.import.json`. External IDs (hostname, IP, serviceCode) for alert matching |
| **Dependencies** | `/relations` | Relationships from `demo_pay_relations.import.json`. All **7 relationship types** from requirements. "Validate model" — graph is intact |
| **Map** | `/graph` | Graph visualization. **Business path** (DB → … → business service). **Impact** — answer for the director |
| **Correlation** | `/correlation` | Alert input (as from monitoring) → **Ingest** → matching and chain |
| **Audit** | `/audit` | Who and when changed the model (import, Autodiscover) |
| **Settings** | `/settings` | Autodiscover connector on `demo-pay-srv`, API documentation for CE |

**Graph (already loaded):**

```
demo-biz (PAY-SVC) → demo-pay-it → demo-app (app-01) → demo-db (10.0.0.5, ext-db-1)
                              ↘ hosted_on → demo-pay-srv (pay-srv-01)
```

**11 CIs:** `demo-biz`, `demo-pay-it`, `demo-app`, `demo-db`, `demo-pay-srv`, `demo-pay-k8s`, `demo-pay-vm`, `demo-pay-queue`, `demo-pay-tc`, `demo-pay-ext`, `demo-net-mon`.

---

## 3. Two correlation scenarios

Tab **Correlation** (`/correlation`): enter alerts as from monitoring → **Process** (Ingest). Below — what to show on the demo and how to explain to the audience.

---

### Scenario A — merge (one incident)

| | |
|---|---|
| **Type** | **One `depends_on` chain.** Different systems send different fields, but all alerts land on nodes of one cascade: DB → application → … → business service PAY. |
| **Why we show it** | Answer to the on-call question: *"Four alerts in a minute — one failure or four?"* Without RSM, CE and the operator match hostname, IP, externalId, and service codes themselves. |
| **What it gives** | **Correlation engine** gets a signal: alerts **can** be merged into **one INC**. The operator immediately sees the **root cause zone** (closer to the DB) and the affected business — instead of dissecting four unrelated tickets. |
| **What we see on screen** | After **Process**: **Matched = 4**, **Related chain = true** (green), **Root cause zone** block — `demo-db`, graph with chain and alerts highlighted, **Enrichment** for found CIs. |

**Story for the presentation:** 02:00, payment contour. Zabbix, Prometheus, CMDB, and APM simultaneously send alarms — different fields, same meaning.

**Input** — 4 rows, each with **one** filled field:

| Row | As in monitoring | Field | Value | Where it lands in the model |
|---|---|---|---|---|
| 1 | Zabbix | hostname | `app-01` | **demo-app** (Application) |
| 2 | Prometheus | ip | `10.0.0.5` | **demo-db** (Database) |
| 3 | CMDB | externalId | `ext-db-1` | **demo-db** (same node) |
| 4 | APM | serviceCode + applicationCode | `PAY` + `PAY-APP` | **demo-biz** (Business Service) |

→ **Process**

**Result for CE:** `chain_related: true` → "one incident" rule. Chain in the model: `demo-db` → `demo-app` → … → `demo-biz`. Root cause — at the DB, not at the APM code.

---

### Scenario B — do not merge (different incidents)

| | |
|---|---|
| **Type** | **Two nodes, one `depends_on` chain — no.** Both alerts are in the payment contour and both are found in the model, but sit on **different branches** of the graph (server via `hosted_on`, application via `depends_on`). |
| **Why we show it** | Answer to the question: *"Two alerts in the same contour — always one incident?"* No. Coincidence in time and PAY domain **does not** mean a common root cause. |
| **What it gives** | CE **does not** get grounds to merge: **two separate INCs** (disk on the server and application error — different work). RSM **does not give a false "yes"** on merging infrastructure and application. |
| **What we see on screen** | **Matched = 2**, **Related chain = false** (yellow). No **Root cause zone** block and no shared chain graph — the system honestly says: no common cascade visible. |

**Story for the presentation:** in the same PAY, both host `pay-srv-01` and application `app-01` went down. Time is close, contour is one — but these are **two different nodes** with no `depends_on` link between them.

**Input** — 2 rows, hostname only:

| Row | hostname | Found CI | CI Type | Relationship to other alert |
|---|---|---|---|---|
| 1 | `pay-srv-01` | **demo-pay-srv** | Server | `hosted_on` — infrastructure |
| 2 | `app-01` | **demo-app** | Application | `depends_on` → DB — application layer |

→ **Process**

**Result for CE:** `chain_related: false` → "do not merge" rule (or escalation to the operator). Matching worked, but **no merge** — and this is expected behavior, not a model error.

---

## 4. Autodiscover scenario — what and why

**Problem:** `demo-app` in the registry has hostname and codes (`PAY`, `PAY-APP`), but **no IP**. An alert by application IP alone **will not match**.

**Why Autodiscover:**

| Role | What they get |
|---|---|
| Analyst | No need to add IP in Excel — **scan from the server** |
| Operator | Alerts by application IP start finding their way into the model |
| Director / CE | Correlation on an **up-to-date** map |

**Demo steps:**

1. `/inventory` → `demo-app` — **no IP**
2. **Autodiscover** → check **`demo-pay-srv`** → **Manual mode** → **Scan**
3. **Fields** tab: `demo-app` / `ip` / **`10.0.0.10`**
4. **Relationships** tab: `depends_on` → `demo-db` (if suggested)
5. **Apply selected** → IP appears on `demo-app`
6. `/audit` — entry with diff

**Outcome:** the model was **not drawn by hand** — pulled from the server, a person confirmed. This is the main difference from Excel-CMDB: the map **does not fall behind** reality, and correlation scenarios A/B work more reliably.

---

**Brief for the presentation:** map already loaded (11 CIs, 10 relationships) → tabs → **A (type: one chain):** 4 alerts, different fields → `chain_related: true`, root cause `demo-db` → one INC → **B (type: different branches):** server + application → `chain_related: false` → two INCs → **Autodiscover:** IP from the server without manual CMDB.

---

## Checklist

- [ ] `seed_demo.py` (PAY fixtures only)
- [ ] Login → Overview: **11 CIs**, health green
- [ ] PAY elements and dependencies visible (`demo_pay_*.import.json`)
- [ ] **3.A:** 4 rows → Matched **4**, Related chain **true**, zone **`demo-db`**
- [ ] **3.B:** `pay-srv-01` + `app-01` → Matched **2**, Related chain **false**, no root cause zone
- [ ] **3.3:** Autodiscover → `demo-app.ip` = `10.0.0.10`
