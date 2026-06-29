# OmniSight RSM

**Русская версия** · [English README](README.md)

**OmniSight** — платформа для учёта ИТ-ландшафта. Модуль **РСМ** (ресурсно-сервисная модель) ведёт каталог конфигурационных единиц (CI), направленных зависимостей между ними, визуализацию топологии и API для внешних систем мониторинга и корреляции алертов.

Стек: **FastAPI** (`apps/api`) + **React** (`apps/web`) + **PostgreSQL**.

| Документ | Назначение |
|----------|------------|
| [`docs/README.ru.md`](docs/README.ru.md) | ТЗ, сопоставление с реализацией, паспорт продукта |
| [`ARCHITECTURE.ru.md`](ARCHITECTURE.ru.md) | Слои, DI, async DB, паттерны фронтенда |
| [`fast_start/ЗАПУСК_WINDOWS.md`](fast_start/ЗАПУСК_WINDOWS.md) | Локальный запуск (Windows) |
| [`fast_start/ЗАПУСК_DOCKER.md`](fast_start/ЗАПУСК_DOCKER.md) | Запуск в Docker |
| [`fast_start/DEMO_GUIDE.ru.md`](fast_start/DEMO_GUIDE.ru.md) | Сценарий демо для жюри |

---

## Возможности

- **Инвентарь CI** — 11 типов, CRUD, внешние идентификаторы (hostname, IP, serviceCode и др.), атрибуты JSON, жизненный цикл, корзина
- **Связи** — 7 типов зависимостей, валидация (циклы, архив, битые ссылки)
- **Граф** — обход по глубине, business path, impact, layout, экспорт PNG
- **Autodiscover (карта)** — авто-сбор данных с серверов, черновой auto-mapping и автозаполнение полей с подтверждением
- **Import / Export** — JSON, CSV, XLSX; preview и сопоставление неизвестных типов при импорте (`/import/preview`, `/import/mapped`); отчёт по результатам
- **Корреляция** — batch resolve идентификаторов алертов, граф связей, `chain_related`
- **Аудит** — журнал изменений с diff old/new
- **RBAC** — роли viewer / editor / admin
- **i18n** — RU / EN, тёмная и светлая тема

---

## Требования

| Компонент | Версия |
|-----------|--------|
| Python | 3.12+ |
| Node.js | 20+ |
| PostgreSQL | 16+ |
| Docker (опционально) | для контейнера PostgreSQL или полного стека |

---

## Быстрый старт (Windows)

**UI + API** (два окна PowerShell):

```powershell
./scripts/dev.ps1
```

**UI + API + Demo CE** (три окна — для раздела корреляции):

```powershell
./scripts/start-all.ps1
```

Скрипты установят зависимости, создадут схему БД (если нет таблиц) и загрузят демо-данные.

| Сервис | URL |
|--------|-----|
| Web UI | http://localhost:5173 |
| API / Swagger | http://localhost:8000/docs |
| Demo CE | http://localhost:8090 (только `start-all.ps1`) |
| Логин | `admin@omnisight.local` / `admin123` |

Подробнее: [`fast_start/ЗАПУСК_WINDOWS.md`](fast_start/ЗАПУСК_WINDOWS.md)

---

## Запуск вручную

### 1. База данных

**Вариант A — локальный PostgreSQL**

```powershell
cd apps/api
pip install -e ".[dev]"
$env:POSTGRES_PASSWORD = "пароль_суперпользователя_postgres"
python scripts/init_postgres.py
```

Скрипт создаёт роль `omnisight`, базу `omnisight` и файл `.env` с `DATABASE_URL`.

**Вариант B — PostgreSQL в Docker** (см. раздел ниже).

### 2. Миграции и демо-данные

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

Полный стек: **PostgreSQL + API + Worker + Nginx (UI)** с healthcheck, JSON-логами, OpenAPI/Swagger и проверкой секретов при старте.

```powershell
cd docker
copy .env.example .env
# Заполните SECRET_KEY, API_KEY, WEBHOOK_SECRET, ADMIN_INITIAL_PASSWORD (openssl rand -hex 32)
docker compose -f docker-compose.prod.yml --env-file .env up -d --build
```

| Сервис | URL |
|--------|-----|
| Web UI | http://localhost:8080 |
| Swagger / OpenAPI | http://localhost:8080/docs · http://localhost:8080/openapi.json |
| Health (ready) | http://localhost:8080/health/ready |
| API (внутри сети Docker) | `api:8000` |

Worker (`python -m src.worker`) обрабатывает auto-sync scheduler и повторную доставку webhook outbox.

Повторный деплой без повторного seed: в `.env` установите `SEED_ON_START=0`.

Переменные production API (`APP_ENV=production`):

