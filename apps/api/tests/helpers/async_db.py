"""Async test database helpers."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.core.database_async import _to_async_url

from tests.helpers.postgres_db import test_database_url

_async_engines: dict[str, object] = {}


async def _dispose_all_async_engines() -> None:
    for engine in _async_engines.values():
        await engine.dispose()
    _async_engines.clear()


def dispose_cached_async_engines() -> None:
    if _async_engines:
        asyncio.run(_dispose_all_async_engines())


@asynccontextmanager
async def async_bundle_for_test_engine(test_engine):
    async_url = _to_async_url(test_database_url())
    async_engine = create_async_engine(async_url, pool_pre_ping=True)
    factory = async_sessionmaker(async_engine, expire_on_commit=False)
    try:
        async with factory() as session:
            yield AsyncRepositoryBundle.from_session(session)
    finally:
        await async_engine.dispose()


@asynccontextmanager
async def async_bundle_for_sync_session(sync_session):
    sync_session.flush()
    bind = sync_session.get_bind()
    url = getattr(bind, "url", None)
    sync_url = str(url) if url is not None else str(bind.engine.url)
    async_url = _to_async_url(sync_url)
    async_engine = create_async_engine(async_url, pool_pre_ping=True)
    factory = async_sessionmaker(async_engine, expire_on_commit=False)
    try:
        async with factory() as session:
            yield AsyncRepositoryBundle.from_session(session)
    finally:
        await async_engine.dispose()


def pydantic_dump(value):
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, list):
        return [pydantic_dump(item) for item in value]
    if isinstance(value, dict):
        return {key: pydantic_dump(item) for key, item in value.items()}
    return value
