"""Unit tests for async topology helpers."""

from __future__ import annotations

import pytest
from sqlalchemy.orm import sessionmaker
from src.models import CI, CIType, Relation
from src.services.rsm.async_topology import (
    async_find_root_cause_candidates,
    async_on_same_dependency_chain,
)


def _create_ci(session, name: str, type_name: str = "Server") -> CI:
    ci_type = session.query(CIType).filter(CIType.name == type_name).first()
    ci = CI(name=name, type_id=ci_type.id, status="active")
    session.add(ci)
    session.flush()
    return ci


def _depends(session, source: CI, target: CI) -> None:
    session.add(
        Relation(
            source_ci_id=source.id,
            target_ci_id=target.id,
            relation_type="depends_on",
            status="active",
        )
    )


def _seed_linear_chain(test_engine, prefix: str) -> tuple[int, int, int]:
    session = sessionmaker(bind=test_engine)()
    try:
        db = _create_ci(session, f"{prefix}-db", "Database")
        app = _create_ci(session, f"{prefix}-app", "Application")
        biz = _create_ci(session, f"{prefix}-biz", "Business Service")
        _depends(session, app, db)
        _depends(session, biz, app)
        session.commit()
        return db.id, app.id, biz.id
    finally:
        session.close()


def _seed_app_db_pair(test_engine, prefix: str) -> tuple[int, int]:
    session = sessionmaker(bind=test_engine)()
    try:
        db = _create_ci(session, f"{prefix}-db", "Database")
        app = _create_ci(session, f"{prefix}-app", "Application")
        _depends(session, app, db)
        session.commit()
        return db.id, app.id
    finally:
        session.close()


@pytest.mark.asyncio
async def test_async_on_same_dependency_chain_single_id(async_bundle):
    assert await async_on_same_dependency_chain([1], rel_repo=async_bundle.relations) is True


@pytest.mark.asyncio
async def test_async_on_same_dependency_chain_linear(test_engine, async_bundle):
    db_id, app_id, biz_id = _seed_linear_chain(test_engine, "async-chain")

    related = await async_on_same_dependency_chain(
        [db_id, app_id, biz_id],
        rel_repo=async_bundle.relations,
    )

    assert related is True


@pytest.mark.asyncio
async def test_async_find_root_cause_candidates(test_engine, async_bundle):
    db_id, app_id = _seed_app_db_pair(test_engine, "async-rc")

    zone = await async_find_root_cause_candidates(
        [db_id, app_id],
        ci_repo=async_bundle.ci,
        rel_repo=async_bundle.relations,
    )

    assert {item.name for item in zone} == {"async-rc-db"}


@pytest.mark.asyncio
async def test_async_find_root_cause_candidates_empty(async_bundle):
    zone = await async_find_root_cause_candidates([], ci_repo=async_bundle.ci, rel_repo=async_bundle.relations)
    assert zone == []
