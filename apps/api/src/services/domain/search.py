"""Shared resource search read logic (sync + async)."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from src.core.serializers import ci_to_response
from src.schemas.resources import ResourceSearchResponse


def resource_search_cache_key(**kwargs: Any) -> str:
    payload = {k: v for k, v in sorted(kwargs.items()) if v is not None and v != ""}
    return f"resource_search:{json.dumps(payload, sort_keys=True, default=str)}"


def build_resource_search_response(cis: list[Any], total: int) -> ResourceSearchResponse:
    return ResourceSearchResponse(items=[ci_to_response(c) for c in cis], total=total)


def resource_search_cached(
    *,
    cache_get: Callable[[str], ResourceSearchResponse | None],
    cache_set: Callable[[str, ResourceSearchResponse, int], None],
    search: Callable[..., tuple[list[Any], int]],
    ttl: int = 30,
    **kwargs: Any,
) -> ResourceSearchResponse:
    cache_key = resource_search_cache_key(**kwargs)
    hit = cache_get(cache_key)
    if hit is not None:
        return hit
    cis, total = search(**kwargs)
    result = build_resource_search_response(cis, total)
    cache_set(cache_key, result, ttl)
    return result
