"""Health check payloads for liveness and readiness probes."""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi.responses import JSONResponse
from src.core.cache import cache_stats_async
from src.core.config import settings
from src.core.database_async import async_engine_enabled, database_ready_async
from src.core.worker_db import database_ready_sync


async def _database_ready_for_health() -> bool:
    if async_engine_enabled():
        return await database_ready_async()
    return database_ready_sync()


async def health_payload(*, ready: bool) -> dict:
    db_ok = await _database_ready_for_health() if ready else None
    cache = await cache_stats_async()
    status = "ok"
    if ready and not db_ok:
        status = "degraded"
    payload: dict[str, Any] = {
        "status": status,
        "service": "omnisight-api",
        "env": settings.app_env,
        "cache": cache,
        "api_versions": ["v1"],
    }
    if ready:
        payload["database"] = db_ok
        payload["nfr"] = {
            "resolve_search_target_ms": 200,
            "scale_target_ci": 50_000,
            "chain_algorithm": "depends_on_directed",
            "fr_coverage": "1-54",
            "cache_backend": cache.get("backend"),
            "read_replica": bool(settings.database_read_url.strip()),
            "async_database": async_engine_enabled(),
            "redis_cache": bool(settings.redis_url.strip()),
            "background_worker": settings.background_tasks_enabled,
            "horizontal_scaling": "postgres_cache_and_rate_limit",
            "scale_verification": "ci_job_nfr_scale_50k",
            "log_json": settings.log_json,
            "rate_limit": f"{settings.rate_limit_max_requests}/{settings.rate_limit_window_seconds}s",
        }
        if settings.docs_enabled:
            payload["nfr"]["openapi"] = "/docs"
    return payload


async def readiness_response() -> dict | JSONResponse:
    payload = await health_payload(ready=True)
    if not payload.get("database"):
        return JSONResponse(status_code=503, content=payload)
    return payload


def readiness_response_sync() -> dict | JSONResponse:
    """Sync wrapper for scripts that cannot await (e.g. verify_demo_acceptance)."""
    return asyncio.run(readiness_response())
