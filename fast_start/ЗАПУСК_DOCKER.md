# Запуск OmniSight в Docker

Три сервиса в dev-compose: **PostgreSQL**, **Backend (API)**, **Frontend (Web через Nginx)**.  
Production-compose добавляет **Worker** (auto-sync, webhook outbox).

См. также: [`../README.md`](../README.md) · [`ЗАПУСК_WINDOWS.md`](./ЗАПУСК_WINDOWS.md) · [`DEMO_GUIDE.md`](./DEMO_GUIDE.md)

---

## Быстрый старт (Windows)

1. Установите [Docker Desktop](https://www.docker.com/products/docker-desktop/) и запустите его.
2. Из корня репозитория:

```powershell
.\scripts\docker-dev.ps1
```

Скрипт создаст `docker/.env` (если его нет), соберёт образы и поднимет контейнеры.

---

## Ручной запуск (dev)

```powershell
cd docker
copy .env.dev.example .env
docker compose -f docker-compose.dev.yml --env-file .env up -d --build
```

Первый запуск занимает несколько минут (сборка образов API и Web).

---

## Адреса

| Сервис | URL | Описание |
|--------|-----|----------|
| Web UI | http://localhost:8080 | Интерфейс (Nginx проксирует `/api` на backend) |
| API / Swagger | http://localhost:8000/docs | REST API напрямую (порт проброшен в dev-compose) |
| Health | http://localhost:8000/health/ready | Готовность API + БД |

**Логин:** `admin@omnisight.local` / `admin123`

При первом старте API автоматически создаёт таблицы (если их нет) и seed (`SEED_ON_START=1`).

---

## Полезные команды

```powershell
cd docker

# Логи всех сервисов
docker compose -f docker-compose.dev.yml logs -f

# Логи только API
docker compose -f docker-compose.dev.yml logs -f api

# Остановить (данные БД сохраняются)
docker compose -f docker-compose.dev.yml down

# Остановить и удалить volume с данными БД
docker compose -f docker-compose.dev.yml down -v

# Пересобрать после изменений в коде
docker compose -f docker-compose.dev.yml up -d --build
```

---

## Файлы Docker в репозитории

| Файл | Назначение |
|------|------------|
| `docker/docker-compose.dev.yml` | **Dev/demo**: БД + API + Web, простые секреты, Swagger включён |
| `docker/docker-compose.yml` | Только PostgreSQL (API и UI запускаются локально) |
| `docker/docker-compose.prod.yml` | **Production**: БД + API + Worker + Web, строгие секреты |
| `docker/docker-compose.ha.yml` | Пример HA PostgreSQL (Patroni) |
| `apps/api/Dockerfile` | Образ FastAPI + worker |
| `apps/web/Dockerfile` | Сборка React + Nginx |
| `docker/.env.dev.example` | Пример переменных для dev |
| `docker/.env.example` | Пример переменных для production |

---

## Production

```powershell
cd docker
copy .env.example .env
# Заполните SECRET_KEY, API_KEY, WEBHOOK_SECRET, ADMIN_INITIAL_PASSWORD
docker compose -f docker-compose.prod.yml --env-file .env up -d --build
```

| Сервис | Доступ |
|--------|--------|
| Web UI | http://localhost:8080 (или `WEB_PORT` из `.env`) |
| API | только внутри Docker-сети; снаружи — через Nginx на `/api` |
| Worker | фоновый процесс, порт не публикуется |

Повторный деплой без seed: `SEED_ON_START=0` в `.env`.

---

## Demo CE (тестовый Correlation Engine)

В Docker-compose **не включён** — запускайте локально после поднятия стека:

```powershell
cd apps\demo-ce
pip install -r requirements.txt
$env:RSM_URL = "http://127.0.0.1:8000"
python main.py
```

Demo CE: http://localhost:8090

> При полном Docker-стеке API доступен на `localhost:8000` (dev) или через Nginx `/api` на `8080`. Demo CE по умолчанию шлёт на `http://127.0.0.1:8000`.

---

## Отличие от локального запуска

| | Docker (`docker-dev.ps1`) | Локально (`dev.ps1` / `start-all.ps1`) |
|--|---------------------------|----------------------------------------|
| UI | http://localhost:8080 (Nginx, prod-сборка) | http://localhost:5173 (Vite dev, hot reload) |
| API | контейнер, порт 8000 | uvicorn --reload |
| БД | контейнер PostgreSQL | локально или отдельный контейнер |
| Demo CE | запуск вручную | `start-all.ps1` поднимает автоматически |
| Hot reload | нет (нужен `--build` после правок) | да |

Для разработки UI удобнее локальный `npm run dev`; для демо и проверки «как в проде» — Docker.
