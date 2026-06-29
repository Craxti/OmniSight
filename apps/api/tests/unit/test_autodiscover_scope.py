"""Unit tests for autodiscover scope helpers."""

import pytest
from src.models import CI, CIType, Relation
from src.services.autodiscover.runtime.scope import graph_scope_ids_async, resolve_scope_ci_ids_async
from src.services.autodiscover.scope import current_field_value, hostname_of


def _ci(db_session, name: str, type_name: str = "Server", **kwargs) -> CI:
    t = db_session.query(CIType).filter(CIType.name == type_name).first()
    ci = CI(name=name, type_id=t.id, status="active", **kwargs)
    db_session.add(ci)
    db_session.flush()
    return ci


@pytest.mark.asyncio
async def test_graph_scope_ids_includes_neighbors(db_session, async_bundle):
    a = _ci(db_session, "scope-a")
    b = _ci(db_session, "scope-b")
    db_session.add(
        Relation(
            source_ci_id=a.id,
            target_ci_id=b.id,
            relation_type="depends_on",
            status="active",
        )
    )
    db_session.commit()

    ids = await graph_scope_ids_async(a.id, depth=1, rel_repo=async_bundle.relations)
    assert a.id in ids
    assert b.id in ids


@pytest.mark.asyncio
async def test_resolve_scope_ci_ids_all_mode(db_session, async_bundle):
    _ci(db_session, "scope-seed-ci")
    db_session.commit()
    ids = await resolve_scope_ci_ids_async(
        scope_mode="all",
        scope_config={},
        server_ci_ids=[],
        ci_repo=async_bundle.ci,
        rel_repo=async_bundle.relations,
    )
    assert len(ids) >= 1


@pytest.mark.asyncio
async def test_resolve_scope_ci_ids_filters_mode(db_session, async_bundle):
    _ci(db_session, "scope-filter-ci", environment="prod", owner="ops")
    _ci(db_session, "scope-other-ci", environment="dev")
    db_session.commit()

    ids = await resolve_scope_ci_ids_async(
        scope_mode="filters",
        scope_config={"environment": "prod", "owner": "ops"},
        server_ci_ids=[],
        ci_repo=async_bundle.ci,
        rel_repo=async_bundle.relations,
    )
    names = {db_session.get(CI, i).name for i in ids}
    assert "scope-filter-ci" in names
    assert "scope-other-ci" not in names


def test_current_field_value_reads_top_level_and_external(db_session):
    ci = _ci(
        db_session,
        "scope-fields-ci",
        owner="team-a",
        environment="staging",
        attributes={"slot": "x"},
        external_ids={"hostname": "host1"},
    )
    db_session.commit()

    assert current_field_value(ci, "owner") == "team-a"
    assert current_field_value(ci, "hostname") == "host1"
    assert current_field_value(ci, "attributes.slot") == "x"
    assert hostname_of(ci) == "host1"
