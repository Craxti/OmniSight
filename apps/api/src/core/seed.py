from sqlalchemy.orm import Session
from src.core.auth import hash_password
from src.core.config import settings
from src.core.session_commit import commit_session
from src.models import SyncProfile, User
from src.services.autodiscover.profile_defaults import DEFAULT_MAPPING_RULES


def _admin_password() -> str:
    if settings.admin_initial_password:
        if len(settings.admin_initial_password) < 12:
            raise RuntimeError("ADMIN_INITIAL_PASSWORD must be at least 12 characters")
        return settings.admin_initial_password
    if settings.is_production:
        raise RuntimeError("ADMIN_INITIAL_PASSWORD is required when seeding production")
    return "admin123"


def _seed_default_sync_profile(db: Session) -> None:
    if db.query(SyncProfile).filter(SyncProfile.name == "default-sync").first():
        return
    db.add(
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
    commit_session(db)


def seed_database(db: Session) -> None:
    if not db.query(User).filter(User.email == "admin@omnisight.local").first():
        db.add(
            User(
                email="admin@omnisight.local",
                hashed_password=hash_password(_admin_password()),
                role="admin",
            )
        )

    if not db.query(User).filter(User.email == "integration@omnisight.local").first():
        db.add(
            User(
                email="integration@omnisight.local",
                hashed_password=hash_password("integration-not-for-login"),
                role="viewer",
                is_active=True,
            )
        )

    from src.core.catalog_defaults import ensure_catalog_defaults

    ensure_catalog_defaults(db)
    _seed_default_sync_profile(db)

    from sqlalchemy import or_
    from src.models import CI
    from src.services.rsm.indexed_ids import sync_search_indexes

    needs_index = (
        db.query(CI.id)
        .filter(
            CI.is_deleted.is_(False),
            or_(
                CI.search_hostname.is_(None),
                CI.search_ip.is_(None),
            ),
            CI.external_ids.isnot(None),
        )
        .limit(1)
        .first()
    )
    if needs_index:
        for ci in db.query(CI).filter(CI.is_deleted.is_(False)).all():
            sync_search_indexes(ci)
        commit_session(db)
