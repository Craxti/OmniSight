"""Unit tests for async uniqueness helpers."""

import pytest
from src.core.exceptions import ConflictError
from src.models import CI, CIType, Relation
from src.services.async_uniqueness import assert_unique_ci_name_async


@pytest.mark.asyncio
async def test_assert_unique_ci_name_raises_on_duplicate(db_session, async_bundle):
    t = db_session.query(CIType).filter(CIType.name == "Server").first()
    db_session.add(CI(name="uniq-ci", type_id=t.id, status="active"))
    db_session.commit()

    with pytest.raises(ConflictError):
        await assert_unique_ci_name_async(async_bundle.ci, "uniq-ci")


@pytest.mark.asyncio
async def test_find_active_relation_returns_edge(db_session, async_bundle):
    t = db_session.query(CIType).filter(CIType.name == "Server").first()
    a = CI(name="uniq-a", type_id=t.id, status="active")
    b = CI(name="uniq-b", type_id=t.id, status="active")
    db_session.add_all([a, b])
    db_session.flush()
    db_session.add(
        Relation(
            source_ci_id=a.id,
            target_ci_id=b.id,
            relation_type="depends_on",
            status="active",
        )
    )
    db_session.commit()

    rel = await async_bundle.relations.find_active(a.id, b.id, "depends_on")
    assert rel is not None
    assert rel.source_ci_id == a.id
