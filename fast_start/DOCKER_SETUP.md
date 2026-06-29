# Running OmniSight in Docker

**English** · [Русская версия](ЗАПУСК_DOCKER.md)

Three services in dev-compose: **PostgreSQL**, **Backend (API)**, **Frontend (Web via Nginx)**.  
Production-compose adds **Worker** (auto-sync, webhook outbox).

See also: [`../README.md`](../README.md) · [`WINDOWS_SETUP.md`](./WINDOWS_SETUP.md) · [`DEMO_GUIDE.md`](./DEMO_GUIDE.md)

---

## Quick start (Windows)

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and start it.
2. From the repository root:

```powershell
.\scripts\docker-dev.ps1
```

The script creates `docker/.env` (if missing), builds images, and starts containers.

---

## Manual startup (dev)

```powershell
cd docker
copy .env.dev.example .env
docker compose -f docker-compose.dev.yml --env-file .env up -d --build
```

First run takes several minutes (building API and Web images).

---

## URLs

| Service | URL | Description |
|---------|-----|-------------|
| Web UI | http://localhost:8080 | Interface (Nginx proxies `/api` to backend) |
| API / Swagger | http://localhost:8000/docs | REST API directly (port exposed in dev-compose) |
| Health | http://localhost:8000/health/ready | API + DB readiness |

**Login:** `admin@omnisight.local` / `admin123`

On first start, the API automatically creates tables (if missing) and seeds (`SEED_ON_START=1`).

---

## Useful commands

```powershell
cd docker

# All service logs
docker compose -f docker-compose.dev.yml logs -f

# API logs only
docker compose -f docker-compose.dev.yml logs -f api

# Stop (DB data preserved)
docker compose -f docker-compose.dev.yml down

# Stop and remove DB volume
docker compose -f docker-compose.dev.yml down -v

# Rebuild after code changes
docker compose -f docker-compose.dev.yml up -d --build
```

---

## Docker files in the repository

| File | Purpose |
|------|---------|
| `docker/docker-compose.dev.yml` | **Dev/demo**: DB + API + Web, simple secrets, Swagger enabled |
| `docker/docker-compose.yml` | PostgreSQL only (API and UI run locally) |
| `docker/docker-compose.prod.yml` | **Production**: DB + API + Worker + Web, strict secrets |
| `docker/docker-compose.ha.yml` | HA PostgreSQL example (Patroni) |
| `apps/api/Dockerfile` | FastAPI + worker image |
| `apps/web/Dockerfile` | React build + Nginx |
| `docker/.env.dev.example` | Example variables for dev |
| `docker/.env.example` | Example variables for production |

---

## Production

```powershell
cd docker
copy .env.example .env
# Set SECRET_KEY, API_KEY, WEBHOOK_SECRET, ADMIN_INITIAL_PASSWORD
docker compose -f docker-compose.prod.yml --env-file .env up -d --build
```

| Service | Access |
|---------|--------|
| Web UI | http://localhost:8080 (or `WEB_PORT` from `.env`) |
| API | inside Docker network only; externally via Nginx at `/api` |
| Worker | background process, no published port |

Redeploy without seed: `SEED_ON_START=0` in `.env`.

---

## Demo CE (test Correlation Engine)

Not included in Docker-compose — run locally after the stack is up:

```powershell
cd apps\demo-ce
pip install -r requirements.txt
$env:RSM_URL = "http://127.0.0.1:8000"
python main.py
```

Demo CE: http://localhost:8090

> With full Docker stack, API is available at `localhost:8000` (dev) or via Nginx `/api` on `8080`. Demo CE defaults to `http://127.0.0.1:8000`.

---

## Docker vs local startup

| | Docker (`docker-dev.ps1`) | Local (`dev.ps1` / `start-all.ps1`) |
|--|---------------------------|----------------------------------------|
| UI | http://localhost:8080 (Nginx, prod build) | http://localhost:5173 (Vite dev, hot reload) |
| API | container, port 8000 | uvicorn --reload |
| DB | PostgreSQL container | local or separate container |
| Demo CE | manual start | `start-all.ps1` starts automatically |
| Hot reload | no (need `--build` after edits) | yes |

For UI development, local `npm run dev` is more convenient; for demo and prod-like checks — Docker.
