# Запуск OmniSight на Windows

Фронтенд, бэкенд и тестовый Correlation Engine (Demo CE) — один скрипт или три терминала вручную.

> **Всё в Docker (БД + API + Web):** см. [`ЗАПУСК_DOCKER.md`](./ЗАПУСК_DOCKER.md) — `.\scripts\docker-dev.ps1`

См. также: [`../README.md`](../README.md) · [`DEMO_GUIDE.md`](./DEMO_GUIDE.md) · [`../docs/README.md`](../docs/README.md)

## Требования

| Компонент | Версия |
|-----------|--------|
| Python | 3.12+ |
| Node.js | 20+ |
| PostgreSQL | 16+ (локально или Docker) |

---

## Быстрый способ — один скрипт

Из **корня репозитория** в PowerShell:

```powershell
.\scripts\start-all.ps1
```

Скрипт:

1. Установит Python-зависимости API и Demo CE
2. Создаст схему БД при необходимости (`deploy_db.py --seed`) и загрузит демо-данные (`seed_demo.py`)
3. Откроет **3 окна PowerShell**:
   - **Backend** (FastAPI) — порт `8000`
   - **Frontend** (React/Vite) — порт `5173`
   - **Тестовый сервер** (Demo CE) — порт `8090`

**Только UI + API** (без Demo CE):

```powershell
.\scripts\dev.ps1
```

### Если PowerShell блокирует скрипт

Один раз (от имени пользователя, не администратора):

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Либо запуск без смены политики:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-all.ps1
```

### Первый запуск — база данных

**Вариант A — PostgreSQL в Docker** (проще):

```powershell
docker compose -f docker\docker-compose.yml up -d
cd apps\api
copy .env.example .env
```

В `.env` должно быть:

```env
DATABASE_URL=postgresql+psycopg2://omnisight:omnisight@localhost:5432/omnisight
```

**Вариант B — локальный PostgreSQL:**

```powershell
cd apps\api
$env:POSTGRES_PASSWORD = "ваш_пароль_postgres"
python scripts/init_postgres.py
```

После настройки БД снова запустите `.\scripts\start-all.ps1` (или `.\scripts\dev.ps1`).

---

## Адреса после запуска

| Сервис | URL | Назначение |
|--------|-----|------------|
| Web UI | http://localhost:5173 | Интерфейс РСМ |
| API / Swagger | http://localhost:8000/docs | REST API |
| Demo CE | http://localhost:8090 | Тестовый Correlation Engine (только `start-all.ps1`) |

**Логин:** `admin@omnisight.local` / `admin123`

---

## Ручной запуск (3 терминала)

Если нужен контроль над каждым процессом отдельно.

### Терминал 1 — Backend (API)

```powershell
cd apps\api
pip install -e ".[dev]"
python scripts/deploy_db.py --seed
python scripts/seed_demo.py
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

### Терминал 2 — Frontend (Web)

```powershell
cd apps\web
npm install
npm run dev
```

### Терминал 3 — Тестовый сервер (Demo CE)

```powershell
cd apps\demo-ce
pip install -r requirements.txt
python main.py
```

> Demo CE должен стартовать **после** API — он шлёт алерты на `http://127.0.0.1:8000`.

---

## Остановка

Закройте окна PowerShell с сервисами (или `Ctrl+C` в каждом терминале).

PostgreSQL в Docker:

```powershell
docker compose -f docker\docker-compose.yml down
```

---

## Проверка, что всё работает

```powershell
# API
curl http://localhost:8000/health/live

# Demo CE (если запущен)
curl http://localhost:8090/health
```

Автоприёмка API (20 проверок):

```powershell
cd apps\api
python scripts\verify_demo_acceptance.py
```

Быстрый smoke (pytest API + web unit + build):

```powershell
.\scripts\smoke.ps1
```

В браузере: http://localhost:5173 — войти и открыть раздел корреляции; http://localhost:8090 — отправить тестовый алерт.
