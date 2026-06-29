"""Webhook integration tests."""

from unittest.mock import MagicMock, patch

import pytest
from src.models import IntegrationOutbox
from src.services.integrations.async_webhook import (
    dispatch_correlation_webhook_async,
    enqueue_outbox_async,
    process_outbox_row_async,
)
from src.services.integrations.webhook_delivery import deliver_webhook


@pytest.mark.asyncio
async def test_enqueue_outbox_persists_row(db_session, async_bundle):
    row = await enqueue_outbox_async(async_bundle.session, "test.event", {"ok": True}, "http://example/hook")
    await async_bundle.session.commit()
    assert row.id is not None
    assert row.status == "pending"
    assert row.event_type == "test.event"


@patch("src.services.integrations.webhook_delivery.urllib.request.urlopen")
def test_deliver_webhook_success(mock_urlopen):
    mock_urlopen.return_value.__enter__.return_value = MagicMock(status=204)
    assert deliver_webhook("http://example/hook", {"a": 1}, secret="s3cret") is True


@patch("src.services.integrations.webhook_delivery.urllib.request.urlopen")
def test_deliver_webhook_http_error(mock_urlopen):
    import urllib.error

    mock_urlopen.side_effect = urllib.error.HTTPError("http://x", 500, "err", {}, None)
    assert deliver_webhook("http://example/hook", {"a": 1}) is False


@pytest.mark.asyncio
async def test_process_outbox_row_updates_status(monkeypatch):
    row = IntegrationOutbox(
        event_type="correlation.ingest",
        target_url="http://example/hook",
        payload={"alerts": []},
        status="pending",
        attempts=0,
    )
    monkeypatch.setattr(
        "src.services.integrations.async_webhook.deliver_webhook",
        lambda *_args, **_kwargs: True,
    )
    assert await process_outbox_row_async(row) is True
    assert row.status == "delivered"
    assert row.attempts == 1


@pytest.mark.asyncio
async def test_dispatch_correlation_webhook_without_url_returns_false(db_session, async_bundle, monkeypatch):
    monkeypatch.setattr("src.services.integrations.async_webhook.settings.webhook_url", "")
    result = await dispatch_correlation_webhook_async(async_bundle.session, {"alerts": []})
    assert result == {"queued": False, "delivered": False}


@pytest.mark.asyncio
async def test_dispatch_correlation_webhook_queues_and_delivers(db_session, async_bundle, monkeypatch):
    monkeypatch.setattr("src.services.integrations.async_webhook.settings.webhook_url", "http://example/hook")
    monkeypatch.setattr("src.services.integrations.async_webhook.settings.webhook_sync_delivery", True)
    monkeypatch.setattr(
        "src.services.integrations.async_webhook.deliver_webhook",
        lambda *_args, **_kwargs: True,
    )
    result = await dispatch_correlation_webhook_async(async_bundle.session, {"alerts": [{"id": 1}]})
    assert result["queued"] is True
    assert result["delivered"] is True
    assert result["outbox_id"] > 0
