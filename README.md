# OmniSight RSM

**English** · [Русская версия / Russian README](README.ru.md)

**OmniSight** is an IT landscape management platform. The **RSM** (Resource-Service Model) module maintains a catalog of configuration items (CIs), directed dependencies between them, topology visualization, and an API for external monitoring and alert correlation systems.

Stack: **FastAPI** (`apps/api`) + **React** (`apps/web`) + **PostgreSQL**.

| Document | Purpose |
|----------|---------|
| [`docs/README.md`](docs/README.md) | Requirements, implementation mapping, product passport |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Layers, DI, async DB, frontend patterns |
| [`fast_start/WINDOWS_SETUP.md`](fast_start/WINDOWS_SETUP.md) | Local setup (Windows) |
| [`fast_start/DOCKER_SETUP.md`](fast_start/DOCKER_SETUP.md) | Docker setup |
| [`fast_start/DEMO_GUIDE.md`](fast_start/DEMO_GUIDE.md) | Demo scenario for judges |

---

## Features

- **CI inventory** — 11 types, CRUD, external identifiers (hostname, IP, serviceCode, etc.), JSON attributes, lifecycle, trash
- **Relations** — 7 dependency types, validation (cycles, archive, broken links)
- **Graph** — depth traversal, business path, impact, layout, PNG export
- **Autodiscover (map)** — auto-collection from servers, draft auto-mapping and field autofill with confirmation
- **Import / Export** — JSON, CSV, XLSX; preview and mapping of unknown types on import (`/import/preview`, `/import/mapped`); result report
- **Correlation** — batch resolve of alert identifiers, relation graph, `chain_related`
- **Audit** — change log with old/new diff
- **RBAC** — viewer / editor / admin roles
- **i18n** — RU / EN, dark and light theme

---

## Requirements

| Component | Version |
|-----------|---------|
| Python | 3.12+ |
| Node.js | 20+ |
| PostgreSQL | 16+ |
| Docker (optional) | for PostgreSQL container or full stack |

---

## Quick start (Windows)

**UI + API** (two PowerShell windows):

```powershell
./scripts/dev.ps1
```

**UI + API + Demo CE** (three windows — for the correlation section):

```powershell
./scripts/start-all.ps1
```

Scripts install dependencies, create the DB schema (if tables are missing), and load demo data.

| Service | URL |
|---------|-----|
| Web UI | http://localhost:5173 |
| API / Swagger | http://localhost:8000/docs |
| Demo CE | http://localhost:8090 (only with `start-all.ps1`) |
| Login | `admin@omnisight.local` / `admin123` |

Details: [`fast_start/WINDOWS_SETUP.md`](fast_start/WINDOWS_SETUP.md)

---

## Manual setup

### 1. Database

**Option A — local PostgreSQL**

```powershell
cd apps/api
pip install -e ".[dev]"
$env:POSTGRES_PASSWORD = "postgres_superuser_password"
python scripts/init_postgres.py
```

The script creates the `omnisight` role, `omnisight` database, and a `.env` file with `DATABASE_URL`.

**Option B — PostgreSQL in Docker** (see section below).

### 2. Migrations and demo data

```powershell
cd apps/api
python scripts/deploy_db.py --seed
python scripts/seed_demo.py
```

### 3. Backend

```powershell
cd apps/api
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Frontend

```powershell
cd apps/web
npm install
npm run dev
```

---

## Production (Docker Compose)

Full stack: **PostgreSQL + API + Worker + Nginx (UI)** with healthcheck, JSON logs, OpenAPI/Swagger, and secret validation on startup.

```powershell
cd docker
copy .env.example .env
# Set SECRET_KEY, API_KEY, WEBHOOK_SECRET, ADMIN_INITIAL_PASSWORD (openssl rand -hex 32)
docker compose -f docker-compose.prod.yml --env-file .env up -d --build
```

| Service | URL |
|---------|-----|
| Web UI | http://localhost:8080 |
| Swagger / OpenAPI | http://localhost:8080/docs · http://localhost:8080/openapi.json |
| Health (ready) | http://localhost:8080/health/ready |
| API (inside Docker network) | `api:8000` |

Worker (`python -m src.worker`) handles auto-sync scheduler and webhook outbox redelivery.

To redeploy without re-seeding: set `SEED_ON_START=0` in `.env`.

Production API variables (`APP_ENV=production`):

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | JWT, minimum 32 characters |
| `API_KEY` / `WEBHOOK_SECRET` | integrations, minimum 24 characters |
| `ADMIN_INITIAL_PASSWORD` | admin password on first seed (≥12 characters) |
| `CACHE_ENABLED=false` | required with multiple replicas without Redis; enable cache with `REDIS_URL` |
| `DATABASE_ASYNC_ENABLED` | **true** by default — reads: native async ORM; writes: async write pool (asyncpg) |
| `REDIS_URL` | optional: distributed cache for multi-replica (`redis://host:6379/0`) |
| `ENSURE_SCHEMA_ON_START=false` | in k8s: schema only via Job `k8s/schema-job.yaml` |
| `CORS_ORIGINS` | public UI URL |
| `TRUSTED_HOSTS` | hosts behind reverse-proxy (optional) |
| `RATE_LIMIT_MAX_REQUESTS` | API request limit per IP (default 300/60s in compose) |
| `BACKGROUND_TASKS_ENABLED=false` | in API with multiple replicas; background tasks run in worker |
| `WEBHOOK_SYNC_DELIVERY=false` | enqueue only; worker delivers with retries |

