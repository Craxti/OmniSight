# OmniSight RSM Product Passport

**English** · [Русская версия](ПАСПОРТ_ПРОДУКТА.md)

> This document is based on a live deployed environment (UI :5173, API :8000, Demo CE :8090).  
> Screenshots were taken from the running interface — see the [`screenshots/`](./screenshots/) folder.

---

## 1. Product Marketing Name

**OmniSight RSM**  
*(OmniSight — IT landscape resource-service model module)*

---

## 2. Product Marketing Description

**OmniSight RSM** is a platform for inventorying and visualizing the IT landscape: a unified registry of configuration items, directed dependencies between them, and an interactive topology map. The product gives operations teams and external monitoring systems a **reference dependency map** — to match disparate technical alerts with model objects, understand the business context of an incident, and accelerate root-cause analysis.

OmniSight **does not replace** a monitoring system or correlation engine; it serves as the **source of truth** for how your IT landscape is structured and how components are connected.

---

## 3. Product Essence

RSM (resource-service model) is a structured description of IT infrastructure elements (servers, databases, applications, business services, etc.) and **directed relationships** between them (`depends_on`, `hosted_on`, `part_of`, `uses`, and others).

**Key idea:** when a group of alerts arrives in monitoring (hostname, IP, serviceCode, externalId…), the external correlation system calls the RSM API, receives matched objects, a dependency graph, and enrichment (criticality, environment, affected business services, root-cause zone). Based on this, the correlation engine decides whether to merge alerts into a single incident.

**In one sentence:** an IT landscape registry with directed relationships and an API for alert correlation.

---

## 4. Product Screenshots

Screenshots were taken from the real UI of a live environment (June 2026).

| # | Screen | File |
|---|--------|------|
| 1 | Login page | [`01-login.png`](./screenshots/01-login.png) |
| 2 | Overview (dashboard) | [`02-dashboard.png`](./screenshots/02-dashboard.png) |
| 3 | RSM element registry | [`03-inventory.png`](./screenshots/03-inventory.png) |
| 4 | Dependencies table | [`04-relations.png`](./screenshots/04-relations.png) |
| 5 | Dependency map (panel) | [`05-graph.png`](./screenshots/05-graph.png) |
| 5b | Dependency map (demo-hub topology) | [`05b-graph-topology.png`](./screenshots/05b-graph-topology.png) |
| 6 | Alert correlation (input) | [`06-correlation.png`](./screenshots/06-correlation.png) |
| 6b | Alert correlation (ingest result) | [`06b-correlation-result.png`](./screenshots/06b-correlation-result.png) |
| 7 | Audit log | [`07-audit.png`](./screenshots/07-audit.png) |
| 8 | Settings (CI types, connectors, API) | [`08-settings.png`](./screenshots/08-settings.png) |
| 9 | Demo Correlation Engine (incoming alerts) | [`09-demo-ce.png`](./screenshots/09-demo-ce.png) |
| 10 | Demo CE — correlation result with RSM | [`10-demo-ce-result.png`](./screenshots/10-demo-ce-result.png) |

### Brief Description of Key Screens

- **Overview** — model summary: element count, relationships, active objects, relationship integrity, distribution by type and status.
- **RSM Elements** — CRUD registry of configuration items with filters, import/export, and Autodiscover.
- **Map** — interactive dependency graph from a selected root element with a legend (root, impact zone, business path, downstream components).
- **Correlation** — manual and API ingest scenario: matching alert identifiers to RSM objects, graph, `chain_related`, root-cause zone.
- **Demo CE** — integration demo: 4 alerts from Zabbix/Prometheus/Nagios/APM → `POST /api/v1/correlation/ingest` → decision to merge into an incident.

---

## 5. Target Audience

