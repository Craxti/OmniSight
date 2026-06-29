"""Correlation context must not reuse dead resource ids from cached resolve snapshots."""

import pytest
from src.models import CI, CIType
from src.services.rsm.async_correlation import build_correlation_context_async
from src.services.rsm.indexed_ids import sync_search_indexes


@pytest.mark.asyncio
async def test_dead_resource_ids_yield_empty_graph_and_enrichment(db_session, async_bundle):
    original = CI(
        name="gone-ci",
        type_id=db_session.query(CIType).filter(CIType.name == "Application").first().id,
        status="active",
        attributes={"hostname": "gone-host"},
        external_ids={"hostname": "gone-host"},
    )
    sync_search_indexes(original)
    db_session.add(original)
    db_session.flush()
    dead_id = original.id
    db_session.delete(original)
    db_session.commit()

    ctx = await build_correlation_context_async(
        [dead_id],
        ci_repo=async_bundle.ci,
        rel_repo=async_bundle.relations,
    )
    assert ctx.enrichment == []
    assert ctx.graph.nodes == []
    assert ctx.chain_related is True
