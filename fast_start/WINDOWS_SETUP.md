# Running OmniSight on Windows

**English** · [Русская версия](ЗАПУСК_WINDOWS.md)

Frontend, backend, and the test Correlation Engine (Demo CE) — one script or three terminals manually.

> **Full Docker stack (DB + API + Web):** see [`DOCKER_SETUP.md`](./DOCKER_SETUP.md) — `.\scripts\docker-dev.ps1`

See also: [`../README.md`](../README.md) · [`DEMO_GUIDE.md`](./DEMO_GUIDE.md) · [`../docs/README.md`](../docs/README.md)

## Requirements

| Component | Version |
|-----------|---------|
| Python | 3.12+ |
| Node.js | 20+ |
| PostgreSQL | 16+ (local or Docker) |

---

## Quick start — one script

From the **repository root** in PowerShell:

```powershell
.\scripts\start-all.ps1
```

The script will:

1. Install Python dependencies for API and Demo CE
2. Create the DB schema if needed (`deploy_db.py --seed`) and load demo data (`seed_demo.py`)
3. Open **3 PowerShell windows**:
   - **Backend** (FastAPI) — port `8000`
   - **Frontend** (React/Vite) — port `5173`
   - **Test server** (Demo CE) — port `8090`

**UI + API only** (without Demo CE):

```powershell
.\scripts\dev.ps1
```

### If PowerShell blocks the script

Once (as user, not administrator):

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Or run without changing policy:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-all.ps1
```

### First run — database

**Option A — PostgreSQL in Docker** (easier):

```powershell
docker compose -f docker\docker-compose.yml up -d
cd apps\api
copy .env.example .env
```

`.env` should contain:

```env
DATABASE_URL=postgresql+psycopg2://omnisight:omnisight@localhost:5432/omnisight
```

**Option B — local PostgreSQL:**

```powershell
cd apps\api
$env:POSTGRES_PASSWORD = "your_postgres_password"
python scripts/init_postgres.py
```

After DB setup, run `.\scripts\start-all.ps1` (or `.\scripts\dev.ps1`) again.

---

## URLs after startup

| Service | URL | Purpose |
|---------|-----|---------|
| Web UI | http://localhost:5173 | RSM interface |
| API / Swagger | http://localhost:8000/docs | REST API |
| Demo CE | http://localhost:8090 | Test Correlation Engine (only with `start-all.ps1`) |

**Login:** `admin@omnisight.local` / `admin123`

---

## Manual startup (3 terminals)

If you need separate control over each process.

### Terminal 1 — Backend (API)

```powershell
cd apps\api
pip install -e ".[dev]"
python scripts/deploy_db.py --seed
python scripts/seed_demo.py
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2 — Frontend (Web)

```powershell
cd apps\web
npm install
npm run dev
```

### Terminal 3 — Test server (Demo CE)

```powershell
cd apps\demo-ce
pip install -r requirements.txt
python main.py
```

> Demo CE must start **after** the API — it sends alerts to `http://127.0.0.1:8000`.

---

## Stopping

Close the PowerShell windows with services (or `Ctrl+C` in each terminal).

PostgreSQL in Docker:

```powershell
docker compose -f docker\docker-compose.yml down
```

---

## Verify everything works

```powershell
# API
curl http://localhost:8000/health/live

# Demo CE (if running)
curl http://localhost:8090/health
```

API acceptance (20 checks):

```powershell
cd apps\api
python scripts\verify_demo_acceptance.py
```

Quick smoke (API pytest + web unit + build):

```powershell
.\scripts\smoke.ps1
```

In the browser: http://localhost:5173 — log in and open the correlation section; http://localhost:8090 — send a test alert.