| Segment | Role | How they use the product |
|---------|------|--------------------------|
| **IT Operations** | L2/L3 engineers, on-call staff | Maintain the CI registry, view the dependency map, assess impact during incidents |
| **Monitoring / Observability** | Monitoring engineers, SRE | Integrate the RSM API with a correlation engine to enrich alerts |
| **Architects and Analysts** | System architects, analysts | Design and maintain the data model, CI types, and relationships |
| **ITSM / AIOps** | ServiceNow, Jira SM, and other integrators | Use the API to match alerts and build incident context |
| **IT Leadership** | IT directors, service owners | Gain visibility: which business services are affected when a component fails |

**Industry:** enterprise B2B — banks, telecom, retail, public sector, and any organization with a mature IT landscape and monitoring systems.

---

## 6. Problems It Solves

1. **Disparate technical alerts** — hostname, IP, metric, service code arrive separately; without a dependency model, it is unclear whether they belong to one incident.
2. **Missing "technology → business" link** — hard to quickly answer which business service is impacted when a database or server goes down.
3. **Outdated or fragmented CMDB** — asset data lives in Excel, in engineers' heads, or in disconnected systems.
4. **Long incident investigation** — without a dependency map, an engineer manually traces the chain "DB → application → business service".
5. **Low correlation quality** — a correlation engine cannot group events without a reference relationship model.
6. **No audit trail for model changes** — unclear who changed an element or relationship and when, reducing trust in the data.

---

## 7. Product Advantages

| Advantage | Description |
|-----------|-------------|
| **Reference dependency map** | 11 CI types, 7 directed relationship types, visual topology |
| **API-first for integrations** | REST API + OpenAPI, `X-API-Key`, batch ingest for correlation engine |
| **Correlation context out of the box** | Identifier resolve, `chain_related`, enrichment, `potential_root_cause_zone` |
| **Autodiscover** | Automatic data collection from servers (SSH, files), draft mapping with confirmation |
| **Import / Export** | JSON, CSV, XLSX — quick start and exchange with external systems |
| **Audit with diff** | Change log with old/new for model quality control |
| **RBAC** | viewer / editor / admin roles |
| **Localization and UX** | RU/EN, dark and light theme, modern React interface |
| **Scalability** | Designed for up to 50,000 CIs, NFR: resolve < 200 ms |
| **Clear responsibility boundaries** | RSM does not replace monitoring and CE — reduces implementation risk |

---

## 8. How the Product Works (Technical)

### Architecture

```
┌─────────────────┐     JWT      ┌──────────────────┐     SQL      ┌─────────────┐
│  React UI       │─────────────▶│  FastAPI API     │─────────────▶│ PostgreSQL  │
│  (Vite, :5173)  │              │  (:8000)         │              │  (:5432)    │
└─────────────────┘              └────────┬─────────┘              └─────────────┘
                                          │
┌─────────────────┐     X-API-Key         │
│  Demo CE        │───────────────────────┘
│  (:8090)        │  POST /api/v1/correlation/ingest
└─────────────────┘
         ▲
         │ alerts (hostname, IP, serviceCode…)
┌────────┴────────┐
│ Zabbix,         │
│ Prometheus,     │
│ Nagios, APM     │
└─────────────────┘
```

### Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS 4, TanStack Query, React Flow |
| Backend | Python 3.12+, FastAPI, SQLAlchemy, Alembic, Pydantic |
| Database | PostgreSQL 16+ |
| Deployment | Docker Compose (dev/prod), Nginx |

### Data Model

- **11 CI types:** Business Service, IT Service, Application, Technical Component, Server, Virtual Machine, Container, Database, Queue, Network Element, External Service.
- **7 relationship types:** `depends_on`, `affects`, `part_of`, `hosted_on`, `uses`, `linked_to`, `reserves`.
- **External identifiers for correlation:** hostname, IP, serviceCode, applicationCode, externalId, cmdbId.

### Main Correlation API Scenario (§3.2 Spec)

