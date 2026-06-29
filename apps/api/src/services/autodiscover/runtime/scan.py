"""Native async autodiscover scan pipeline."""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

from src.core.exceptions import DomainValidationError, NotFoundError
from src.models import AutodiscoverMapping, AutodiscoverRun, SyncConnector, User
from src.repositories.async_orm.autodiscover_repository import (
    AsyncAutodiscoverMappingRepository,
    AsyncAutodiscoverRunRepository,
    AsyncSyncConnectorRepository,
    AsyncSyncProfileRepository,
)
from src.repositories.async_orm.ci_repository import AsyncCiRepository
from src.repositories.async_orm.ci_type_repository import AsyncCITypeRepository
from src.repositories.async_orm.relation_repository import AsyncRelationRepository
from src.repositories.async_orm.relation_type_repository import AsyncRelationTypeRepository
from src.schemas.autodiscover import (
    AutodiscoverScanRequest,
    AutodiscoverScanResponse,
    SyncConnectorSyncResponse,
)
from src.services.autodiscover.auto_sync_request import connector_auto_sync_request
from src.services.autodiscover.connectors.registry import discover_with_retry
from src.services.autodiscover.runtime.apply_run import AsyncAutodiscoverApplyService
from src.services.autodiscover.runtime.mapping import map_discovered_entities_async
from src.services.autodiscover.runtime.scope import resolve_scope_ci_ids_async
from src.services.autodiscover.runtime.seed import ensure_default_sync_assets_async
from src.services.autodiscover.scan_finalizer import ScanRunFinalizer
from src.services.autodiscover.scan_models import CollectResult, ScanConfig
from src.services.autodiscover.scope import ssh_target_of
from src.services.autodiscover.serializers import run_to_scan_response
from src.services.base.async_domain import AsyncDomainService


