import pytest
from src.models import CI, CIType, Relation
from src.services.async_read.correlation import AsyncCorrelationReadService
from src.services.rsm.async_topology import async_on_same_dependency_chain
from src.services.rsm.indexed_ids import sync_search_indexes


def _create_ci_with_hostname(db, name: str, hostname: str) -> CI:
    server_type = db.query(CIType).filter(CIType.name == "Server").first()
    ci = CI(
        name=name,
        type_id=server_type.id,
        status="active",
        external_ids={"hostname": hostname},
        attributes={"hostname": hostname},
    )
    sync_search_indexes(ci)
    db.add(ci)
    db.flush()
    return ci


@pytest.mark.asyncio
async def test_match_resource_by_hostname(db_session, async_bundle):
    ci = _create_ci_with_hostname(db_session, "match-host", "unique-host-01")
    db_session.commit()

    result = await AsyncCorrelationReadService(async_bundle).resolve_batch([{"hostname": "unique-host-01"}])
    assert result.resolved
    assert result.resolved[0].resource is not None
    assert result.resolved[0].resource.id == ci.id
    assert result.resolved[0].ambiguous is False


@pytest.mark.asyncio
async def test_match_resource_not_found(db_session, async_bundle):
    result = await AsyncCorrelationReadService(async_bundle).resolve_batch([{"hostname": "no-such-host"}])
    assert result.unresolved
    assert result.unresolved[0].resolved is False


@pytest.mark.asyncio
async def test_match_resource_ambiguous(db_session, async_bundle):
    _create_ci_with_hostname(db_session, "dup-a", "dup-host")
    _create_ci_with_hostname(db_session, "dup-b", "dup-host")
    db_session.commit()

    result = await AsyncCorrelationReadService(async_bundle).resolve_batch([{"hostname": "dup-host"}])
    assert result.resolved
    assert result.resolved[0].ambiguous
    assert result.resolved[0].match_count == 2


@pytest.mark.asyncio
async def test_match_resource_by_cmdb_id(db_session, async_bundle):
    ci = _create_ci_with_hostname(db_session, "cmdb-target", "cmdb-host")
    db_session.commit()

    result = await AsyncCorrelationReadService(async_bundle).resolve_batch([{"cmdbId": str(ci.id)}])
    assert result.resolved
    assert result.resolved[0].resource is not None
    assert result.resolved[0].resource.id == ci.id


@pytest.mark.asyncio
async def test_seeds_in_one_chain_single(db_session, async_bundle):
    ci = _create_ci_with_hostname(db_session, "solo", "solo-host")
    db_session.commit()
    assert await async_on_same_dependency_chain([ci.id], rel_repo=async_bundle.relations) is True


@pytest.mark.asyncio
async def test_seeds_in_one_chain_parallel_false(db_session, async_bundle):
    db_type = db_session.query(CIType).filter(CIType.name == "Database").first()
    app_type = db_session.query(CIType).filter(CIType.name == "Application").first()
    db_ci = CI(name="par-db", type_id=db_type.id, status="active")
    app1 = CI(name="par-app-1", type_id=app_type.id, status="active")
    app2 = CI(name="par-app-2", type_id=app_type.id, status="active")
    db_session.add_all([db_ci, app1, app2])
    db_session.flush()
    db_session.add(Relation(source_ci_id=app1.id, target_ci_id=db_ci.id, relation_type="depends_on", status="active"))
    db_session.add(Relation(source_ci_id=app2.id, target_ci_id=db_ci.id, relation_type="depends_on", status="active"))
    db_session.commit()
    assert await async_on_same_dependency_chain([app1.id, app2.id], rel_repo=async_bundle.relations) is False
