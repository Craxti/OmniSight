"""TTL cache: PostgreSQL-backed (or Redis when REDIS_URL is set)."""

import asyncio
import base64
import json
import time
from collections.abc import Callable
from datetime import UTC, datetime
from functools import wraps
from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.core.cache_models import deserialize_cached_pydantic
from src.core.config import settings
from src.core.database import sync_session

T = TypeVar("T")
_store: dict[str, tuple[float, Any]] = {}
_redis_client = None


def _redis() -> Any:
    global _redis_client
    if _redis_client is None:
        import redis

        _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


def _redis_get(key: str) -> Any | None:
    raw = _redis().get(f"omnisight:cache:{key}")
    if raw is None:
        return None
    return _deserialize(raw)


def _redis_set(key: str, value: Any, ttl: float) -> None:
    _redis().setex(f"omnisight:cache:{key}", int(ttl), _serialize(value))


def _redis_invalidate_prefix(prefix: str) -> None:
    client = _redis()
    for match in client.scan_iter(f"omnisight:cache:{prefix}*"):
        client.delete(match)


def cache_enabled() -> bool:
    return settings.cache_enabled


def cache_backend() -> str:
    if not cache_enabled():
        return "disabled"
    if settings.redis_url.strip():
        return "redis"
    return "postgres"


_CACHE_FMT_JSON = "json"
_CACHE_FMT_PYDANTIC = "pydantic"


def _serialize(value: Any) -> str:
    if isinstance(value, BaseModel):
        payload = {
            "fmt": _CACHE_FMT_PYDANTIC,
            "cls": value.__class__.__name__,
            "data": value.model_dump(mode="json"),
        }
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    else:
        raw = json.dumps({"fmt": _CACHE_FMT_JSON, "data": value}, ensure_ascii=False, default=str).encode("utf-8")
    return base64.b64encode(raw).decode("ascii")


def _deserialize_pydantic(cls_name: str, data: dict[str, Any]) -> Any:
    return deserialize_cached_pydantic(cls_name, data)


def _deserialize(raw: str) -> Any:
    decoded = base64.b64decode(raw.encode("ascii"))
    try:
        payload = json.loads(decoded.decode("utf-8"))
        if isinstance(payload, dict) and payload.get("fmt") == _CACHE_FMT_PYDANTIC:
            return _deserialize_pydantic(payload["cls"], payload["data"])
        if isinstance(payload, dict) and payload.get("fmt") == _CACHE_FMT_JSON:
            return payload["data"]
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return None


def _memory_get(key: str) -> Any | None:
    entry = _store.get(key)
    if not entry:
        return None
    expires_at, value = entry
    if time.monotonic() > expires_at:
        _store.pop(key, None)
        return None
    return value


def _memory_set(key: str, value: Any, ttl: float) -> None:
    _store[key] = (time.monotonic() + ttl, value)


def _memory_invalidate_prefix(prefix: str) -> None:
    for key in list(_store):
        if key.startswith(prefix):
            _store.pop(key, None)


def _utc_timestamp() -> float:
    return datetime.now(UTC).timestamp()


def _postgres_get_db(db: Session, key: str) -> Any | None:
    from src.models import CacheEntry

    row = db.get(CacheEntry, key)
    if not row:
        return None
    if _utc_timestamp() > row.expires_at:
        db.delete(row)
        db.commit()
        return None
    return _deserialize(row.value_blob)


def _postgres_set_db(db: Session, key: str, value: Any, ttl: float) -> None:
    from src.models import CacheEntry

    expires_at = _utc_timestamp() + ttl
    row = db.get(CacheEntry, key)
    if row:
        row.value_blob = _serialize(value)
        row.expires_at = expires_at
    else:
        db.add(CacheEntry(key=key, value_blob=_serialize(value), expires_at=expires_at))
    db.commit()


def _postgres_invalidate_prefix_db(db: Session, prefix: str) -> None:
    from src.models import CacheEntry

    db.query(CacheEntry).filter(CacheEntry.key.startswith(prefix)).delete(synchronize_session=False)
    db.commit()


async def _postgres_get_async(session, key: str) -> Any | None:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.models import CacheEntry

    assert isinstance(session, AsyncSession)
    row = await session.get(CacheEntry, key)
    if not row:
        return None
    if _utc_timestamp() > row.expires_at:
        await session.delete(row)
        await session.commit()
        return None
    return _deserialize(row.value_blob)


async def _postgres_set_async(session, key: str, value: Any, ttl: float) -> None:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.models import CacheEntry

    assert isinstance(session, AsyncSession)
    expires_at = _utc_timestamp() + ttl
    row = await session.get(CacheEntry, key)
    if row:
        row.value_blob = _serialize(value)
        row.expires_at = expires_at
    else:
        session.add(CacheEntry(key=key, value_blob=_serialize(value), expires_at=expires_at))
    await session.commit()


async def _postgres_invalidate_prefix_async(session, prefix: str) -> None:
    from sqlalchemy import delete
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.models import CacheEntry

    assert isinstance(session, AsyncSession)
    await session.execute(delete(CacheEntry).where(CacheEntry.key.startswith(prefix)))
    await session.commit()


