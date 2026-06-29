"""Pydantic cache deserialization registry."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel

_PYDANTIC_CACHE_MODELS: dict[str, Callable[[dict[str, Any]], BaseModel]] = {}


def register_cache_model(cls: type[BaseModel]) -> type[BaseModel]:
    """Register a Pydantic model for cache round-trip by class name."""
    _PYDANTIC_CACHE_MODELS[cls.__name__] = cls.model_validate
    return cls


def deserialize_cached_pydantic(cls_name: str, data: dict[str, Any]) -> Any:
    factory = _PYDANTIC_CACHE_MODELS.get(cls_name)
    if factory is None:
        return data
    return factory(data)


def _bootstrap_cache_models() -> None:
    from src.schemas.correlation import CorrelationResolvePayload
    from src.schemas.resources import ResourceGraphResponse

    register_cache_model(ResourceGraphResponse)
    register_cache_model(CorrelationResolvePayload)


_bootstrap_cache_models()
