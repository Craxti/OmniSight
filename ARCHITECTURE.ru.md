# Архитектура OmniSight

**Русская версия** · [English](ARCHITECTURE.md)

## Слоистая структура

### Backend (`apps/api`)

```
api/v1  >  core/deps/  >  services/*  >  repositories/*  >  models/
```

| Слой | Ответственность | Может импортировать |
|-------|----------------|------------|
| `api/` | HTTP-маршрутизация, аутентификация, привязка DTO | `services/`, `schemas/`, `core/deps` |
| `services/` | Доменная логика, оркестрация | `repositories/`, `models/`, `schemas/`, `core/` |
| `repositories/` | Доступ к данным через SQLAlchemy | `models/`, `core/` ? **не** `services/` |
| `core/` | Инфраструктура: auth, cache, DB, DI | `models/` в ограниченном объёме |

**Политика транзакций** (`core/async_unit_of_work.py`, `core/session_commit.py`):

- CRUD-сервисы выполняют commit после каждой успешной мутации
- Пайплайны импорта группируют мутации; вызывающий код выполняет commit один раз через `async_transactional_write_session`
- Пути только для чтения никогда не выполняют commit

**Доступ к базе данных:**

| Модуль | Использование |
|--------|-----|
| `core/database_async.py` | Все HTTP-обработчики, runtime воркера, async cache API |
| `core/database.py` | Синхронный `engine` + `sync_session()` ? bootstrap схемы, CLI-скрипты, legacy sync cache helpers |
| `core/migrations.py` + `alembic/` | Эволюция схемы (`alembic upgrade head`, brownfield `stamp head`) |
| `core/sync_transaction.py` | Legacy deferred-commit sync session (тесты / bridged imports) |

### Frontend (`apps/web`)

```
features/*/XPage.tsx  >  hooks/useXPage.ts  >  shared/api/*  +  shared/components/*
```

| Слой | Может импортировать |
|-------|------------|
| `features/` | `shared/`, `lib/`, `context/` |
| `shared/` | `shared/`, `lib/` ? **не** `features/` |
| `shared/components/graph/` | Canvas графа, легенда, встроенная read-only панель |
| `components/` (shell) | `Layout`, `ProtectedRoute`, `PageLoader`, `ui.tsx` barrel ? **не** `features/` |
| `shared/components/` | Переиспользуемый UI: таблицы, формы, модалки (`ui-primitives`, `EnvironmentInput`), canvas графа |

**Правила импорта:**

- App shell только из `@/components/*`
- Переиспользуемые виджеты из `@/shared/components/*` или `@/components/ui` (barrel re-exports shared primitives)
- **Не** импортировать `@/components/Modal` ? использовать `@/components/ui`
- Использовать path alias `@/` (`@/shared/...`, `@/features/...`) для всех импортов

Стили находятся в `src/styles/` (`tokens.css`, `theme.css`, `base.css`, `components.css`, `graph.css`, `layout.css`), импортируются через `src/index.css`. См. **`apps/web/docs/STYLING.md`** — когда использовать Tailwind vs CSS classes vs tokens.

**Общий клиентский контракт:** `packages/omnisight-contract` (`@omnisight/contract`) ? доменные константы для web и будущих клиентов; генерируется `sync_domain_constants.py`.

**Design tokens** (`tokens.css`): радиусы, отступы, размер caption (`--rsm-font-caption`), семантическая палитра (`--rsm-color-*`). Theme-aware semantic text и alerts (`--text-warning`, `--alert-warning-*` и т.д.) находятся в `theme.css`. UI-классы: `.btn-*`, `.alert-*`, `.hint`, `.text-warning` в `components.css`.

Страницы маршрутов используют `React.lazy()` + `Suspense` в `App.tsx`. Тяжёлые vendor chunks: `vite.config.ts` `manualChunks`.

Path alias: `@/` > `src/` (Vite + `tsconfig.app.json`) ? **использовать для всех новых и мигрированных импортов**.

## Внедрение зависимостей (API)

Провайдеры находятся в `core/deps/` (`read.py`, `write.py`, `domain.py`). Re-export из `core.deps` для импортов в routes.