```
1. Monitoring → group of alerts within a time window
2. Correlation Engine → POST /api/v1/correlation/ingest
   Body: { "alerts": [{ "hostname": "app-01" }, { "ip": "10.0.0.5" }, …] }
3. RSM → resolve (match to CIs) + graph (dependency graph)
4. RSM → correlation.chain_related (are alerts on the same depends_on chain?)
5. RSM → enrichment (name, type, criticality, environment, business services)
6. RSM → potential_root_cause_zone (depends_on chain leaves)
7. CE → decision to merge into an incident (outside RSM)
```

### Key Backend Modules

- `services/ci/` — element CRUD, import/export
- `services/relations/` — relationships, validation (cycles, archive, broken references)
- `services/rsm/` — graph, topology, impact, search
- `services/rsm_correlation.py` — batch resolve and correlation context
- `services/autodiscover/` — pipeline: connector → discovery → mapping → apply
- `services/audit.py` — change log

### Security and Operations

- JWT for UI, `X-API-Key` for integrations
- Health: `/health/live`, `/health/ready`
- Rate limiting, CORS, security headers
- OpenAPI: `http://localhost:8000/docs`

---

## 9. Client Benefits (Business)

| Benefit | Business effect |
|---------|-----------------|
| **Reduced MTTR** | Faster understanding of dependency chains and root-cause zone — less service downtime |
| **Lower alert noise** | Correlation engine receives structure to group related events into one incident |
| **Business transparency** | Visible which Business Service is affected when a technical component fails |
| **Single source of truth** | One current model instead of fragmented Excel and outdated CMDB |
| **Faster AIOps adoption** | Ready ingest API — no need to build a dependency model from scratch |
| **Data quality control** | Audit, relationship validation, import reports — model stays trustworthy |
| **Lower integration TCO** | OpenAPI, standard import/export formats, demo environment for acceptance |
| **Scale without rewrite** | Architecture designed for tens of thousands of CIs |

**ROI logic:** investment in a current RSM pays off through reduced incident investigation time and improved automatic correlation quality — without replacing the existing monitoring stack.

---

## 10. User Scenarios

Below are four typical OmniSight RSM usage scenarios. Each is described in a uniform format: **goal → who performs it → where it starts → step-by-step actions → expected outcome**.

| # | Scenario | Role | Interface |
|---|----------|------|-----------|
| 1 | Alert correlation | Monitoring engineer / CE | API + Demo CE, "Correlation" UI |
| 2 | Impact analysis on the map | Operations engineer | "Map" UI |
| 3 | Model population (Autodiscover / import) | Model administrator | "Elements", "Settings", "Audit" UI |
| 4 | CE integration via API | Integration developer / SRE | Swagger, Demo CE, "Settings → API" |

---

### Scenario 1. Alert Correlation

| | |
|---|---|
| **Goal** | Determine whether several technical alerts belong to one incident and obtain business context for investigation |
| **Role** | Monitoring engineer (L2) or correlation engine |
| **Preconditions** | A dependency chain exists in RSM (e.g. PAY: `demo-db` → `demo-app` → `demo-biz`); CIs have external IDs filled in (hostname, IP, serviceCode, etc.) |
| **Trigger** | A group of alerts from different monitoring systems arrives within a short window (5–10 min) |

**Scenario flow**

1. **Incoming events.** Monitoring records alerts with different identifiers:
   - Zabbix: `hostname: app-01` (CPU > 90%)
   - Prometheus: `ip: 10.0.0.5` (low disk space)
   - Nagios: `externalId: ext-db-1` (database connection errors)
   - APM: `serviceCode: PAY`, `applicationCode: PAY-APP` (latency spike)
2. **Send to RSM.** Correlation engine sends a batch to the API:
   `POST /api/v1/correlation/ingest` with the `X-API-Key` header.
3. **Matching (resolve).** RSM finds model objects by hostname, IP, externalId, serviceCode and returns resolved / unresolved lists.
4. **Context building.** RSM returns:
   - dependency graph for matched CIs;
   - `chain_related: true/false` — whether all alerts are on the same `depends_on` chain;
   - **enrichment** — type, environment, criticality, affected business services;
   - **root-cause zone** (`potential_root_cause_zone`) — candidates at the root of the chain.
