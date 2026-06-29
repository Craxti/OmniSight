"""Custom OpenAPI schema extensions."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from src.core.openapi_tags import OPENAPI_TAG_GROUPS


def apply_custom_openapi(app: FastAPI) -> None:
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=app.openapi_tags,
        )
        schema["x-tagGroups"] = OPENAPI_TAG_GROUPS
        schemes = schema.setdefault("components", {}).setdefault("securitySchemes", {})
        bearer = schemes.setdefault("HTTPBearer", {"type": "http", "scheme": "bearer"})
        bearer["description"] = (
            "JWT из `POST /api/v1/auth/token` (поле `session.access_token`). В Authorize вставьте только токен."
        )
        schemes["XApiKey"] = {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "Ключ интеграции для correlation ingest и внешних систем.",
        }
        webhook = schemes.get("APIKeyHeader")
        if webhook:
            webhook["name"] = "X-Webhook-Secret"
            webhook["description"] = "Секрет webhook-интеграций."
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi  # type: ignore[method-assign]