Local production-like API run:

```powershell
cd apps/api
$env:APP_ENV = "production"
$env:LOG_JSON = "true"
# ... other secrets from .env.example
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 2 --proxy-headers
```

Details: [`fast_start/DOCKER_SETUP.md`](fast_start/DOCKER_SETUP.md)

---

## Docker (database only)

The repo includes `docker/docker-compose.yml` — starts **PostgreSQL** only. API and UI run locally and connect to the container.

### 1. Start PostgreSQL

```powershell
docker compose -f docker/docker-compose.yml up -d
```

Container parameters:

| Parameter | Value |
|-----------|-------|
| Port | `5432` |
| User | `omnisight` |
| Password | `omnisight` |
| Database | `omnisight` |

### 2. Configure API `.env`

```powershell
cd apps/api
copy .env.example .env
```

In `.env` set:

```env
DATABASE_URL=postgresql+psycopg2://omnisight:omnisight@localhost:5432/omnisight
```

### 3. Migrations, demo data, run the app

```powershell
cd apps/api
pip install -e ".[dev]"
python scripts/deploy_db.py --seed
python scripts/seed_demo.py
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

In another terminal:

```powershell
cd apps/web
npm install
npm run dev
```

### Stop the container

```powershell
docker compose -f docker/docker-compose.yml down
```

Data persists in Docker volume `pgdata`. To remove the volume as well:

```powershell
docker compose -f docker/docker-compose.yml down -v
```

---

## Tests

```powershell
cd apps/api
pytest tests/ -q                    # 380+ tests, coverage ≥84%
python scripts/seed_demo.py
python scripts/verify_demo_acceptance.py   # 20/20
```

```powershell
cd apps/web
npm run build
npm test
npm run test:e2e
```

Quick smoke (API + web unit + build):

```powershell
./scripts/smoke.ps1
```

---

## Project structure

```
OmniSight/
├── apps/
│   ├── api/          # FastAPI, Alembic, worker, tests, scripts/
│   ├── web/          # React + Vite, e2e/
│   └── demo-ce/      # test Correlation Engine (port 8090)
├── docker/           # compose: PostgreSQL, dev, prod (+ worker), HA
├── k8s/              # Kubernetes: API, worker, web, ingress, HPA, redis
├── docs/             # requirements, mapping, product passport
├── fast_start/       # setup guides and demo scenario (EN + RU)
├── fixtures/         # domain constants, demo data, drift tests
├── scripts/
│   ├── dev.ps1           # UI + API (local)
│   ├── start-all.ps1     # UI + API + Demo CE
│   ├── docker-dev.ps1    # full stack in Docker
│   └── smoke.ps1         # quick CI check
├── README.md             # English
└── README.ru.md          # Russian
```

Documentation is bilingual: English files are the default entry points; each has a Russian counterpart (`.ru.md` or a Russian-named file) with a language switcher at the top.

---

## API

Canonical API version is **`/api/v1`** (UI, acceptance tests, integrations), as in competition spec §8. See [`docs/REQUIREMENTS_MAPPING.md`](docs/REQUIREMENTS_MAPPING.md).

Main endpoint groups:

- `/api/v1/auth` — login, users, password change
- `/api/v1/ci`, `/api/v1/ci/types` — CRUD, types, import/export, preview/mapped import
- `/api/v1/relations` — CRUD, validate, import/export
- `/api/v1/resources/*` — search, graph, impact, components, business-path, resolve, graph-layout
- `/api/v1/correlation/*` — ingest, context, chain-check
- `/api/v1/autodiscover/*` — connectors, scan, apply
- `/api/v1/dashboard` — overview metrics
- `/api/v1/audit` — audit log
- `/api/v1/meta` — schema version, constants
- `/health`, `/health/live`, `/health/ready` — health checks (ready → 503 without DB)

Full spec: http://localhost:8000/docs · file `apps/api/openapi.json`

Acceptance tests for FR 1–54:

```powershell
cd apps/api
python scripts/seed_demo.py
python scripts/verify_demo_acceptance.py   # expected 20/20 PASS
```

---

## License

[MIT](LICENSE)
