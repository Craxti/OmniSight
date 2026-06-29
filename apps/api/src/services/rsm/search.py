"""RSM search helpers — internal implementation.

HTTP handlers use ``AsyncSearchService`` from ``core.deps`` as the public DI entry point.
"""

from typing import Any

from sqlalchemy.orm import Session
from src.core.constants import EXPORT_MAX_ROWS
from src.core.session_commit import commit_or_rollback
from src.models import CI
from src.repositories.protocols import CiRepositoryProtocol
from src.services.rsm.indexed_ids import merge_external_ids, sync_search_indexes

__all__ = ["merge_external_ids", "search_cis", "find_cis_for_alert", "backfill_search_indexes"]


def _extract_alert_lookup_fields(alert: dict[str, Any]) -> dict[str, Any | None]:
    """Normalize alert identifier keys used for CI lookup and merge filtering."""
    return {
        "cmdb_id": alert.get("cmdbId"),
        "hostname": alert.get("hostname"),
        "ip": alert.get("ip"),
        "external_id": alert.get("externalId"),
        "service_code": alert.get("serviceCode"),
        "application_code": alert.get("applicationCode"),
    }


def search_cis(
    db: Session,
    *,
    ci_repo: CiRepositoryProtocol,
    **kwargs: Any,
) -> tuple[list[CI], int]:
    return ci_repo.search(**kwargs)


def _ci_matches_alert(ci: CI, alert: dict[str, Any]) -> bool:
    ext = merge_external_ids(ci.attributes, ci.external_ids)
    fields = _extract_alert_lookup_fields(alert)
    matched = False

    cmdb_id = fields["cmdb_id"]
    if cmdb_id and str(ci.id) == str(cmdb_id):
        matched = True
    if fields["hostname"] and ext.get("hostname") == fields["hostname"]:
        matched = True
    if fields["ip"] and ext.get("ip") == fields["ip"]:
        matched = True
    if fields["external_id"] and ext.get("externalId") == fields["external_id"]:
        matched = True
    service_code = fields["service_code"]
    application_code = fields["application_code"]
    if service_code and application_code:
        if ext.get("serviceCode") == service_code and ext.get("applicationCode") == application_code:
            matched = True
    elif service_code and ext.get("serviceCode") == service_code:
        matched = True
    return matched


def find_cis_for_alert(db: Session, alert: dict[str, Any], *, ci_repo: CiRepositoryProtocol) -> list[CI]:
    """Indexed exact lookup + merge semantics (FR 31, 37)."""
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

    candidates = ci_repo.find_for_alert_conditions(conditions)
    return [ci for ci in candidates if _ci_matches_alert(ci, alert)]


def backfill_search_indexes(db: Session, *, ci_repo: CiRepositoryProtocol) -> int:
    cis = ci_repo.list_active(limit=EXPORT_MAX_ROWS)
    for ci in cis:
        sync_search_indexes(ci)
    commit_or_rollback(db)
    return len(cis)
