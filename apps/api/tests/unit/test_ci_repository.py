import pytest
from src.models import CI, CIType


@pytest.mark.asyncio
async def test_ci_repository_search_by_hostname(db_session, async_bundle):
    t = db_session.query(CIType).filter(CIType.name == "Server").first()
    db_session.add(CI(name="repo-host", type_id=t.id, status="active", search_hostname="host-1"))
    db_session.commit()

    items, total = await async_bundle.ci.search(hostname="host-1", limit=10)
    assert total == 1
    assert items[0].name == "repo-host"
