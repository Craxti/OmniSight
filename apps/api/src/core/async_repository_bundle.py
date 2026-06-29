"""Async session-scoped repository bundle."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.async_orm.audit_repository import AsyncAuditRepository
from src.repositories.async_orm.autodiscover_repository import (
    AsyncAutodiscoverMappingRepository,
    AsyncAutodiscoverRunRepository,
    AsyncSyncConnectorRepository,
    AsyncSyncProfileRepository,
)
from src.repositories.async_orm.ci_repository import AsyncCiRepository
from src.repositories.async_orm.ci_type_repository import AsyncCITypeRepository
from src.repositories.async_orm.graph_layout_repository import AsyncGraphLayoutRepository
from src.repositories.async_orm.relation_repository import AsyncRelationRepository
from src.repositories.async_orm.relation_type_repository import AsyncRelationTypeRepository
from src.repositories.async_orm.user_repository import AsyncUserRepository


@dataclass(slots=True)
class AsyncRepositoryBundle:
    session: AsyncSession
    ci: AsyncCiRepository
    relations: AsyncRelationRepository
    relation_types: AsyncRelationTypeRepository
    ci_types: AsyncCITypeRepository
    users: AsyncUserRepository
    audit: AsyncAuditRepository
    autodiscover_connectors: AsyncSyncConnectorRepository
    autodiscover_profiles: AsyncSyncProfileRepository
    autodiscover_runs: AsyncAutodiscoverRunRepository
    autodiscover_mappings: AsyncAutodiscoverMappingRepository
    graph_layout: AsyncGraphLayoutRepository

    @classmethod
    def from_session(cls, session: AsyncSession) -> AsyncRepositoryBundle:
        return cls(
            session=session,
            ci=AsyncCiRepository(session),
            relations=AsyncRelationRepository(session),
            relation_types=AsyncRelationTypeRepository(session),
            ci_types=AsyncCITypeRepository(session),
            users=AsyncUserRepository(session),
            audit=AsyncAuditRepository(session),
            autodiscover_connectors=AsyncSyncConnectorRepository(session),
            autodiscover_profiles=AsyncSyncProfileRepository(session),
            autodiscover_runs=AsyncAutodiscoverRunRepository(session),
            autodiscover_mappings=AsyncAutodiscoverMappingRepository(session),
            graph_layout=AsyncGraphLayoutRepository(session),
        )
