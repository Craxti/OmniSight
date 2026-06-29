import json
import logging
import time
import uuid

from src.core.config import settings
from src.core.rate_limit import allow_request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger("omnisight.api")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())[:12]
        started = time.perf_counter()
        response: Response | None = None
        error: str | None = None
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            error = str(exc)
            raise
        finally:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            status = response.status_code if response else 500
            log_entry = {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": status,
                "duration_ms": duration_ms,
            }
            if error:
                log_entry["error"] = error
            should_log = (
                settings.log_json
                or status >= 400
                or request.url.path.startswith("/api/v1/ci/import")
                or "export" in request.url.path
            )
            if should_log:
                logger.info(json.dumps(log_entry, ensure_ascii=False))
            if response:
                response.headers["X-Request-ID"] = request_id


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 120, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next) -> Response:
        if not settings.rate_limit_enabled or not request.url.path.startswith("/api/"):
            return await call_next(request)
        if request.url.path in ("/api/v1/auth/login", "/api/v1/auth/token"):
            return await call_next(request)
        client = request.client.host if request.client else "unknown"
        allowed = await allow_request(
            client,
            self.max_requests,
            self.window_seconds,
        )
        if not allowed:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
        return await call_next(request)