async def _postgres_cache_stats_async(session, *, now_utc: float) -> dict[str, int | bool | str]:
    from sqlalchemy import func, select
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.models import CacheEntry

    assert isinstance(session, AsyncSession)
    total = int(await session.scalar(select(func.count()).select_from(CacheEntry)) or 0)
    active = int(
        await session.scalar(select(func.count()).select_from(CacheEntry).where(CacheEntry.expires_at > now_utc)) or 0
    )
    return {"enabled": True, "backend": "postgres", "entries": total, "active": active}


def _postgres_get(key: str) -> Any | None:
    with sync_session() as db:
        return _postgres_get_db(db, key)


def _postgres_set(key: str, value: Any, ttl: float) -> None:
    with sync_session() as db:
        _postgres_set_db(db, key, value, ttl)


def _postgres_invalidate_prefix(prefix: str) -> None:
    with sync_session() as db:
        _postgres_invalidate_prefix_db(db, prefix)


def cache_get(key: str) -> Any | None:
    if not cache_enabled():
        return None
    backend = cache_backend()
    if backend == "redis":
        return _redis_get(key)
    if backend == "postgres":
        return _postgres_get(key)
    return _memory_get(key)


def cache_set(key: str, value: Any, ttl: float | None = None) -> None:
    if not cache_enabled():
        return
    expires = ttl if ttl is not None else settings.cache_ttl_seconds
    backend = cache_backend()
    if backend == "redis":
        _redis_set(key, value, expires)
    elif backend == "postgres":
        _postgres_set(key, value, expires)
    else:
        _memory_set(key, value, expires)


def cache_invalidate_prefix(prefix: str) -> None:
    if not cache_enabled():
        return
    backend = cache_backend()
    if backend == "redis":
        _redis_invalidate_prefix(prefix)
    elif backend == "postgres":
        _postgres_invalidate_prefix(prefix)
    else:
        _memory_invalidate_prefix(prefix)


async def cache_get_async(key: str) -> Any | None:
    if not cache_enabled():
        return None
    backend = cache_backend()
    if backend == "postgres":
        from src.core.database_async import async_write_session

        async with async_write_session() as session:
            return await _postgres_get_async(session, key)
    return cache_get(key)


async def cache_set_async(key: str, value: Any, ttl: float | None = None) -> None:
    if not cache_enabled():
        return
    expires = ttl if ttl is not None else settings.cache_ttl_seconds
    backend = cache_backend()
    if backend == "postgres":
        from src.core.database_async import async_write_session

        async with async_write_session() as session:
            await _postgres_set_async(session, key, value, expires)
        return
    cache_set(key, value, ttl=expires)


async def cache_invalidate_prefix_async(prefix: str) -> None:
    if not cache_enabled():
        return
    backend = cache_backend()
    if backend == "postgres":
        from src.core.database_async import async_write_session

        async with async_write_session() as session:
            await _postgres_invalidate_prefix_async(session, prefix)
        return
    cache_invalidate_prefix(prefix)


def cached(ttl: float | None = None, key_fn: Callable[..., str] | None = None):
    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            if not cache_enabled():
                return fn(*args, **kwargs)
            key = key_fn(*args, **kwargs) if key_fn else f"{fn.__name__}:{args}:{kwargs}"
            hit = cache_get(key)
            if hit is not None:
                return hit
            result = fn(*args, **kwargs)
            cache_set(key, result, ttl=ttl)
            return result

        return wrapper

    return decorator


def _postgres_cache_stats_db(db: Session, *, now_utc: float) -> dict[str, int | bool | str]:
    from src.models import CacheEntry

    total = db.query(CacheEntry).count()
    active = db.query(CacheEntry).filter(CacheEntry.expires_at > now_utc).count()
    return {"enabled": True, "backend": "postgres", "entries": total, "active": active}


def _redis_cache_stats() -> dict[str, int | bool | str]:
    try:
        keys = list(_redis().scan_iter("omnisight:cache:*", count=200))
        return {"enabled": True, "backend": "redis", "entries": len(keys), "active": len(keys)}
    except Exception:
        return {"enabled": True, "backend": "redis", "entries": 0, "active": 0}


def cache_stats() -> dict[str, int | bool | str]:
    now_mono = time.monotonic()
    now_utc = _utc_timestamp()
    backend = cache_backend()
    if backend == "redis":
        return _redis_cache_stats()
    if backend == "postgres":
        with sync_session() as db:
            return _postgres_cache_stats_db(db, now_utc=now_utc)
    active = sum(1 for exp, _ in _store.values() if exp > now_mono)
    return {"enabled": cache_enabled(), "backend": cache_backend(), "entries": len(_store), "active": active}


async def cache_stats_async() -> dict[str, int | bool | str]:
    now_mono = time.monotonic()
    now_utc = _utc_timestamp()
    backend = cache_backend()
    if backend == "redis":
        return await asyncio.to_thread(_redis_cache_stats)
    if backend == "postgres":
        from src.core.database_async import async_read_session

        async with async_read_session() as session:
            return await _postgres_cache_stats_async(session, now_utc=now_utc)
    active = sum(1 for exp, _ in _store.values() if exp > now_mono)
    return {"enabled": cache_enabled(), "backend": cache_backend(), "entries": len(_store), "active": active}