5. **CE decision.** Based on the RSM response, the correlation engine decides: merge alerts into one incident or keep them separate.  
   *In the demo:* when `chain_related=true` and 4/4 resolved → incident "INC-DEMO: PAY stack degradation".
6. **UI verification (optional).** The same ingest can be repeated manually on the **Correlation** screen (`/correlation`) to debug rules.

**Expected outcome**

- Instead of 4 unrelated tickets — **one incident** with a root-cause hypothesis (e.g. `demo-db`).
- The incident card shows: affected business service, criticality, environment.

**Value:** reduced MTTR, less noise from duplicate alerts, clear business context without manual CMDB lookup.

**Screenshots:** [`10-demo-ce-result.png`](./screenshots/10-demo-ce-result.png), [`06b-correlation-result.png`](./screenshots/06b-correlation-result.png)

---

### Scenario 2. Impact Analysis on the Dependency Map

| | |
|---|---|
| **Goal** | Before work begins or during an outage, understand which services and components will be affected |
| **Role** | Operations engineer, on-call staff |
| **Preconditions** | RSM has a model with directed relationships; elements have `active` status |
| **Trigger** | Planned maintenance on a server / VM / DB **or** an alert on an infrastructure component |

**Scenario flow**

1. User opens the **Dependency Map** (`/graph`).
2. In the **"Root element"** field, selects the starting point — Business Service (`demo-hub-biz`) or the component to be changed (`demo-hub-srv`).
3. Sets **depth** of traversal (e.g. 3) and optionally filters by relationship type.
4. On the graph, sees the color legend:
   - **root** (red) — selected element;
   - **business path** (green) — chain up to the business service;
   - **impact zone** (yellow) — what will be affected if the root fails;
   - **downstream components** (blue) — infrastructure "below" the application.
5. In the side panel, reads the summary: business path, affected Business Services, list of downstream components.
6. Makes a decision: maintenance window, escalation to the `owner`, incident priority by CI **criticality**.

**Example with demo data**

```
demo-hub-biz (Business Service)
    └── depends_on → demo-hub (Application)
            ├── depends_on  → demo-hub-db
            ├── hosted_on   → demo-hub-srv   ← planned work here
            ├── part_of     → demo-hub-vm
            └── uses / linked_to / affects / reserves → …
```

**Expected outcome**

- Clear **blast radius**: which business service and which applications/DBs are affected.
- Justified coordination of work with the service owner.

**Value:** lower risk of accidentally taking down a critical service; quick answer to "what breaks if X fails".

**Screenshot:** [`05b-graph-topology.png`](./screenshots/05b-graph-topology.png)

---

### Scenario 3. Model Population (Autodiscover and Import)

| | |
|---|---|
| **Goal** | Quickly and reliably populate or update the CI and relationship registry without manually entering hundreds of records |
| **Role** | Model administrator (editor / admin role) |
| **Preconditions** | User is authorized with rights to create CIs; a connector is configured or an import file is prepared |
| **Trigger** | A new scope appears (cluster, environment, branch) **or** data migration from Excel / legacy CMDB is needed |

**Scenario flow — option A: Autodiscover**

1. **Source setup.** In **Settings → Connectors**, creates a connector (SSH/host or file).
2. **Run discovery.** On the **Elements** screen (`/inventory`), clicks **Autodiscover** — the system collects data from specified hosts or from a file.
3. **Draft mapping.** RSM proposes auto-mapping: which fields become CI, hostname, IP, element type.
4. **Confirmation.** Administrator reviews the draft, edits if needed, and **confirms** CI creation/update.
5. **Relationships.** If needed, adds dependencies manually or via relationship import.

**Scenario flow — option B: file import**

