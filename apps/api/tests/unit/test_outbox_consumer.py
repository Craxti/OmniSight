"""Outbox retry consumer tests."""

import pytest
from src.models import IntegrationOutbox
from src.repositories.async_orm.outbox_repository import AsyncOutboxRepository


@pytest.mark.asyncio
async def test_async_fetch_retryable_rows_includes_failed_under_max_attempts(db_session, async_bundle, monkeypatch):
    monkeypatch.setattr("src.core.config.settings.outbox_max_attempts", 5)
    row = IntegrationOutbox(
        event_type="correlation.ingest",
        target_url="http://example/hook",
        payload={"alerts": []},
        status="failed",
        attempts=2,
    )
    db_session.add(row)
    db_session.commit()

    repo = AsyncOutboxRepository(async_bundle.session)
    rows = await repo.fetch_retryable(limit=10, max_attempts=5)
    assert len(rows) == 1
    assert rows[0].id == row.id
