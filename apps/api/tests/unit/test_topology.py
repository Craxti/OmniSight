import pytest
from src.models import CI, CIType, Relation
from src.services.rsm.async_topology import (
    async_find_business_path_directed,
    async_find_component_ids_below,
    async_find_components_below,
    async_find_impacted_business_services,
    async_find_root_cause_candidates,
    async_on_same_dependency_chain,
)


def _create_ci(db, name: str, type_name: str, **kwargs) -> CI:
    ci_type = db.query(CIType).filter(CIType.name == type_name).first()
    ci = CI(name=name, type_id=ci_type.id, status="active", **kwargs)
    db.add(ci)
    db.flush()
    return ci


def _depends(db, source: CI, target: CI) -> None:
    db.add(
        Relation(
            source_ci_id=source.id,
            target_ci_id=target.id,
            relation_type="depends_on",
            status="active",
        )
    )


@pytest.mark.asyncio
async def test_chain_related_linear_chain(db_session, async_bundle):
    db = _create_ci(db_session, "chain-db", "Database")
    app = _create_ci(db_session, "chain-app", "Application")
    biz = _create_ci(db_session, "chain-biz", "Business Service")
    _depends(db_session, app, db)
    _depends(db_session, biz, app)
    db_session.commit()

    assert (
        await async_on_same_dependency_chain(
            [db.id, app.id, biz.id],
            rel_repo=async_bundle.relations,
        )
        is True
    )


@pytest.mark.asyncio
async def test_chain_related_parallel_branches_false(db_session, async_bundle):
    db = _create_ci(db_session, "shared-db", "Database")
    app1 = _create_ci(db_session, "branch-app-1", "Application")
    app2 = _create_ci(db_session, "branch-app-2", "Application")
    _depends(db_session, app1, db)
    _depends(db_session, app2, db)
    db_session.commit()

    assert (
        await async_on_same_dependency_chain(
            [app1.id, app2.id],
            rel_repo=async_bundle.relations,
        )
        is False
    )


@pytest.mark.asyncio
async def test_impact_follows_depends_on_upward(db_session, async_bundle):
    db = _create_ci(db_session, "impact-db", "Database")
    app = _create_ci(db_session, "impact-app", "Application")
    biz = _create_ci(db_session, "impact-biz", "Business Service", criticality="high")
    _depends(db_session, app, db)
    _depends(db_session, biz, app)
    db_session.commit()

    impact = await async_find_impacted_business_services(
        db.id,
        ci_repo=async_bundle.ci,
        rel_repo=async_bundle.relations,
    )
    names = {s.name for s in impact}
    assert "impact-biz" in names


@pytest.mark.asyncio
async def test_business_path_from_db(db_session, async_bundle):
    db = _create_ci(db_session, "path-db", "Database")
    app = _create_ci(db_session, "path-app", "Application")
    biz = _create_ci(db_session, "path-biz", "Business Service")
    _depends(db_session, app, db)
    _depends(db_session, biz, app)
    db_session.commit()

    path = await async_find_business_path_directed(
        db.id,
        ci_repo=async_bundle.ci,
        rel_repo=async_bundle.relations,
    )
    names = [n.name for n in path]
    assert names == ["path-db", "path-app", "path-biz"]


@pytest.mark.asyncio
async def test_root_cause_leaves_deepest_node(db_session, async_bundle):
    db = _create_ci(db_session, "rc-db", "Database")
    app = _create_ci(db_session, "rc-app", "Application")
    _depends(db_session, app, db)
    db_session.commit()

    zone = await async_find_root_cause_candidates(
        [db.id, app.id],
        ci_repo=async_bundle.ci,
        rel_repo=async_bundle.relations,
    )
    names = {z.name for z in zone}
    assert names == {"rc-db"}


@pytest.mark.asyncio
async def test_component_ids_below_business_service(db_session, async_bundle):
    db = _create_ci(db_session, "comp-db", "Database")
    app = _create_ci(db_session, "comp-app", "Application")
    biz = _create_ci(db_session, "comp-biz", "Business Service")
    _depends(db_session, app, db)
    _depends(db_session, biz, app)
    db_session.commit()

    below = await async_find_component_ids_below(
        biz.id,
        ci_repo=async_bundle.ci,
        rel_repo=async_bundle.relations,
    )
    assert below == {db.id, app.id}

    components = await async_find_components_below(
        biz.id,
        ci_repo=async_bundle.ci,
        rel_repo=async_bundle.relations,
    )
    assert {c.name for c in components} == {"comp-db", "comp-app"}
