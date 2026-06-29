"""Ensure HTTP ports use async SQLAlchemy sessions only."""

from __future__ import annotations

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.core.auth_lookup import get_user_by_email
from src.core.deps.read import get_ci_read_port
from src.core.deps.write import get_ci_write_port


def _fake_async_session_cm():
    @asynccontextmanager
    async def _cm():
        yield MagicMock()

    return _cm


@pytest.mark.asyncio
async def test_read_port_uses_async_read_session():
    with patch("src.core.deps.read.database_async.async_read_session", _fake_async_session_cm()):
        port = await get_ci_read_port().__anext__()

    assert port is not None


@pytest.mark.asyncio
async def test_write_port_uses_async_write_session():
    with patch("src.core.deps.write.database_async.async_write_session", _fake_async_session_cm()):
        port = await get_ci_write_port().__anext__()

    assert port is not None


@pytest.mark.asyncio
async def test_auth_lookup_uses_async_read_session():
    with patch("src.core.auth_lookup.database_async.async_read_session", _fake_async_session_cm()):
        with patch(
            "src.repositories.async_orm.user_repository.AsyncUserRepository.get_by_email",
            new_callable=AsyncMock,
            return_value=None,
        ) as lookup:
            await get_user_by_email("a@b.c")

    lookup.assert_awaited_once()
