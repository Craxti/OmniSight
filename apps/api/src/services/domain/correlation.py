"""Shared correlation read response builders (sync + async)."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from src.core.pagination import pagination_meta
from src.core.serializers import ci_to_response
from src.schemas.correlation import (
    ChainCheckResponse,
    CorrelationMatchResult,
    CorrelationResolvePayload,
)


def resolve_batch_cache_key(
    alerts: list[dict[str, Any]],
    *,
    page: int = 1,
    page_size: int | None = None,
) -> str:
    return f"resolve:{json.dumps(alerts, sort_keys=True, default=str)}:{page}:{page_size}"


def paginate_alerts(
    alerts: list[dict[str, Any]],
    *,
    page: int = 1,
    page_size: int | None = None,
) -> tuple[list[dict[str, Any]], dict[str, int] | None]:
    total = len(alerts)
    if page_size is not None:
        start = (page - 1) * page_size
        return alerts[start : start + page_size], pagination_meta(total, page, page_size)
    return alerts, None


def match_alert_to_result(alert: dict[str, Any], matches: list[Any]) -> CorrelationMatchResult:
    hostname = alert.get("hostname")
    ip = alert.get("ip")
    ambiguous = len(matches) > 1 and bool(hostname or ip)
    if not matches:
        return CorrelationMatchResult(alert=alert, resolved=False, resource=None, ambiguous=False)
    return CorrelationMatchResult(
        alert=alert,
        resolved=True,
        ambiguous=ambiguous,
        resource=ci_to_response(matches[0]),
        match_count=len(matches),
    )


def build_resolve_payload(
    resolved: list[CorrelationMatchResult],
    unresolved: list[CorrelationMatchResult],
    *,
    pagination: dict[str, int] | None,
) -> CorrelationResolvePayload:
    return CorrelationResolvePayload(
        resolved=resolved,
        unresolved=unresolved,
        schema_version="rsm-correlation-v1",
        pagination=pagination,
    )


def build_chain_check_response(resource_ids: list[int], chain_related: bool) -> ChainCheckResponse:
    return ChainCheckResponse(resource_ids=resource_ids, chain_related=chain_related)


def resolve_batch_cached(
    alerts: list[dict[str, Any]],
    *,
    cache_get: Callable[[str], CorrelationResolvePayload | None],
    cache_set: Callable[[str, CorrelationResolvePayload, int], None],
    match_alert: Callable[[dict[str, Any]], list[Any]],
    page: int = 1,
    page_size: int | None = None,
    ttl: int = 30,
) -> CorrelationResolvePayload:
    cache_key = resolve_batch_cache_key(alerts, page=page, page_size=page_size)
    hit = cache_get(cache_key)
    if hit is not None:
        return hit

    slice_alerts, pagination = paginate_alerts(alerts, page=page, page_size=page_size)
    resolved: list[CorrelationMatchResult] = []
    unresolved: list[CorrelationMatchResult] = []
    for alert in slice_alerts:
        result = match_alert_to_result(alert, match_alert(alert))
        if result.resolved:
            resolved.append(result)
        else:
            unresolved.append(result)

    payload = build_resolve_payload(resolved, unresolved, pagination=pagination)
    cache_set(cache_key, payload, ttl)
    return payload
