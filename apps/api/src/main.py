import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from src.api.v1 import audit as audit_v1
from src.api.v1 import auth as auth_v1
from src.api.v1 import autodiscover as autodiscover_v1
from src.api.v1 import ci as ci_v1
from src.api.v1 import ci_types as ci_types_v1
from src.api.v1 import correlation as correlation_v1
from src.api.v1 import dashboard as dashboard_v1
from src.api.v1 import meta as meta_v1
from src.api.v1 import relation_types as relation_types_v1
from src.api.v1 import relations as relations_v1
from src.api.v1 import resources as resources_v1
from src.core.background_tasks import start_api_background_tasks, stop_api_background_tasks
from src.core.config import settings
from src.core.database_async import async_engine_enabled, dispose_async_engines
from src.core.exceptions import ConflictError, DomainValidationError, NotFoundError
from src.core.health import readiness_response
from src.core.logging_config import setup_logging
from src.core.middleware import RateLimitMiddleware, RequestLoggingMiddleware, SecurityHeadersMiddleware
from src.core.openapi_schema import apply_custom_openapi
from src.core.openapi_tags import OPENAPI_TAGS
from src.core.production import validate_production_settings

logger = logging.getLogger("omnisight.api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging(settings)
    validate_production_settings(settings)
    if not os.getenv("SKIP_DB_INIT") and not os.getenv("SKIP_MIGRATIONS"):
        from src.core.schema import bootstrap_database

        if settings.ensure_schema_on_start:
            bootstrap_database(seed=True)
    if settings.is_production:
        logger.info("Starting OmniSight API in production mode")
    scheduler_task = start_api_background_tasks()
    try:
        yield
    finally:
        await stop_api_background_tasks(scheduler_task)
        if async_engine_enabled():
            await dispose_async_engines()


_fastapi_kwargs: dict = {
    "title": settings.app_name,
    "version": "2.0.0",
    "description": (
        "Ресурсно-сервисная модель (РСМ) — API v1 для учёта элементов, связей и корреляции алертов.\n\n"
        "**Integration API (ТЗ §8)** — `Resources`, `Correlation`, `Meta`: контракт для correlation engine "
        "и внешних систем мониторинга.\n\n"
        "**Admin API** — `CI`, `Relations`, справочники, Autodiscover, аудит: ведение модели через UI "
        "и администрирование."
    ),
    "openapi_tags": OPENAPI_TAGS,
    "lifespan": lifespan,
}
if settings.is_production and not settings.docs_enabled:
    _fastapi_kwargs.update(docs_url=None, redoc_url=None, openapi_url=None)

app = FastAPI(**_fastapi_kwargs)
apply_custom_openapi(app)


@app.exception_handler(NotFoundError)
async def handle_not_found(_: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.message})


@app.exception_handler(ConflictError)
async def handle_conflict(_: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": exc.message})


@app.exception_handler(DomainValidationError)
async def handle_validation(_: Request, exc: DomainValidationError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": exc.message})


@app.exception_handler(ValueError)
async def handle_value_error(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


if settings.trusted_hosts_list:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts_list)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list or (["*"] if not settings.is_production else []),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    max_requests=settings.rate_limit_max_requests,
    window_seconds=settings.rate_limit_window_seconds,
)

app.include_router(auth_v1.router, prefix="/api/v1")
app.include_router(resources_v1.router, prefix="/api/v1")
app.include_router(meta_v1.router, prefix="/api/v1")
app.include_router(dashboard_v1.router, prefix="/api/v1")
app.include_router(audit_v1.router, prefix="/api/v1")
app.include_router(correlation_v1.router, prefix="/api/v1")
app.include_router(ci_types_v1.router, prefix="/api/v1")
app.include_router(ci_v1.router, prefix="/api/v1")
app.include_router(relation_types_v1.router, prefix="/api/v1")
app.include_router(relations_v1.router, prefix="/api/v1")
app.include_router(autodiscover_v1.router, prefix="/api/v1")


@app.get("/health/live")
async def health_live():
    return {"status": "ok", "service": "omnisight-api"}


@app.get("/health/ready")
async def health_ready():
    return await readiness_response()


@app.get("/health")
async def health():
    return await health_ready()