1. Prepares a **JSON / CSV / XLSX** file (or uses ready-made demo files from `fast_start/`).
2. On **Elements**, clicks **Import**, uploads the file.
3. Receives an **import report**: created / updated / errors.
4. If needed, imports relationships in a separate file.

**Completion (common for A and B)**

6. On **Overview**, checks metrics: element count, relationships, **relationship integrity** (no issues / warnings present).
7. On **Map**, runs **"Validate model"** (FR 19 validation).
8. In **Audit** (`/audit`), sees a record of import / autodiscover with old/new diff.

**Expected outcome**

- Current model ready for **alert correlation** (resolve by hostname, IP, externalId).
- Transparent change history for data quality audit.

**Value:** quick start without an "empty CMDB"; fewer manual entry errors; quality control through validation and audit.

**Screenshots:** [`03-inventory.png`](./screenshots/03-inventory.png), [`08-settings.png`](./screenshots/08-settings.png), [`07-audit.png`](./screenshots/07-audit.png)

---

### Scenario 4. Correlation Engine Integration via API

| | |
|---|---|
| **Goal** | Connect an existing or new correlation engine to RSM without modifying the product core |
| **Role** | Integration developer, SRE, AIOps architect |
| **Preconditions** | RSM is deployed; model is populated; access to Swagger and API Key |
| **Trigger** | Organization decides to use RSM as the **context source** for alert grouping |

**Scenario flow**

1. **Obtain access.** In **Settings → API**, copies `X-API-Key` (in dev: `omnisight-api-key-dev`).
2. **Study the contract.** Opens Swagger (`http://localhost:8000/docs`), key methods:
   - `POST /api/v1/correlation/ingest` — batch matching + graph + correlation context;
   - resolve, graph, impact — for point queries when needed.
3. **Implement the call.** In CE, when a batch of alerts accumulates within a time window:
   ```http
   POST /api/v1/correlation/ingest
   X-API-Key: <key>
   Content-Type: application/json

   {
     "alerts": [
       { "hostname": "app-01" },
       { "ip": "10.0.0.5" },
       { "externalId": "ext-db-1" },
       { "serviceCode": "PAY", "applicationCode": "PAY-APP" }
     ],
     "source": "my-ce",
     "depth": 3
   }
   ```
4. **Use the response** in CE logic:
   - `resolve.resolved` / `resolve.unresolved` — what was matched;
   - `correlation.chain_related` — whether alerts can be considered related;
   - `correlation.enrichment` — enrichment for ticket/incident;
   - `correlation.potential_root_cause_zone` — root-cause candidates.
5. **Grouping rule (example).** CE creates one incident if `chain_related=true` and resolved ≥ N; otherwise — separate incidents or escalation to an operator.
6. **Test on the environment.** Before prod, runs the scenario on **Demo CE** (`http://localhost:8090`) — the "Send 4 alerts to RSM" button reproduces the full cycle.

**Expected outcome**

- CE receives structured context from RSM in a single API call.
- Integration documented via OpenAPI; no RSM core changes required.

**Value:** faster AIOps adoption; clear separation of responsibilities — **RSM provides the model, CE decides** on grouping.

**Screenshots:** [`09-demo-ce.png`](./screenshots/09-demo-ce.png), [`10-demo-ce-result.png`](./screenshots/10-demo-ce-result.png)

---

## Appendix: Running the Demo Environment

```powershell
# From repository root
.\scripts\start-all.ps1
# or
.\scripts\dev.ps1
```

| Service | URL | Credentials |
|---------|-----|-------------|
| Web UI | http://localhost:5173 | admin@omnisight.local / admin123 |
| API / Swagger | http://localhost:8000/docs | X-API-Key: omnisight-api-key-dev |
| Demo CE | http://localhost:8090 | — |

Re-capturing screenshots:

```powershell
cd apps\web
node scripts/capture-product-screenshots.mjs
node scripts/capture-product-screenshots-extra.mjs
```

---

*Document version: 1.0 · Date: 23.06.2026 · Product: OmniSight RSM v1.0.0*
