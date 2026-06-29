"""Native async sync-connector CRUD."""

from __future__ import annotations

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.core.exceptions import DomainValidationError, NotFoundError
from src.models import SyncConnector
from src.repositories.async_orm.autodiscover_repository import AsyncSyncConnectorRepository
from src.schemas.autodiscover import (
    SyncConnectorCreate,
    SyncConnectorResponse,
    SyncConnectorUpdate,
)
from src.services.autodiscover.connectors.registry import SUPPORTED_CONNECTOR_TYPES
from src.services.autodiscover.serializers import connector_to_response
from src.services.base.async_domain import AsyncDomainService


class AsyncAutodiscoverConnectorWriteService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)
        self._connectors: AsyncSyncConnectorRepository = bundle.autodiscover_connectors

    async def _get_or_404(self, connector_id: int) -> SyncConnector:
        row = await self._connectors.get_by_id(connector_id)
        if not row:
            raise NotFoundError("Connector not found")
        return row

    async def create_connector(self, body: SyncConnectorCreate) -> SyncConnectorResponse:
        if body.connector_type not in SUPPORTED_CONNECTOR_TYPES:
            raise DomainValidationError(f"Unsupported connector type. Allowed: {SUPPORTED_CONNECTOR_TYPES}")
        if await self._connectors.get_by_name(body.name):
            raise DomainValidationError(f"Connector name already exists: {body.name}")
        connector = SyncConnector(
            name=body.name,
            connector_type=body.connector_type,
            server_ci_id=body.server_ci_id,
            config=body.config,
            credentials=body.credentials.model_dump(exclude_none=True) if body.credentials else None,
            timeout_seconds=body.timeout_seconds,
            max_retries=body.max_retries,
            read_only=True,
            enabled=body.enabled,
            auto_sync=body.auto_sync,
        )
        self._session.add(connector)
        await self._session.commit()
        await self._session.refresh(connector)
        return connector_to_response(connector)

    async def update_connector(self, connector_id: int, body: SyncConnectorUpdate) -> SyncConnectorResponse:
        connector = await self._get_or_404(connector_id)
        data = body.model_dump(exclude_unset=True)
        if "name" in data and data["name"] != connector.name:
            if await self._connectors.get_by_name(data["name"]):
                raise DomainValidationError(f"Connector name already exists: {data['name']}")
        if "credentials" in data and data["credentials"] is not None:
            data["credentials"] = body.credentials.model_dump(exclude_none=True) if body.credentials else None
        for key, value in data.items():
            setattr(connector, key, value)
        await self._session.commit()
        await self._session.refresh(connector)
        return connector_to_response(connector)

    async def delete_connector(self, connector_id: int) -> dict:
        connector = await self._get_or_404(connector_id)
        await self._session.delete(connector)
        await self._session.commit()
        return {"ok": True}
