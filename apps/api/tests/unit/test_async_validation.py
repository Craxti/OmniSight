"""Async relation validation parity with sync ``validate_relations``."""

from __future__ import annotations

import pytest
from sqlalchemy.orm import sessionmaker
from src.models import CI, CIType, Relation
from src.services.rsm.async_validation import validate_relations_async


def _session(test_engine):
    return sessionmaker(bind=test_engine)()


@pytest.mark.asyncio
async def test_validate_relations_async_ok(async_bundle):
    result = await validate_relations_async(ci_repo=async_bundle.ci, rel_repo=async_bundle.relations)
    assert result["valid"] is True
    assert result["issue_count"] == 0


@pytest.mark.asyncio
async def test_validate_relations_async_broken_reference(test_engine, async_bundle):
    session = _session(test_engine)
    try:
        server_type = session.query(CIType).filter(CIType.name == "Server").first()
        active = CI(name="async-broken-active", type_id=server_type.id, status="active")
        ghost = CI(name="async-broken-ghost", type_id=server_type.id, status="active")
        session.add_all([active, ghost])
        session.flush()
        session.add(
            Relation(
                source_ci_id=active.id,
                target_ci_id=ghost.id,
                relation_type="depends_on",
                status="active",
            )
        )
        ghost.is_deleted = True
        session.commit()
    finally:
        session.close()

    result = await validate_relations_async(ci_repo=async_bundle.ci, rel_repo=async_bundle.relations)

    assert result["valid"] is False
    assert any(i["type"] == "broken_reference" for i in result["issues"])


@pytest.mark.asyncio
async def test_validate_relations_async_archived_reference(test_engine, async_bundle):
    session = _session(test_engine)
    try:
        server_type = session.query(CIType).filter(CIType.name == "Server").first()
        archived = CI(name="async-archived-ci", type_id=server_type.id, status="archived")
        active = CI(name="async-active-ci", type_id=server_type.id, status="active")
        session.add_all([archived, active])
        session.flush()
        session.add(
            Relation(
                source_ci_id=active.id,
                target_ci_id=archived.id,
                relation_type="depends_on",
                status="active",
            )
        )
        session.commit()
    finally:
        session.close()

    result = await validate_relations_async(ci_repo=async_bundle.ci, rel_repo=async_bundle.relations)

    assert result["valid"] is False
    assert any(i["type"] == "archived_reference" for i in result["issues"])


@pytest.mark.asyncio
async def test_validate_relations_async_cycle(test_engine, async_bundle):
    session = _session(test_engine)
    try:
        server_type = session.query(CIType).filter(CIType.name == "Server").first()
        a = CI(name="async-cycle-a", type_id=server_type.id, status="active")
        b = CI(name="async-cycle-b", type_id=server_type.id, status="active")
        session.add_all([a, b])
        session.flush()
        session.add_all(
            [
                Relation(source_ci_id=a.id, target_ci_id=b.id, relation_type="depends_on", status="active"),
                Relation(source_ci_id=b.id, target_ci_id=a.id, relation_type="depends_on", status="active"),
            ]
        )
        session.commit()
    finally:
        session.close()

    result = await validate_relations_async(ci_repo=async_bundle.ci, rel_repo=async_bundle.relations)

    assert result["valid"] is False
    assert any(i["type"] == "cycle" for i in result["issues"])
