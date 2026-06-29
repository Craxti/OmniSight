"""Native async scheduled connector auto-sync."""

from __future__ import annotations

import logging

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.core.database_async import async_write_session
from src.services.autodiscover.runtime.scan import AsyncAutodiscoverScanService

logger = logging.getLogger("omnisight.autodiscover.auto_sync")


async def _sync_connector(connector_id: int, connector_name: str, *, user_email: str) -> dict:
    async with async_write_session() as session:
        bundle = AsyncRepositoryBundle.from_session(session)
        user = await bundle.users.get_by_email(user_email)
        if not user:
            return {
                "connector_id": connector_id,
                "connector_name": connector_name,
                "status": "failed",
                "error": "integration user not found",
            }
        scan = AsyncAutodiscoverScanService(bundle)
        response = await scan.sync_connector(connector_id, user)

    apply_result = response.apply_result.model_dump() if response.apply_result else {}
    result = {
        "run_id": response.run_id,
        "status": response.status,
        "sources_ok": response.sources_ok,
        "fields_found": response.fields_found,
        "apply_result": apply_result,
    }
    return {"connector_id": connector_id, "connector_name": connector_name, **result}


async def run_scheduled_auto_sync_async(*, user_email: str) -> list[dict]:
    """Sync enabled auto_sync connectors; each connector uses its own short-lived DB session."""
    async with async_write_session() as session:
        bundle = AsyncRepositoryBundle.from_session(session)
        connectors = await bundle.autodiscover_connectors.list_auto_sync_due()
        connector_jobs = [(connector.id, connector.name) for connector in connectors]

    results: list[dict] = []
    for connector_id, connector_name in connector_jobs:
        try:
            result = await _sync_connector(connector_id, connector_name, user_email=user_email)
            results.append(result)
            logger.info(
                "auto_sync connector=%s run_id=%s status=%s applied=%s",
                connector_name,
                result.get("run_id"),
                result.get("status"),
                (result.get("apply_result") or {}).get("applied", 0),
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("auto_sync failed connector=%s: %s", connector_name, exc)
            results.append(
                {
                    "connector_id": connector_id,
                    "connector_name": connector_name,
                    "status": "failed",
                    "error": str(exc),
                }
            )
    return results