Write path ? `core/deps/write.py` (`get_*_write_port`, transactional variants):

- `get_ci_write_port`, `get_relation_write_port`, `get_graph_layout_write_port`, `get_correlation_write_port`
- `get_user_write_port`, `get_ci_type_write_port`, `get_ci_import_export_write_port`, `get_autodiscover_write_port`
- `get_transactional_ci_import_export_write_port`, `get_transactional_autodiscover_write_port`
- Legacy aliases: `get_ci_service`, `get_relation_service`, ? (те же провайдеры)

Обработчики вызывают `await write_service.method(...)`. Все HTTP-мутации используют **async write pool**:

- **Native async ORM:** CI, relations, CI types, graph layout, users, correlation ingest
- **Bridged ``await session.run_sync``:** CI/relation import-export, autodiscover (connector CRUD, scan)
- **Transactional async write pool:** mapped import apply, autodiscover apply (`async_transactional_write_session`, deferred commit)

Read path ? `core/deps/read.py` (`get_*_read_port`, optional `DATABASE_READ_URL` replica):

- `get_ci_read_port`, `get_relation_read_port`, `get_topology_read_port`, `get_dashboard_read_port`
- `get_search_read_port`, `get_correlation_read_port`, `get_graph_layout_read_port`
- `get_audit_read_port`, `get_user_read_port`, `get_ci_type_read_port`
- `get_ci_import_export_read_port`, `get_relation_import_export_read_port`, `get_autodiscover_read_port`
- Legacy aliases: `get_read_ci_service`, `get_search_service`, ? (те же провайдеры)

Обработчики вызывают `await read_service.method(...)` на native async read services.

Auth JWT / API-key lookup ? `core/auth_lookup.py` (`AsyncUserRepository` on async read pool).

Worker / rate-limit / postgres cache ? `await run_sync_on_write_session` (no thread-pool DB fallback).

## Доменные модули

| Домен | Точка входа сервиса | Примечания |
|--------|---------------|-------|
| CI | `CiService` | Facade над CRUD + lifecycle |
| CI types | `CiTypeService` | Кастомные типы, admin CRUD |
| CI I/O | `CiImportExportService` | JSON/CSV/XLSX/RSM; `import_type_mapping` для неизвестных типов |
| Relations | `RelationService` | CRUD + validation |
| Relations I/O | `RelationImportExportService` | CSV/JSON import/export |
| Topology | `TopologyService` | Graph, impact, components, business path |
| Search | `SearchService` | Поиск по external ID / атрибутам |
| Graph layout | `GraphLayoutService` | Сохранённые позиции узлов |
| Correlation | `CorrelationService` | Ingest, context, chain-check |
| Auth | `UserService` | Администрирование пользователей, login |
| Audit | `AuditService` | Query + helper `log_audit()` |
| Dashboard | `DashboardService` | Агрегаты для overview |
| Autodiscover | `AutodiscoverService` | Connectors, scan, apply |
| Export formats | `services/export/registry.py` | Pluggable CSV/XLSX/RSM |

Общие SQL / filter builders: `repositories/queries/*` (CI, relations, audit, topology edges).

## Общие константы

Доменные константы находятся в `fixtures/domain-constants.json`, синхронизируются в:

- `apps/api/src/core/constants.py`
- `apps/web/src/shared/domainConstants.generated.ts`

Drift tests защищают обе стороны.

**Web entity types:** `apps/api/scripts/export_web_types.py` генерирует `apps/web/src/shared/api/types.generated.ts` из Pydantic schemas (`npm run codegen:api`). `types.ts` re-exports с frontend aliases (`CI`, `Relation`, ?). Drift test: `test_web_types_export.py`.

## Паттерны frontend

- **Page hooks**: `useXPage` хранит state + queries; компонент страницы остаётся thin
- **Mutations**: предпочтительно `useApiMutation` + `shared/queryInvalidation.ts`
- **Query keys**: централизованы в `shared/queryKeys.ts`
- **Forms**: React Hook Form + Zod schemas в `lib/forms/schemas/`; общий wrapper `FormField`
- **Cross-feature modals**: переиспользуемые flows (например, autodiscover, import type mapping) находятся в `shared/components/`, не в `features/`
- **Tables**: `VirtualDataTable` (`@tanstack/react-virtual`) + server-side pagination для больших списков
- **Modals**: канонические `Modal` / `AppDialog` в `shared/components/ui-primitives.tsx`, экспортируются через `components/ui.tsx`

