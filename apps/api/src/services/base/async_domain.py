"""Base classes for HTTP-facing async domain services."""

from __future__ import annotations

from src.core.async_repository_bundle import AsyncRepositoryBundle


class AsyncDomainService:
    """Shared root for HTTP-facing async services (read and write)."""

    __slots__ = ("_bundle", "_session")

    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        self._bundle = bundle
        self._session = bundle.session
