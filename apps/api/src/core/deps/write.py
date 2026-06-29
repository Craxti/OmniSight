"""Write dependency providers (native async ORM)."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable

from src.core import database_async
from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.services.async_write.autodiscover import AsyncAutodiscoverWriteService
from src.services.async_write.ci import AsyncCiWriteService
from src.services.async_write.ci_types import AsyncCiTypeWriteService
from src.services.async_write.correlation import AsyncCorrelationWriteService
from src.services.async_write.graph_layout import AsyncGraphLayoutWriteService
from src.services.async_write.import_export import (
    AsyncCiImportExportWriteService,
    AsyncRelationImportExportWriteService,
)
from src.services.async_write.relation_types import AsyncRelationTypeWriteService
from src.services.async_write.relations import AsyncRelationWriteService
from src.services.async_write.users import AsyncUserWriteService


def _native_write_port(native_factory: Callable[[AsyncRepositoryBundle], object]):
    async def provider() -> AsyncGenerator[object, None]:
        async with database_async.async_write_session() as session:
            yield native_factory(AsyncRepositoryBundle.from_session(session))

    return provider


def _transactional_write_port(native_factory: Callable[[AsyncRepositoryBundle], object]):
    async def provider() -> AsyncGenerator[object, None]:
        async with database_async.async_transactional_write_session() as session:
            yield native_factory(AsyncRepositoryBundle.from_session(session))

    return provider


get_ci_write_port = _native_write_port(AsyncCiWriteService)
get_relation_write_port = _native_write_port(AsyncRelationWriteService)
get_relation_type_write_port = _native_write_port(AsyncRelationTypeWriteService)
get_graph_layout_write_port = _native_write_port(AsyncGraphLayoutWriteService)
get_ci_type_write_port = _native_write_port(AsyncCiTypeWriteService)
get_user_write_port = _native_write_port(AsyncUserWriteService)
get_correlation_write_port = _native_write_port(AsyncCorrelationWriteService)

get_ci_import_export_write_port = _native_write_port(AsyncCiImportExportWriteService)
get_relation_import_export_write_port = _transactional_write_port(AsyncRelationImportExportWriteService)
get_autodiscover_write_port = _native_write_port(AsyncAutodiscoverWriteService)

get_transactional_ci_import_export_write_port = _transactional_write_port(AsyncCiImportExportWriteService)
get_transactional_autodiscover_write_port = _transactional_write_port(AsyncAutodiscoverWriteService)