| Переменная | Назначение |
|------------|------------|
| `SECRET_KEY` | JWT, минимум 32 символа |
| `API_KEY` / `WEBHOOK_SECRET` | интеграции, минимум 24 символа |
| `ADMIN_INITIAL_PASSWORD` | пароль admin при первом seed (≥12 символов) |
| `CACHE_ENABLED=false` | обязательно при нескольких репликах без Redis; с `REDIS_URL` можно включить кэш |
| `DATABASE_ASYNC_ENABLED` | **true** по умолчанию — reads: native async ORM; writes: async write pool (asyncpg) |
| `REDIS_URL` | опционально: распределённый кэш для multi-replica (`redis://host:6379/0`) |
| `ENSURE_SCHEMA_ON_START=false` | в k8s: схема только через Job `k8s/schema-job.yaml` |
| `CORS_ORIGINS` | публичный URL UI |
| `TRUSTED_HOSTS` | хосты за reverse-proxy (опционально) |
| `RATE_LIMIT_MAX_REQUESTS` | лимит API-запросов на IP (по умолчанию 300/60s в compose) |
| `BACKGROUND_TASKS_ENABLED=false` | в API при нескольких репликах; фоновые задачи — в worker |
| `WEBHOOK_SYNC_DELIVERY=false` | enqueue only; worker доставляет с retries |

Локальный production-like запуск API:

```powershell
cd apps/api
$env:APP_ENV = "production"
$env:LOG_JSON = "true"
# ... остальные секреты из .env.example
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 2 --proxy-headers
```

Подробнее: [`fast_start/ЗАПУСК_DOCKER.md`](fast_start/ЗАПУСК_DOCKER.md)

---

## Запуск через Docker (только БД)

В репозитории есть `docker/docker-compose.yml` — поднимает только **PostgreSQL**. API и UI запускаются локально и подключаются к контейнеру.

### 1. Запустить PostgreSQL

```powershell
docker compose -f docker/docker-compose.yml up -d
```

Параметры контейнера:

| Параметр | Значение |
|----------|----------|
| Порт | `5432` |
| Пользователь | `omnisight` |
| Пароль | `omnisight` |
| База данных | `omnisight` |

### 2. Настроить `.env` для API

```powershell
cd apps/api
copy .env.example .env
```

В `.env` укажите:

```env
DATABASE_URL=postgresql+psycopg2://omnisight:omnisight@localhost:5432/omnisight
```

### 3. Миграции, демо-данные, запуск приложения

```powershell
cd apps/api
pip install -e ".[dev]"
python scripts/deploy_db.py --seed
python scripts/seed_demo.py
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

В другом терминале:

```powershell
cd apps/web
npm install
npm run dev
```

### Остановка контейнера

```powershell
docker compose -f docker/docker-compose.yml down
```

Данные сохраняются в Docker volume `pgdata`. Чтобы удалить и volume:

```powershell
docker compose -f docker/docker-compose.yml down -v
```

---

## Тесты

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

Быстрый smoke (API + web unit + build):

```powershell
./scripts/smoke.ps1
```

---

## Структура проекта

```
OmniSight/
├── apps/
│   ├── api/          # FastAPI, Alembic, worker, тесты, scripts/
│   ├── web/          # React + Vite, e2e/
│   └── demo-ce/      # тестовый Correlation Engine (порт 8090)
├── docker/           # compose: PostgreSQL, dev, prod (+ worker), HA
├── k8s/              # Kubernetes: API, worker, web, ingress, HPA, redis
├── docs/             # ТЗ, сопоставление, паспорт продукта
├── fast_start/       # инструкции запуска и демо-сценарий (EN + RU)
├── fixtures/         # domain-constants, демо-данные, drift-тесты
├── scripts/
│   ├── dev.ps1           # UI + API (локально)
│   ├── start-all.ps1     # UI + API + Demo CE
│   ├── docker-dev.ps1    # полный стек в Docker
│   └── smoke.ps1         # быстрая проверка CI
├── README.md             # English
└── README.ru.md          # Русский
```

Документация двуязычная: английские файлы — точка входа по умолчанию; у каждого есть русская версия (`.ru.md` или файл с русским именем) со ссылкой наверху.

---

## API

Каноническая версия API — **`/api/v1`** (UI, автоприёмка и интеграции), как в §8 ТЗ конкурса. См. [`docs/СОПОСТАВЛЕНИЕ_ТЗ.md`](docs/СОПОСТАВЛЕНИЕ_ТЗ.md).

Основные группы эндпоинтов:

- `/api/v1/auth` — login, users, смена пароля
- `/api/v1/ci`, `/api/v1/ci/types` — CRUD, типы, import/export, preview/mapped import
- `/api/v1/relations` — CRUD, validate, import/export
- `/api/v1/resources/*` — поиск, граф, impact, components, business-path, resolve, graph-layout
- `/api/v1/correlation/*` — ingest, context, chain-check
- `/api/v1/autodiscover/*` — коннекторы, сканирование, apply
- `/api/v1/dashboard` — метрики обзора
- `/api/v1/audit` — журнал аудита
- `/api/v1/meta` — версия схемы, константы
- `/health`, `/health/live`, `/health/ready` — проверка состояния (ready → 503 без БД)

Полная спецификация: http://localhost:8000/docs · файл `apps/api/openapi.json`

Автоприёмка по FR 1–54:

```powershell
cd apps/api
python scripts/seed_demo.py
python scripts/verify_demo_acceptance.py   # ожидается 20/20 PASS
```

---

## Лицензия

[MIT](LICENSE)
