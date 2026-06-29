"""Async alert-to-CI lookup."""

from __future__ import annotations

from typing import Any

from src.models import CI
from src.repositories.async_orm.ci_repository import AsyncCiRepository
from src.services.rsm.search import _ci_matches_alert, _extract_alert_lookup_fields


async def find_cis_for_alert_async(
    alert: dict[str, Any],
    *,
    ci_repo: AsyncCiRepository,
) -> list:
    fields = _extract_alert_lookup_fields(alert)
    conditions = []
    cmdb_id = fields["cmdb_id"]
    hostname = fields["hostname"]
    ip = fields["ip"]
    external_id = fields["external_id"]
    service_code = fields["service_code"]
    application_code = fields["application_code"]

    if cmdb_id is not None and str(cmdb_id).strip():
        try:
            conditions.append(CI.id == int(cmdb_id))
        except (TypeError, ValueError):
            pass
    if hostname:
        conditions.append(CI.search_hostname == hostname)
    if ip:
        conditions.append(CI.search_ip == ip)
    if external_id:
        conditions.append(CI.search_external_id == external_id)
    if service_code and application_code:
        conditions.append((CI.search_service_code == service_code) & (CI.search_application_code == application_code))
    elif service_code:
        conditions.append(CI.search_service_code == service_code)

    if not conditions:
        return []

    candidates = await ci_repo.find_for_alert_conditions(conditions)
    return [ci for ci in candidates if _ci_matches_alert(ci, alert)]
