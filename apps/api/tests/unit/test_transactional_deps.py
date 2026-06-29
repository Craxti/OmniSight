"""Transactional dependency wiring."""

from contextlib import asynccontextmanager
from unittest.mock import MagicMock, patch

import pytest
from src.core.deps.write import (
    get_transactional_autodiscover_write_port,
    get_transactional_ci_import_export_write_port,
)
from src.services.async_write.autodiscover import AsyncAutodiscoverWriteService
from src.services.async_write.import_export import AsyncCiImportExportWriteService


@pytest.mark.asyncio
async def test_transactional_deps_use_typed_async_services():
    @asynccontextmanager
    async def _cm():
        yield MagicMock()

    with patch(
        "src.core.deps.write.database_async.async_transactional_write_session",
        _cm,
    ):
        ci_port = await get_transactional_ci_import_export_write_port().__anext__()
        auto_port = await get_transactional_autodiscover_write_port().__anext__()

    assert isinstance(ci_port, AsyncCiImportExportWriteService)
    assert isinstance(auto_port, AsyncAutodiscoverWriteService)