## Чеклист SOLID

- **SRP**: один service class на доменную зону ответственности; разделение fat modules (pipeline, graph) со временем
- **OCP**: export registry, autodiscover connector protocol
- **DIP**: `repositories/protocols.py` + repository factories в `core/deps/`
- **Canonical CI API (v1)**: `GET /api/v1/ci/{id}`, `GET /api/v1/ci/{id}/relations`; topology на `/api/v1/resources/{id}/graph|impact|...`

## Асинхронный доступ к данным (API)

`DATABASE_ASYNC_ENABLED=true` по умолчанию (PostgreSQL через asyncpg).

| Путь | Импорт | Когда |
|------|--------|------|
| **HTTP reads (v1)** | `Depends(get_*_read_port)` | Native `Async*ReadService` или `SyncReadPort` fallback |
| **HTTP writes (v1)** | `Depends(get_*_write_port)` | Async write pool: native ORM или ``session.run_sync`` bridge; transactional routes исключены |
| **Writes (legacy)** | `core.db_access.run_write` | Только worker / internal callers |
| **Transactional writes** | `run_in_threadpool` / sync `Session` | Routes с `get_transactional_db` (deferred commit в конце запроса) |
| **Fallback** | `core.db_access.run_sync` | `DATABASE_ASYNC_ENABLED=false` |

`core/db_access.py` оборачивает `async_db.run_db` named helpers (`run_read`, `run_write`, `run_sync`) и decision-tree docstring ? предпочтительно использовать его вместо прямого вызова `run_db` в новых routes.

Optional `DATABASE_READ_URL` направляет async reads на replica.

### Выбор пути доступа к DB

| Нужно | Использовать |
|------|-----|
| Default HTTP read (v1) | Inject `get_*_read_port`; `await service.method(...)` |
| Default HTTP write / CRUD | Inject `get_*_write_port`; `await service.method(...)` |
| Multi-step import / autodiscover apply | `get_transactional_*` + deferred commit в конце запроса |
| Unit tests / `DATABASE_ASYNC_ENABLED=false` | `await run_sync(fn)` + sync `Session` |
| Worker / scheduler | `run_worker_write()` |

Pool sizing (`DATABASE_POOL_SIZE`, `DATABASE_MAX_OVERFLOW`, default 3+5): каждый uvicorn worker держит **read + write** async pools. Безопасная верхняя граница:

`api_replicas ? UVICORN_WORKERS ? (pool_size + max_overflow) ? 2 < postgres_max_connections`

С k8s defaults (HPA max 4, workers 2): ceiling ? **128** connections. Использовать PgBouncer перед повышением HPA или pool caps.

### Консолидация async/sync read (завершена для HTTP read paths)

Sync services и `Async*ReadService` adapters разделяют assembly ответов в **`services/domain/`** для всех доменов с async read twins (CI, audit, dashboard, relations, search, correlation, users, ci_types, graph_layout, autodiscover, import/export reads, topology guards). Graph/topology **алгоритмы** (BFS, impact, business path, chain check) находятся в **`services/rsm/topology_algorithms.py`** с thin sync/async repo adapters в `graph` / `async_graph` и `topology` / `async_topology`.

**Постепенные follow-ups:**

| Фаза | Действие | Статус |
|-------|--------|--------|
| 1. **Query modules** | Shared SQL / filter builders в `repositories/queries/*` | CI, relations, audit, topology edges |
| 2. **Read protocols** | Расширить `repositories/protocols.py` async variants | **done** (CI, relations, audit, users, ci_types) |
| 3. **Thin async adapters** | `Async*ReadService` делегирует в `services/domain/*` | **done** (все async_read modules) |
| 4. **Read-path tests** | `test_handler_read_envelopes.py`, `test_topology_algorithms.py`, `test_async_orm.py`, `test_async_topology.py`, `test_async_validation.py`, `test_write_port_registry.py`, `test_inventory_handlers.py`, `test_v1_envelopes.py` | **done** |

