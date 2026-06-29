"""Unit tests for depends_on cycle helpers."""

import pytest
from src.models import CI, CIType, Relation
from src.services.rsm.async_depends_on_cycle import would_create_depends_on_cycle_async


def _ci(db_session, name: str) -> CI:
    t = db_session.query(CIType).filter(CIType.name == "Server").first()
    ci = CI(name=name, type_id=t.id, status="active")
    db_session.add(ci)
    db_session.flush()
    return ci


@pytest.mark.asyncio
async def test_would_create_depends_on_cycle_detects_loop(db_session, async_bundle):
    a = _ci(db_session, "cycle-a")
    b = _ci(db_session, "cycle-b")
    db_session.add(
        Relation(
            source_ci_id=b.id,
            target_ci_id=a.id,
            relation_type="depends_on",
            status="active",
        )
    )
    db_session.commit()

    assert await would_create_depends_on_cycle_async(async_bundle.relations, a.id, b.id) is True
