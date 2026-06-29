# Competition Requirements vs OmniSight RSM Implementation

**English** · [Русская версия](СОПОСТАВЛЕНИЕ_ТЗ.md)

Requirements source: [`Требования_к_РСМ_конкурс.docx`](./Требования_к_РСМ_конкурс.docx) · text copy: [`_requirements_extract.txt`](./_requirements_extract.txt).

**API version:** canonical implementation — **`/api/v1`**, as in §8 of the requirements. UI, automated acceptance, and OpenAPI use v1.

**Automated acceptance:** `cd apps/api && python scripts/seed_demo.py && python scripts/verify_demo_acceptance.py` (20 checks, FR 1–54 and §8).

---

## Functional requirements FR 1–54

| FR | Area | Requirement (summary) | Status | Implementation |
|----|------|----------------------|--------|----------------|
| 1 | Elements | CRUD for RSM elements | ✅ | API `GET/POST/PATCH/DELETE /api/v1/ci`, UI `/inventory` |
| 2 | Elements | 11 types (business service … external service) | ✅ | `src/core/constants.py` → `RSM_OFFICIAL_TYPE_NAMES`, seed, `GET /api/v1/ci/types` |
| 3 | Elements | Unique internal ID | ✅ | `CI.id` (PK), API and detail card |
| 4 | Elements | External IDs (hostname, IP, serviceCode, …) | ✅ | `CI.external_ids`, `EXTERNAL_ID_FIELDS`, searchable columns |
| 5 | Elements | name, type, description, status, criticality, environment, owner, team | ✅ | `CI` model, UI forms, API schemas |
| 6 | Elements | Custom attributes (JSON) | ✅ | `CI.attributes`, no schema migrations |
| 7 | Elements | Lifecycle status (active … archived) | ✅ | `CI_STATUSES` in `constants.py` |
| 8 | Elements | Grouping by environments | ✅ | `environment` field, presets + free-form input (`EnvironmentInput`) |
| 9 | Elements | Search by name, type, ID, hostname, IP, owner, attributes | ✅ | `GET /api/v1/ci?q=…`, `GET /api/v1/resources/search` |
| 10 | Elements | Detail card with attributes, IDs, relations | ✅ | `GET /api/v1/ci/{id}`, UI `/inventory/:id` |
| 11 | Relations | Create relations | ✅ | `POST /api/v1/relations`, UI `/relations`, graph |
| 12 | Relations | Directed relations | ✅ | `source_ci_id` → `target_ci_id` |
| 13 | Relations | 7 relation types | ✅ | `RELATION_TYPES` in `constants.py` |
| 14 | Relations | type, direction, status, created_at, data_source | ✅ | `Relation` model, API responses |
| 15 | Relations | Graph for selected element | ✅ | `GET /api/v1/resources/{id}/graph`, UI `/graph` |
| 16 | Relations | Graph traversal to depth N | ✅ | query `depth` (1–10) |
| 17 | Relations | Business services depending on a resource | ✅ | `GET /api/v1/resources/{id}/impact` |
| 18 | Relations | Components below a business service | ✅ | `GET /api/v1/resources/{id}/components` |
| 19 | Relations | Validation (broken refs, archive, cycles) | ✅ | `GET /api/v1/relations/validate` |
| 20 | Relations | Visual chain up to business service | ✅ | `business-path` API + panel on `/graph` |
| 21 | Import | Import elements from files | ✅ | `POST /api/v1/ci/import`, `/import/csv`, `/import/mapped` |
| 22 | Import | Import relations | ✅ | `POST /api/v1/relations/import/json`, `/import/csv` |
| 23 | Import | Field, type, and relation validation | ✅ | import services, preview |
| 24 | Import | Report created/updated/skipped/errors | ✅ | `ImportReport` in API responses and UI |
| 25 | Export | Export full model | ✅ | `GET /api/v1/ci/export/full` |
| 26 | Export | Export with filters | ✅ | query params `environment`, `type_name`, `owner`, `criticality` |
| 27 | Export | elements + relations + attributes + external_ids | ✅ | JSON/CSV/XLSX export |
| 28 | Export | JSON, XLSX, CSV | ✅ | `/export/full`, `/export/csv`, `/export/xlsx` |
| 29 | Export | JSON for integrations | ✅ | `export` structure in JSON responses |
| 30 | API | GET element by internal ID | ✅ | `GET /api/v1/ci/{id}` |
| 31 | API | Search by external identifiers | ✅ | `GET /api/v1/resources/search` |
| 32 | API | Detail card (attributes, type, status, criticality, environment, owners) | ✅ | `GET /api/v1/ci/{id}`, resources API |
| 33 | API | Direct relations of an element | ✅ | `GET /api/v1/ci/{id}/relations` |
| 34 | API | Graph to depth N | ✅ | `GET /api/v1/resources/{id}/graph?depth=N` |
| 35 | API | Affected business services | ✅ | `GET /api/v1/resources/{id}/impact` |
| 36 | API | Downstream components | ✅ | `GET /api/v1/resources/{id}/components` |
| 37 | API | Batch resolve alerts | ✅ | `POST /api/v1/resources/resolve`, `POST /api/v1/correlation/ingest` |
| 38 | API | Shared graph for a group of objects | ✅ | `POST /api/v1/correlation/context` |
| 39 | API | Single chain check (chain_related) | ✅ | `POST /api/v1/correlation/chain-check` |
| 40 | API | Relation direction in response | ✅ | graph: `source`/`target` on edges |
| 41 | API | Relation types in response | ✅ | `relation_type` field on edges |
| 42 | API | Last modified date | ✅ | `updated_at` on CI and Relation |
| 43 | API | OpenAPI/Swagger | ✅ | `/docs`, `/openapi.json`, `apps/api/openapi.json` |
| 44 | Audit | CRUD history for elements | ✅ | `AuditLog`, `GET /api/v1/audit` |
| 45 | Audit | CRUD history for relations | ✅ | audit + `GET /api/v1/audit/relation/{id}` |
| 46 | Audit | Import/export history | ✅ | `log_import_audit` / `log_export_audit` |
| 47 | Audit | date, user, action, object, old/new | ✅ | `AuditLog` + diff in UI |
| 48 | Audit | History for a specific element | ✅ | `GET /api/v1/audit/ci/{id}`, tab on CI detail card |
| 49 | Audit | History for a specific relation | ✅ | `GET /api/v1/audit/relation/{id}`, modal on `/relations` |
| 50 | Roles | User roles | ✅ | `User.role` model, JWT |
| 51 | Roles | viewer / editor / admin | ✅ | `ROLES` in `constants.py` |
| 52 | Roles | viewer — read-only | ✅ | `require_viewer`, 403 on POST for viewer |
| 53 | Roles | editor — CI and relations | ✅ | `require_editor` on mutations |
| 54 | Roles | admin — directories, import, settings, roles | ✅ | `require_admin`, UI `/settings`, import 403 for editor |

