"""Async session scope and service factory."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.core.async_service_factory import AsyncServiceFactory


@dataclass(slots=True)
class AsyncDbSessionScope:
    bundle: AsyncRepositoryBundle
    services: AsyncServiceFactory

    @classmethod
    def from_session(cls, session: AsyncSession) -> AsyncDbSessionScope:
        bundle = AsyncRepositoryBundle.from_session(session)
        return cls(bundle=bundle, services=AsyncServiceFactory(bundle))

    @property
    def session(self) -> AsyncSession:
        return self.bundle.session

    @property
    def ci(self):
        return self.bundle.ci

    @property
    def relations(self):
        return self.bundle.relations

    @property
    def ci_types(self):
        return self.bundle.ci_types

    @property
    def users(self):
        return self.bundle.users

    @property
    def audit(self):
        return self.bundle.audit
