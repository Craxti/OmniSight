"""Native async default sync profile seeding."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from src.models import SyncProfile
from src.repositories.async_orm.autodiscover_repository import AsyncSyncProfileRepository
from src.services.autodiscover.profile_defaults import DEFAULT_MAPPING_RULES


async def ensure_default_sync_assets_async(
    session: AsyncSession,
    profiles: AsyncSyncProfileRepository | None = None,
) -> None:
    repo = profiles or AsyncSyncProfileRepository(session)
    if await repo.get_by_name("default-sync"):
        return
    session.add(
        SyncProfile(
            name="default-sync",
            description="Default serversivor autodiscover profile",
            connector_ids=[],
            source_types=["host", "api", "file", "db", "stream"],
            scope_mode="all",
            scope_config={"depth": 2},
            mapping_rules={
                **DEFAULT_MAPPING_RULES,
                "discover_relations": True,
                "create_missing_ci": True,
                "auto_apply": True,
            },
            auto_apply_threshold=0.85,
        )
    )
    await session.flush()
