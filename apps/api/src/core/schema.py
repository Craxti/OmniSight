"""PostgreSQL schema bootstrap via Alembic migrations."""

from __future__ import annotations

import logging

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.exc import DBAPIError, OperationalError
from src.core.config import settings
from src.core.database import engine, sync_session
from src.core.migrations import ensure_migrations_applied
from src.core.seed import seed_database

logger = logging.getLogger("omnisight.api")

_SCHEMA_MARKER_TABLE = "users"
_BOOTSTRAP_TIMEOUT_MS = 10_000


def _apply_session_timeouts(db) -> None:
    db.execute(text(f"SET statement_timeout = '{_BOOTSTRAP_TIMEOUT_MS}'"))
    db.execute(text("SET lock_timeout = '3s'"))


def ensure_application_database_exists() -> None:
    """Create the configured database when connecting to a dedicated DB name."""
    target = make_url(settings.database_url)
    db_name = (target.database or "").strip()
    if not db_name or db_name == "postgres":
        if db_name == "postgres":
            logger.warning(
                "DATABASE_URL uses shared database 'postgres'; "
                "prefer a dedicated database (e.g. omnisight) to avoid lock contention"
            )
        return

    admin = target.set(database="postgres")
    admin_engine = create_engine(
        admin.render_as_string(hide_password=False),
        isolation_level="AUTOCOMMIT",
        connect_args={"connect_timeout": 5},
    )
    try:
        with admin_engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": db_name},
            ).scalar()
            if not exists:
                conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                logger.info("Created database %s", db_name)
    finally:
        admin_engine.dispose()


def schema_has_tables(db_engine: Engine | None = None) -> bool:
    bind = db_engine or engine
    try:
        with bind.connect() as conn:
            conn.execute(text(f"SET statement_timeout = '{_BOOTSTRAP_TIMEOUT_MS}'"))
            result = conn.execute(
                text("SELECT to_regclass(:qualified) IS NOT NULL"),
                {"qualified": f"public.{_SCHEMA_MARKER_TABLE}"},
            )
            return bool(result.scalar())
    except (OperationalError, DBAPIError, TimeoutError) as exc:
        logger.warning("schema check failed: %s", exc)
        return False


def ensure_database_schema(db_engine: Engine | None = None) -> bool:
    """Apply Alembic migrations when the schema is missing or behind."""
    bind = db_engine or engine
    url = bind.url.render_as_string(hide_password=False)
    return ensure_migrations_applied(url)


def bootstrap_database(*, seed: bool = True, db_engine: Engine | None = None) -> None:
    """Ensure schema exists and apply base seed when admin user is absent."""
    from src.models import User

    ensure_application_database_exists()
    created = ensure_database_schema(db_engine)
    if not seed:
        return

    with sync_session() as db:
        try:
            _apply_session_timeouts(db)
            from src.core.catalog_defaults import ensure_catalog_defaults

            ensure_catalog_defaults(db)
            db.commit()
            if db.query(User).filter(User.email == "admin@omnisight.local").first():
                return
            seed_database(db)
            db.commit()
        except (OperationalError, DBAPIError, TimeoutError) as exc:
            db.rollback()
            if created:
                logger.error("database bootstrap failed after schema create: %s", exc)
                raise
            logger.warning("seed check skipped (database busy), continuing startup: %s", exc)
