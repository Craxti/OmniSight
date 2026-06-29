# OmniSight RSM Documentation

**English** · [Русская версия](README.ru.md)

Documents in this folder correspond to the competition requirements (text copy: [`_requirements_extract.txt`](./_requirements_extract.txt)).

| Document | Contents |
|----------|----------|
| [**_requirements_extract.txt**](./_requirements_extract.txt) | Full requirements text (FR 1–54, §8) |
| [**REQUIREMENTS_MAPPING.md**](./REQUIREMENTS_MAPPING.md) | Table: requirements ↔ implementation |
| [**product-passport/PRODUCT_PASSPORT.md**](./product-passport/PRODUCT_PASSPORT.md) | Product passport, screenshots, scenarios |

Setup and demo: [`../fast_start/WINDOWS_SETUP.md`](../fast_start/WINDOWS_SETUP.md) · [`../fast_start/DOCKER_SETUP.md`](../fast_start/DOCKER_SETUP.md) · [`../fast_start/DEMO_GUIDE.md`](../fast_start/DEMO_GUIDE.md)

Code architecture: [`../ARCHITECTURE.md`](../ARCHITECTURE.md)

## API

Canonical version is **`/api/v1`** (UI, acceptance tests, OpenAPI). Competition spec §8 lists `/api/v1/...` paths — functionally equivalent to v1; see [`REQUIREMENTS_MAPPING.md`](./REQUIREMENTS_MAPPING.md).

Specification (FR 43):

| Environment | Swagger | OpenAPI JSON |
|-------------|---------|--------------|
| Dev (local) | http://localhost:8000/docs | http://localhost:8000/openapi.json |
| Docker / prod compose | http://localhost:8080/docs | http://localhost:8080/openapi.json |
| File in repository | — | `apps/api/openapi.json` |

## Quick start

**UI + API only:**

```powershell
./scripts/dev.ps1
```

**UI + API + Demo CE** (correlation, test alerts):

```powershell
./scripts/start-all.ps1
```

**Full stack in Docker** (PostgreSQL + API + Web):

```powershell
./scripts/docker-dev.ps1
```

| URL | Purpose |
|-----|---------|
| http://localhost:5173 | UI (local Vite) |
| http://localhost:8080 | UI (Docker / prod compose) |
| http://localhost:8000/docs | Swagger (API directly) |
| http://localhost:8090 | Demo CE (only with `start-all.ps1`) |

Login: `admin@omnisight.local` / `admin123`

## Acceptance tests

```powershell
cd apps/api
python scripts/seed_demo.py
python scripts/verify_demo_acceptance.py   # 20 checks, expected 20/20 PASS
pytest tests/ -q                           # fast local run (no coverage)
pytest tests/ -q --cov=src --cov-report=term-missing:skip-covered --cov-fail-under=80  # CI gate
```

Quick smoke (API pytest + web unit + build):

```powershell
./scripts/smoke.ps1
```

Rebuild docx from requirements text: `python scripts/build_requirements_docx.py`
