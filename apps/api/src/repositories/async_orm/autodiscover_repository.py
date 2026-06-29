from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models import AutodiscoverMapping, AutodiscoverRun, SyncConnector, SyncProfile
from src.repositories.async_base import AsyncRepository


class AsyncSyncConnectorRepository(AsyncRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_by_id(self, connector_id: int) -> SyncConnector | None:
        return await self.scalar_one_or_none(select(SyncConnector).where(SyncConnector.id == connector_id))

    async def get_by_name(self, name: str) -> SyncConnector | None:
        return await self.scalar_one_or_none(select(SyncConnector).where(SyncConnector.name == name))

    async def list_ordered(self, *, enabled_only: bool = True) -> list[SyncConnector]:
        stmt = select(SyncConnector)
        if enabled_only:
            stmt = stmt.where(SyncConnector.enabled.is_(True))
        return await self.scalars_all(stmt.order_by(SyncConnector.name))

    async def resolve_enabled(
        self,
        *,
        connector_ids: list[int] | None,
        server_ci_ids: list[int] | None,
        source_types: list[str] | None,
    ) -> list[SyncConnector]:
        if connector_ids:
            stmt = select(SyncConnector).where(
                SyncConnector.enabled.is_(True),
                SyncConnector.id.in_(connector_ids),
            )
        elif server_ci_ids:
            stmt = select(SyncConnector).where(
                SyncConnector.enabled.is_(True),
                SyncConnector.server_ci_id.in_(server_ci_ids),
            )
        else:
            return []
        if source_types:
            stmt = stmt.where(SyncConnector.connector_type.in_(source_types))
        return await self.scalars_all(stmt)

    async def list_auto_sync_due(self) -> list[SyncConnector]:
        stmt = (
            select(SyncConnector)
            .where(SyncConnector.enabled.is_(True), SyncConnector.auto_sync.is_(True))
            .order_by(SyncConnector.id)
        )
        return await self.scalars_all(stmt)


class AsyncSyncProfileRepository(AsyncRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_by_id(self, profile_id: int) -> SyncProfile | None:
        return await self.scalar_one_or_none(select(SyncProfile).where(SyncProfile.id == profile_id))

    async def get_by_name(self, name: str) -> SyncProfile | None:
        return await self.scalar_one_or_none(select(SyncProfile).where(SyncProfile.name == name))

    async def list_all(self) -> list[SyncProfile]:
        return await self.scalars_all(select(SyncProfile).order_by(SyncProfile.name))


class AsyncAutodiscoverRunRepository(AsyncRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_by_id(self, run_id: int) -> AutodiscoverRun | None:
        return await self.scalar_one_or_none(select(AutodiscoverRun).where(AutodiscoverRun.id == run_id))

    async def get_with_mappings(self, run_id: int) -> AutodiscoverRun | None:
        stmt = select(AutodiscoverRun).options(joinedload(AutodiscoverRun.mappings)).where(AutodiscoverRun.id == run_id)
        return await self.scalar_one_or_none(stmt)

    async def list_recent(self, limit: int = 20) -> list[AutodiscoverRun]:
        stmt = select(AutodiscoverRun).order_by(AutodiscoverRun.id.desc()).limit(limit)
        return await self.scalars_all(stmt)


class AsyncAutodiscoverMappingRepository(AsyncRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def list_for_run(self, run_id: int) -> list[AutodiscoverMapping]:
        stmt = (
            select(AutodiscoverMapping)
            .where(AutodiscoverMapping.run_id == run_id)
        )
        return await self.scalars_all(stmt)

    async def list_pending_for_apply(
        self,
        run_id: int,
        *,
        mapping_ids: list[str] | None = None,
        apply_auto_only: bool = False,
    ) -> list[AutodiscoverMapping]:
        stmt = select(AutodiscoverMapping).where(
            AutodiscoverMapping.run_id == run_id,
            AutodiscoverMapping.applied_at.is_(None),
        )
        if mapping_ids is not None:
            stmt = stmt.where(AutodiscoverMapping.mapping_id.in_(mapping_ids))
        elif apply_auto_only:
            stmt = stmt.where(
                AutodiscoverMapping.status == "auto",
                AutodiscoverMapping.selected.is_(True),
            )
        return await self.scalars_all(stmt)

    async def list_auto_apply_ids(self, run_id: int) -> list[str]:
        stmt = select(AutodiscoverMapping.mapping_id).where(
            AutodiscoverMapping.run_id == run_id,
            AutodiscoverMapping.status.in_(["auto", "needs_confirmation"]),
        )
        result = await self.execute(stmt)
        return [row[0] for row in result.all()]
