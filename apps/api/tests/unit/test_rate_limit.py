import uuid

import pytest
from src.core.rate_limit import allow_request


@pytest.mark.asyncio
async def test_rate_limit_blocks_after_max_requests():
    client_key = f"test-client-nfr-{uuid.uuid4().hex}"
    max_requests = 3
    window_seconds = 60

    for _ in range(max_requests):
        assert await allow_request(client_key, max_requests, window_seconds) is True

    assert await allow_request(client_key, max_requests, window_seconds) is False
