"""OpenAPI tag names — Integration API (§8) vs Admin API."""

from __future__ import annotations

TAG_INTEGRATION_RESOURCES = "Integration API · Resources (§8)"
TAG_INTEGRATION_CORRELATION = "Integration API · Correlation (§8)"
TAG_INTEGRATION_META = "Integration API · Meta"

TAG_ADMIN_CI = "Admin API · CI"
TAG_ADMIN_RELATIONS = "Admin API · Relations"
TAG_ADMIN_CI_TYPES = "Admin API · CI Types"
TAG_ADMIN_RELATION_TYPES = "Admin API · Relation Types"
TAG_ADMIN_AUTODISCOVER = "Admin API · Autodiscover"
TAG_ADMIN_AUDIT = "Admin API · Audit"
TAG_ADMIN_DASHBOARD = "Admin API · Dashboard"
TAG_ADMIN_AUTH = "Admin API · Auth"

OPENAPI_TAGS: list[dict[str, str]] = [
    {
        "name": TAG_INTEGRATION_RESOURCES,
        "description": (
            "Контракт ТЗ §8 для correlation engine и внешних систем мониторинга: "
            "поиск объектов, карточка, связи, граф, impact, batch resolve."
        ),
    },
    {
        "name": TAG_INTEGRATION_CORRELATION,
        "description": ("Корреляционный контекст ТЗ §8: общий граф по группе объектов, ingest, chain-check."),
    },
    {
        "name": TAG_INTEGRATION_META,
        "description": "Справочные константы модели и версия схемы для клиентов.",
    },
    {
        "name": TAG_ADMIN_CI,
        "description": (
            "Управление элементами РСМ (CRUD, импорт/экспорт, корзина). "
            "Для интеграций используйте Integration API · Resources."
        ),
    },
    {
        "name": TAG_ADMIN_RELATIONS,
        "description": "Управление направленными связями между элементами РСМ.",
    },
    {
        "name": TAG_ADMIN_CI_TYPES,
        "description": "Справочник типов CI (только администратор).",
    },
    {
        "name": TAG_ADMIN_RELATION_TYPES,
        "description": "Справочник типов связей (только администратор).",
    },
    {
        "name": TAG_ADMIN_AUTODISCOVER,
        "description": "Autodiscover: сканирование серверов и применение черновика полей/связей.",
    },
    {
        "name": TAG_ADMIN_AUDIT,
        "description": "Журнал аудита изменений модели, импортов и экспортов.",
    },
    {
        "name": TAG_ADMIN_DASHBOARD,
        "description": "Сводка по модели для UI (KPI, целостность).",
    },
    {
        "name": TAG_ADMIN_AUTH,
        "description": "Аутентификация, пользователи и смена пароля.",
    },
]

OPENAPI_TAG_GROUPS: list[dict[str, object]] = [
    {
        "name": "Integration API (ТЗ §8)",
        "tags": [
            TAG_INTEGRATION_RESOURCES,
            TAG_INTEGRATION_CORRELATION,
            TAG_INTEGRATION_META,
        ],
    },
    {
        "name": "Admin API (UI и сопровождение модели)",
        "tags": [
            TAG_ADMIN_AUTH,
            TAG_ADMIN_CI,
            TAG_ADMIN_RELATIONS,
            TAG_ADMIN_CI_TYPES,
            TAG_ADMIN_RELATION_TYPES,
            TAG_ADMIN_AUTODISCOVER,
            TAG_ADMIN_AUDIT,
            TAG_ADMIN_DASHBOARD,
        ],
    },
]