**HTTP write path полностью async** при `DATABASE_ASYNC_ENABLED=true` (default). Import/autodiscover apply сохраняет sync transactional session для multi-row atomic commit; worker/scheduler использует `run_worker_write()`.

### Структура Autodiscover

| Путь | Роль |
|------|------|
| `services/autodiscover/discovery/` | Collectors + inference (SSH, Docker, K8s) |
| `services/autodiscover/connectors/` | Connector registry |
| `services/autodiscover/runtime/` | Async orchestration (scan, apply, auto-sync) ? ранее `async_autodiscover/` |
| `services/async_read/autodiscover.py` | HTTP read adapter |
| `services/async_write/autodiscover.py` | HTTP write adapter |
| `services/domain/autodiscover.py` | Shared list/summary builders |

| Фаза | Действие | Статус |
|-------|--------|--------|
| 5. **Native async CI writes** | `AsyncCiWriteService` | **done** |
| 6. **Native async relation writes** | `AsyncRelationWriteService` | **done** |
| 7. **Native async CI type writes** | `AsyncCiTypeWriteService` | **done** |
| 8. **Native async graph layout writes** | `AsyncGraphLayoutWriteService` | **done** |
| 9. **Native async user writes** | `AsyncUserWriteService` | **done** |
| 10. **Native async correlation ingest** | `AsyncCorrelationWriteService` | **done** |
| 11. **Bridged import/autodiscover writes** | `AsyncSessionWriteBridge` | **done** |
| 12. **Write-path tests** | `test_write_port_registry.py`, `test_transactional_deps.py`, `test_ci_type_delete.py`, `test_async_validation.py` | **done** |

### Ментальная модель read path (после консолидации)

| Слой | Роль |
|-------|------|
| `core/deps/read.py` | Request-scoped `Async*ReadService` (или `SyncReadPort` fallback) |
| `services/domain/*` | Shared response builders и orchestration |
| `services/async_read/*` | Thin `async def` adapters над `services/domain/*` + async repos |
| Handlers | `await read_service.method(...)` / `await write_service.method(...)` |

`run_read` / `run_write` остаются для worker и legacy internal callers.

Read/write coverage: async read envelopes и domain builders покрыты `tests/unit/test_handler_read_envelopes.py`, `test_v1_envelopes.py` и `test_write_port_registry.py`. Relation validation sync/async parity находится в `tests/unit/test_async_validation.py`.

## Фоновая работа и масштабирование

| Процесс | Команда | Ответственность | DB access |
|---------|---------|----------------|-----------|
| API | `uvicorn src.main:app` | HTTP; `BACKGROUND_TASKS_ENABLED=false` в multi-replica prod | Async read/write pools |
| Worker | `python -m src.worker` | Auto-sync scheduler + webhook outbox retry | `run_worker_write()` |

Worker batches вызывают `core/worker_db.run_worker_write()` ? sync ORM через `AsyncSession.run_sync` на asyncpg при `DATABASE_ASYNC_ENABLED=true`.

| Настройка | Назначение |
|---------|---------|
| `WEBHOOK_SYNC_DELIVERY=false` | Только enqueue; worker доставляет с retries |
| `REDIS_URL` | Distributed cache (`CACHE_ENABLED=true` в k8s при развёрнутом Redis) |
| `DATABASE_READ_URL` | Read replica для dashboard/graph/search (optional; задать в secrets) |
| `DATABASE_POOL_SIZE` / `DATABASE_MAX_OVERFLOW` | Per-engine connection caps (default 3/5) |

K8s manifests: `k8s/` (API HPA, web HPA, worker, web, migration Job). HA Postgres sample: `docker/docker-compose.ha.yml`.

**Масштабирование worker:** держать scheduler на 1 replica (advisory lock). Outbox consumer может масштабироваться горизонтально (`SKIP LOCKED`). Разделить на отдельные deployments при росте auto-sync load.

**Масштабирование write:** imports/autodiscover/correlation пишут в primary; read replicas не разгружают writes ? ставить тяжёлые imports в очередь или шардировать по tenant, если write load доминирует.