class AsyncAutodiscoverScanService(AsyncDomainService):
    def __init__(self, bundle) -> None:
        super().__init__(bundle)
        self._connectors: AsyncSyncConnectorRepository = bundle.autodiscover_connectors
        self._profiles: AsyncSyncProfileRepository = bundle.autodiscover_profiles
        self._runs: AsyncAutodiscoverRunRepository = bundle.autodiscover_runs
        self._mappings: AsyncAutodiscoverMappingRepository = bundle.autodiscover_mappings
        self._ci: AsyncCiRepository = bundle.ci
        self._relations: AsyncRelationRepository = bundle.relations
        self._relation_types: AsyncRelationTypeRepository = bundle.relation_types
        self._types: AsyncCITypeRepository = bundle.ci_types
        self._apply = AsyncAutodiscoverApplyService(bundle)
        self._finalizer = ScanRunFinalizer()

    async def run_scan(self, body: AutodiscoverScanRequest, user: User) -> AutodiscoverScanResponse:
        await ensure_default_sync_assets_async(self._session, self._profiles)
        config = await self._resolve_config(body)
        run = await self._create_run(body, user, config)
        scope_ids = await resolve_scope_ci_ids_async(
            scope_mode=config.scope_mode,
            scope_config=config.scope_config,
            server_ci_ids=config.server_ci_ids or [c.server_ci_id for c in config.connectors if c.server_ci_id],
            ci_repo=self._ci,
            rel_repo=self._relations,
        )
        collected = await self._collect(config, scope_ids)
        await self._persist_mappings(run, collected.all_mappings)
        self._finalizer.finalize(run, config=config, collected=collected)
        await self._maybe_auto_apply(run, body, user)
        await self._session.commit()
        loaded = await self._runs.get_with_mappings(run.id)
        if not loaded:
            raise NotFoundError("Autodiscover run not found")
        return run_to_scan_response(loaded)

    async def sync_connector(self, connector_id: int, user: User) -> SyncConnectorSyncResponse:
        connector = await self._connectors.get_by_id(connector_id)
        if not connector:
            raise NotFoundError("Connector not found")
        try:
            scan = await self.run_scan(connector_auto_sync_request(connector.id), user)
        except (DomainValidationError, ValueError) as exc:
            return SyncConnectorSyncResponse(run_id=0, status="failed", error=str(exc))
        return SyncConnectorSyncResponse(
            run_id=scan.run_id,
            status=scan.status,
            sources_ok=scan.sources_ok,
            fields_found=scan.fields_found,
            apply_result=scan.apply_result,
        )

    async def _resolve_config(self, body: AutodiscoverScanRequest) -> ScanConfig:
        profile = await self._profiles.get_by_id(body.profile_id) if body.profile_id else None

        connector_ids = body.connector_ids or (profile.connector_ids if profile else None)
        server_ci_ids = body.server_ci_ids or []
        source_types = body.source_types or (profile.source_types if profile else None)
        scope_mode = body.scope_mode or (profile.scope_mode if profile else "graph")
        scope_config = {**(profile.scope_config if profile else {}), **(body.scope_config or {})}
        if body.scope_depth is not None:
            scope_config["depth"] = body.scope_depth
        if body.root_ci_id is not None:
            scope_config["root_ci_id"] = body.root_ci_id

        mapping_rules = {**(profile.mapping_rules if profile else {}), **(body.mapping_rules or {})}
        if body.discover_relations is not None:
            mapping_rules["discover_relations"] = body.discover_relations
        if body.create_missing_ci is not None:
            mapping_rules["create_missing_ci"] = body.create_missing_ci
        if profile:
            mapping_rules.setdefault("auto_apply_threshold", profile.auto_apply_threshold)

        connectors = await self._connectors.resolve_enabled(
            connector_ids=connector_ids,
            server_ci_ids=server_ci_ids if not connector_ids else None,
            source_types=source_types,
        )
        if not connectors:
            raise DomainValidationError(
                "No sync connectors found. Add a connector in Settings → Sync / Autodiscover "
                "and link it to the selected Server CI."
            )

        previous_schema = None
        if profile and profile.last_run_id:
            prev_run = await self._runs.get_by_id(profile.last_run_id)
            previous_schema = prev_run.discovered_schema if prev_run else None

        return ScanConfig(
            profile=profile,
            connector_ids=connector_ids,
            server_ci_ids=server_ci_ids,
            source_types=source_types,
            scope_mode=scope_mode,
            scope_config=scope_config,
            mapping_rules=mapping_rules,
            connectors=connectors,
            previous_schema=previous_schema,
        )

    async def _create_run(
        self,
        body: AutodiscoverScanRequest,
        user: User,
        config: ScanConfig,
    ) -> AutodiscoverRun:
        run = AutodiscoverRun(
            profile_id=config.profile.id if config.profile else None,
            status="running",
            user_email=user.email,
            request_snapshot=body.model_dump(),
            report={},
            discovered_schema={},
            previous_schema=config.previous_schema,
        )
        self._session.add(run)
        await self._session.flush()
        return run

    async def _collect(self, config: ScanConfig, scope_ids: set[int]) -> CollectResult:
        source_reports: list[dict[str, Any]] = []
        all_mappings: list[dict[str, Any]] = []
        schemas: list[dict[str, Any]] = []
        sources_ok = 0

        for connector in config.connectors:
            server_hostname, server_name = await self._server_target(connector)
            result = await asyncio.to_thread(discover_with_retry, connector, server_hostname)
            source_reports.append(self._source_report(connector, server_name, server_hostname, result))
            if not result.ok:
                continue
            sources_ok += 1
            if result.schema:
                schemas.append(result.schema.to_dict())
            all_mappings.extend(
                await map_discovered_entities_async(
                    entities=result.entities,
                    scope_ids=scope_ids,
                    rules=config.mapping_rules,
                    source_server=server_hostname or connector.name,
                    source_connector=connector.name,
                    scope_mode=config.scope_mode,
                    server_ci_id=connector.server_ci_id,
                    ci_repo=self._ci,
                    rel_repo=self._relations,
                    type_repo=self._types,
                    relation_type_repo=self._relation_types,
                )
            )

        return CollectResult(
            source_reports=source_reports,
            all_mappings=all_mappings,
            schemas=schemas,
            sources_ok=sources_ok,
        )

    async def _server_target(self, connector: SyncConnector) -> tuple[str | None, str]:
        server_name = connector.name
        server_hostname = None
        if connector.server_ci_id:
            server = await self._ci.get_active(connector.server_ci_id)
            if server:
                server_name = server.name
                server_hostname = ssh_target_of(server)
        return server_hostname, server_name

    @staticmethod
    def _source_report(
        connector: SyncConnector,
        server_name: str,
        server_hostname: str | None,
        result: Any,
    ) -> dict[str, Any]:
        return {
            "connector_id": connector.id,
            "connector_name": connector.name,
            "connector_type": connector.connector_type,
            "server_ci_id": connector.server_ci_id,
            "server_name": server_name,
            "hostname": server_hostname,
            "ok": result.ok,
            "records_found": len(result.entities),
            "error": result.error,
            "duration_ms": result.duration_ms,
            "attempts": result.attempts,
        }

    async def _persist_mappings(self, run: AutodiscoverRun, mappings: list[dict[str, Any]]) -> None:
        for item in mappings:
            kind = item.get("mapping_kind", "field")
            if kind == "relation":
                mid = f"rel:{item['ci_id']}:{item['relation_type']}:{item['discovered_value']}:{uuid.uuid4().hex[:8]}"
            elif kind == "ci_create":
                mid = f"ci:{item['discovered_value']}:{uuid.uuid4().hex[:8]}"
            else:
                mid = f"{item['ci_id']}:{item['field']}:{uuid.uuid4().hex[:8]}"
            self._session.add(
                AutodiscoverMapping(
                    run_id=run.id,
                    mapping_id=mid,
                    mapping_kind=kind,
                    ci_id=item.get("ci_id"),
                    ci_name=item["ci_name"],
                    target_ci_id=item.get("target_ci_id"),
                    target_ci_name=item.get("target_ci_name"),
                    relation_type=item.get("relation_type"),
                    field=item["field"],
                    payload=item.get("payload"),
                    current_value=item.get("current_value"),
                    discovered_value=item["discovered_value"],
                    source_server=item["source_server"],
                    source_connector=item["source_connector"],
                    confidence=item["confidence"],
                    status=item["status"],
                    selected=item["status"] == "auto",
                )
            )
        await self._session.flush()

    async def _maybe_auto_apply(self, run: AutodiscoverRun, body: AutodiscoverScanRequest, user: User) -> None:
        if not body.auto_apply:
            return
        applicable_ids = await self._mappings.list_auto_apply_ids(run.id)
        apply_result: dict[str, Any] = {
            "applied": 0,
            "skipped": 0,
            "errors": [],
            "updated_ci_ids": [],
            "created_cis": 0,
            "applied_relations": 0,
        }
        if applicable_ids:
            response = await self._apply.apply_run(run.id, user=user, mapping_ids=applicable_ids)
            apply_result = response.model_dump()
        run.report = {**(run.report or {}), "apply_result": apply_result}
