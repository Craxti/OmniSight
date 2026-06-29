"""Ensure HTTP write ports use typed async write services."""

from __future__ import annotations

from contextlib import asynccontextmanager
from unittest.mock import MagicMock, patch

import pytest
from src.core.deps.write import (
    get_autodiscover_write_port,
    get_ci_import_export_write_port,
    get_ci_write_port,
    get_correlation_write_port,
    get_graph_layout_write_port,
    get_relation_import_export_write_port,
    get_relation_write_port,
    get_transactional_autodiscover_write_port,
    get_transactional_ci_import_export_write_port,
    get_user_write_port,
)
from src.services.async_write.autodiscover import AsyncAutodiscoverWriteService
from src.services.async_write.ci import AsyncCiWriteService
from src.services.async_write.correlation import AsyncCorrelationWriteService
from src.services.async_write.graph_layout import AsyncGraphLayoutWriteService
from src.services.async_write.import_export import (
    AsyncCiImportExportWriteService,
    AsyncRelationImportExportWriteService,
)
from src.services.async_write.relations import AsyncRelationWriteService
from src.services.async_write.users import AsyncUserWriteService

NATIVE_WRITE_PORTS = (
    (get_ci_write_port, AsyncCiWriteService),
    (get_relation_write_port, AsyncRelationWriteService),
    (get_graph_layout_write_port, AsyncGraphLayoutWriteService),
    (get_user_write_port, AsyncUserWriteService),
    (get_correlation_write_port, AsyncCorrelationWriteService),
    (get_ci_import_export_write_port, AsyncCiImportExportWriteService),
    (get_autodiscover_write_port, AsyncAutodiscoverWriteService),
)

TRANSACTIONAL_WRITE_PORTS = (
    (get_transactional_ci_import_export_write_port, AsyncCiImportExportWriteService),
    (get_transactional_autodiscover_write_port, AsyncAutodiscoverWriteService),
    (get_relation_import_export_write_port, AsyncRelationImportExportWriteService),
)


def _fake_async_session_cm():
    @asynccontextmanager
    async def _cm():
        yield MagicMock()

    return _cm


@pytest.mark.asyncio
@pytest.mark.parametrize(("provider", "native_cls"), NATIVE_WRITE_PORTS)
async def test_native_write_ports(provider, native_cls):
    with patch("src.core.deps.write.database_async.async_write_session", _fake_async_session_cm()):
        port = await provider().__anext__()

    assert isinstance(port, native_cls)


@pytest.mark.asyncio
@pytest.mark.parametrize(("provider", "native_cls"), TRANSACTIONAL_WRITE_PORTS)
async def test_transactional_write_ports(provider, native_cls):
    with patch(
        "src.core.deps.write.database_async.async_transactional_write_session",
        _fake_async_session_cm(),
    ):
        port = await provider().__anext__()

    assert isinstance(port, native_cls)
