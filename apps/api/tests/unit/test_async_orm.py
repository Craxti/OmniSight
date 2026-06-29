"""Integration tests for async repositories (asyncpg)."""

from __future__ import annotations

import asyncio

from src.repositories.async_orm.ci_repository import AsyncCiRepository
from src.repositories.async_orm.relation_repository import AsyncRelationRepository
from src.services.async_read.dashboard import AsyncDashboardService
from tests.helpers.async_db import async_bundle_for_test_engine


def test_async_ci_repository_count_active(test_engine):
    async def _run() -> None:
        async with async_bundle_for_test_engine(test_engine) as bundle:
            repo = AsyncCiRepository(bundle.session)
            count = await repo.count_active()
            assert count == 0

    asyncio.run(_run())


def test_async_ci_type_repository_seeded(test_engine):
    async def _run() -> None:
        async with async_bundle_for_test_engine(test_engine) as bundle:
            types = await bundle.ci_types.list_ordered()
            names = {t.name for t in types}
            assert "Server" in names
            assert "Business Service" in names

    asyncio.run(_run())


def test_async_relation_repository_count(test_engine):
    async def _run() -> None:
        async with async_bundle_for_test_engine(test_engine) as bundle:
            repo = AsyncRelationRepository(bundle.session)
            count = await repo.count_active()
            assert count == 0

    asyncio.run(_run())


def test_async_dashboard_overview(test_engine):
    async def _run() -> None:
        async with async_bundle_for_test_engine(test_engine) as bundle:
            service = AsyncDashboardService(bundle)
            overview = await service.overview()
            assert overview.total_ci == 0
            assert overview.total_relations == 0
            assert overview.model_health.valid is True

    asyncio.run(_run())