---

## §8 Requirements — API endpoint compliance

| Requirements (§8) | Implementation | Notes |
|-------------------|----------------|-------|
| `GET /api/v1/resources/{id}` | `GET /api/v1/resources/{id}` | CI detail card (§8) |
| `GET /api/v1/resources/search` | `GET /api/v1/resources/search` | |
| `GET /api/v1/resources/{id}/relations` | `GET /api/v1/resources/{id}/relations` | direct relations (§8) |
| `GET /api/v1/resources/{id}/graph?depth=N` | `GET /api/v1/resources/{id}/graph?depth=N` | |
| `GET /api/v1/resources/{id}/impact` | `GET /api/v1/resources/{id}/impact` | |
| `POST /api/v1/resources/resolve` | `POST /api/v1/resources/resolve` | |
| `POST /api/v1/correlation/context` | `POST /api/v1/correlation/context` | |
| — | `GET /api/v1/ci/{id}`, `GET /api/v1/ci/{id}/relations` | aliases for CRUD UI (mutations via `/ci`) |
| — | `POST /api/v1/correlation/ingest` | resolve + context in one call (§3.2) |
| — | `POST /api/v1/correlation/chain-check` | FR 39 |

---

## §7 Requirements — UI

| UI requirement | Route | Component |
|----------------|-------|-----------|
| CI list with search and filters | `/inventory` | `InventoryPage` |
| Element detail card | `/inventory/:id` | `CIDetailPage` |
| Graph visualization | `/graph` | `GraphPage` |
| Import / export | `/inventory`, `/settings` | import/export modals |
| Audit log | `/audit` | `AuditPage` |
| Correlation (§3.2 scenario) | `/correlation` | `CorrelationPage` |

---

## §9 — Non-functional requirements

| Category | Status | Implementation |
|----------|--------|----------------|
| Performance resolve/search | ✅ | NFR &lt;200 ms, `tests/test_nfr_scale.py` (optional 50k CI) |
| Scalability | ✅ | indexes, pagination, PostgreSQL cache, rate limit |
| Reliability / integrity | ✅ | relation validation, soft-delete (`is_deleted`) |
| Logging | ✅ | `RequestLoggingMiddleware`, JSON logs in production |
| OpenAPI | ✅ | FR 43 |
| Async API (read/write pools) | ✅ | 100% async HTTP: native ORM + `session.run_sync` bridge, no thread-pool DB |

---

## §10–11 — Artifacts and lifecycle

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Model export JSON / XLSX / CSV | ✅ | export API |
| Import report | ✅ | `ImportReport` |
| Audit log | ✅ | `/audit` |
| Active and archived CI/relations | ✅ | statuses + `is_deleted`, recycle-bin |
| `updated_at` | ✅ | CI, Relation |
| “Who / when” history | ✅ | AuditLog |

---

## Additional (beyond requirements)

| Capability | Description |
|------------|-------------|
| Autodiscover | `/api/v1/autodiscover/*`, collection from servers, apply with confirmation |
| Demo CE | `apps/demo-ce` — demo correlation engine → ingest |
| i18n RU/EN | `apps/web/src/i18n` |
| Docker production | `docker/docker-compose.prod.yml` |

---

## Staging verification

```powershell
cd apps/api
python scripts/seed_demo.py
python scripts/verify_demo_acceptance.py
pytest tests/ -q
```

Expected result from `verify_demo_acceptance.py`: **20/20 PASS**, including FR37–39 ingest, FR52/FR54 RBAC, FR43 OpenAPI.
