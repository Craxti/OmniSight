import pytest
from src.models import CI, CIType, Relation
from src.services.rsm.async_graph import (
    async_build_graph,
    async_compute_impact,
    async_find_business_path,
    async_get_direct_relations,
)


def _create_ci(db, name: str, type_name: str, **kwargs) -> CI:
    ci_type = db.query(CIType).filter(CIType.name == type_name).first()
    ci = CI(name=name, type_id=ci_type.id, status="active", **kwargs)
    db.add(ci)
    db.flush()
    return ci


@pytest.mark.asyncio
async def test_build_graph_depth(db_session, async_bundle):
    app = _create_ci(db_session, "graph-app", "Application")
    db = _create_ci(db_session, "graph-db", "Database")
    db_session.add(
        Relation(
            source_ci_id=app.id,
            target_ci_id=db.id,
            relation_type="depends_on",
            status="active",
        )
    )
    db_session.commit()

    graph = await async_build_graph(async_bundle.ci, async_bundle.relations, app.id, depth=1)
    assert graph.root_id == app.id
    node_ids = {n.id for n in graph.nodes}
    assert app.id in node_ids
    assert db.id in node_ids
    assert len(graph.edges) == 1


@pytest.mark.asyncio
async def test_compute_impact_finds_business_service(db_session, async_bundle):
    biz = _create_ci(db_session, "impact-biz", "Business Service", criticality="high")
    app = _create_ci(db_session, "impact-app", "Application")
    db = _create_ci(db_session, "impact-db", "Database")
    db_session.add(Relation(source_ci_id=app.id, target_ci_id=db.id, relation_type="depends_on", status="active"))
    db_session.add(Relation(source_ci_id=biz.id, target_ci_id=app.id, relation_type="depends_on", status="active"))
    db_session.commit()

    impact = await async_compute_impact(db.id, ci_repo=async_bundle.ci, rel_repo=async_bundle.relations)
    assert impact.count >= 1
    assert any(s.name == "impact-biz" for s in impact.impacted_business_services)


@pytest.mark.asyncio
async def test_find_business_path(db_session, async_bundle):
    biz = _create_ci(db_session, "path-biz", "Business Service")
    app = _create_ci(db_session, "path-app", "Application")
    db_session.add(Relation(source_ci_id=biz.id, target_ci_id=app.id, relation_type="depends_on", status="active"))
    db_session.commit()

    path = await async_find_business_path(app.id, ci_repo=async_bundle.ci, rel_repo=async_bundle.relations)
    names = [n.name for n in path.path]
    assert "path-app" in names
    assert "path-biz" in names


@pytest.mark.asyncio
async def test_get_direct_relations(db_session, async_bundle):
    app = _create_ci(db_session, "rel-app", "Application")
    db = _create_ci(db_session, "rel-db", "Database")
    db_session.add(Relation(source_ci_id=app.id, target_ci_id=db.id, relation_type="depends_on", status="active"))
    db_session.commit()

    rels = await async_get_direct_relations(async_bundle.relations, app.id)
    assert len(rels) == 1
    assert rels[0].target_ci_id == db.id
