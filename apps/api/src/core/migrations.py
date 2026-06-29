"""Alembic migration helpers."""

from __future__ import annotations

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from src.core.config import settings

logger = logging.getLogger("omnisight.api")

_API_ROOT = Path(__file__).resolve().parents[2]
_ALEMBIC_INI = _API_ROOT / "alembic.ini"
_BASELINE_REVISION = "001_baseline"


def alembic_config(database_url: str | None = None) -> Config:
    cfg = Config(str(_ALEMBIC_INI))
    cfg.set_main_option("script_location", str(_API_ROOT / "alembic"))
    cfg.set_main_option("prepend_sys_path", str(_API_ROOT))
    cfg.set_main_option("sqlalchemy.url", database_url or settings.database_url)
    return cfg


def alembic_version_exists(engine: Engine | None = None) -> bool:
    bind = engine or create_engine(settings.database_url, pool_pre_ping=True)
    own_engine = engine is None
    try:
        with bind.connect() as conn:
            exists = conn.execute(text("SELECT to_regclass('public.alembic_version') IS NOT NULL")).scalar()
            return bool(exists)
    except Exception:
        return False
    finally:
        if own_engine:
            bind.dispose()


def upgrade_head(database_url: str | None = None) -> None:
    command.upgrade(alembic_config(database_url), "head")


def stamp_head(database_url: str | None = None) -> None:
    command.stamp(alembic_config(database_url), "head")


def ensure_migrations_applied(database_url: str | None = None) -> bool:
    """Apply migrations. Returns True when schema was empty before migration."""
    url = database_url or settings.database_url
    engine = create_engine(url, pool_pre_ping=True)
    try:
        had_schema = _schema_marker_exists(engine)
        if alembic_version_exists(engine):
            upgrade_head(url)
            return False
        if had_schema:
            logger.info("Existing schema detected without alembic_version; stamping %s", _BASELINE_REVISION)
            stamp_head(url)
            return False
        logger.info("Applying baseline migration %s", _BASELINE_REVISION)
        upgrade_head(url)
        return True
    finally:
        engine.dispose()


def _schema_marker_exists(engine: Engine) -> bool:
    with engine.connect() as conn:
        return bool(conn.execute(text("SELECT to_regclass('public.users') IS NOT NULL")).scalar())
