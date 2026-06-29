# Документация OmniSight РСМ

Документы в этой папке соответствуют ТЗ конкурса (текстовая копия: [`_requirements_extract.txt`](./_requirements_extract.txt)).

| Документ | Содержание |
|----------|------------|
| [**_requirements_extract.txt**](./_requirements_extract.txt) | Полный текст ТЗ (FR 1–54, §8) |
| [**СОПОСТАВЛЕНИЕ_ТЗ.md**](./СОПОСТАВЛЕНИЕ_ТЗ.md) | Таблица: пункты ТЗ ↔ реализация |
| [**product-passport/ПАСПОРТ_ПРОДУКТА.md**](./product-passport/ПАСПОРТ_ПРОДУКТА.md) | Паспорт продукта, скриншоты, сценарии |

Запуск и демо: [`../fast_start/ЗАПУСК_WINDOWS.md`](../fast_start/ЗАПУСК_WINDOWS.md) · [`../fast_start/ЗАПУСК_DOCKER.md`](../fast_start/ЗАПУСК_DOCKER.md) · [`../fast_start/DEMO_GUIDE.md`](../fast_start/DEMO_GUIDE.md)

Архитектура кода: [`../ARCHITECTURE.md`](../ARCHITECTURE.md)

## API

Каноническая версия — **`/api/v1`** (UI, автоприёмка, OpenAPI). В §8 ТЗ указаны пути `/api/v1/...` — функционально эквивалентны v1; см. [`СОПОСТАВЛЕНИЕ_ТЗ.md`](./СОПОСТАВЛЕНИЕ_ТЗ.md).

Спецификация (FR 43):

| Окружение | Swagger | OpenAPI JSON |
|-----------|---------|--------------|
| Dev (локально) | http://localhost:8000/docs | http://localhost:8000/openapi.json |
| Docker / prod compose | http://localhost:8080/docs | http://localhost:8080/openapi.json |
| Файл в репозитории | — | `apps/api/openapi.json` |

## Быстрый старт

**Только UI + API:**

```powershell
./scripts/dev.ps1
```

**UI + API + Demo CE** (корреляция, тестовые алерты):

```powershell
./scripts/start-all.ps1
```

**Полный стек в Docker** (PostgreSQL + API + Web):

```powershell
./scripts/docker-dev.ps1
```

| URL | Назначение |
|-----|------------|
| http://localhost:5173 | UI (локальный Vite) |
| http://localhost:8080 | UI (Docker / prod compose) |
| http://localhost:8000/docs | Swagger (API напрямую) |
| http://localhost:8090 | Demo CE (только `start-all.ps1`) |

Логин: `admin@omnisight.local` / `admin123`

## Автоприёмка

```powershell
cd apps/api
python scripts/seed_demo.py
python scripts/verify_demo_acceptance.py   # 20 проверок, ожидается 20/20 PASS
pytest tests/ -q                           # fast local run (no coverage)
pytest tests/ -q --cov=src --cov-report=term-missing:skip-covered --cov-fail-under=80  # CI gate
```

Быстрый smoke (API pytest + web unit + build):

```powershell
./scripts/smoke.ps1
```

Пересборка docx из текста ТЗ: `python scripts/build_requirements_docx.py`
