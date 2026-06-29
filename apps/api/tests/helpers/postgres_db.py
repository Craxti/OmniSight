"""PostgreSQL test database helpers."""

from __future__ import annotations

import os

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import Session, sessionmaker
from src.core.config import settings
from src.models.base import Base
from src.core.seed import seed_database

_TEST_DB_NAME = "omnisight_test"


def test_database_url() -> str:
    return test_database_url_object().render_as_string(hide_password=False)


def test_database_url_object():
    explicit = os.getenv("TEST_DATABASE_URL", "").strip()
    if explicit:
        return make_url(explicit)
    url = make_url(settings.database_url)
    if url.host in (None, "localhost"):
        url = url.set(host="127.0.0.1")
    return url.set(database=_TEST_DB_NAME)


def _assert_safe_test_database(url) -> None:
    if url.database == _TEST_DB_NAME:
        return
    configured = make_url(settings.database_url).database
    if url.database == configured and url.database != _TEST_DB_NAME:
        raise RuntimeError(
            f"Refusing to modify main database '{configured}'. "
            f"Use a separate TEST_DATABASE_URL (default: {_TEST_DB_NAME})."
        )


def ensure_test_database_exists() -> None:
    target = test_database_url_object()
    _assert_safe_test_database(target)
    main = make_url(settings.database_url)
    if target.database == main.database:
        return
    engine = create_engine(settings.database_url, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": target.database},
            ).scalar()
            if not exists:
                conn.execute(text(f'CREATE DATABASE "{target.database}"'))
    finally:
        engine.dispose()


def create_test_engine() -> Engine:
    url = test_database_url_object()
    if url.drivername.startswith("sqlite"):
        raise RuntimeError("SQLite is not supported; set TEST_DATABASE_URL or DATABASE_URL to PostgreSQL")
    _assert_safe_test_database(url)
    ensure_test_database_exists()
    return create_engine(url, pool_pre_ping=True)


def dispose_application_engines() -> None:
    import src.core.database as db_module

    db_module.engine.dispose()


def prepare_clean_test_database(engine: Engine) -> None:
    _assert_safe_test_database(engine.url)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = current_database()
                  AND pid <> pg_backend_pid()
                """
            )
        )
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    from src.core.migrations import upgrade_head

    upgrade_head(engine.url.render_as_string(hide_password=False))


def reset_database(engine: Engine | None = None) -> None:
    url = test_database_url_object()
    _assert_safe_test_database(url)
    own_engine = engine is None
    trunc_engine = engine if engine is not None else create_test_engine()
    if own_engine:
        dispose_application_engines()
    try:
        inspector = sa_inspect(trunc_engine)
        existing = set(inspector.get_table_names())
        table_names = ", ".join(f'"{table.name}"' for table in Base.metadata.sorted_tables if table.name in existing)
        if not table_names:
            return
        with trunc_engine.begin() as conn:
            conn.execute(text("SET lock_timeout = '5s'"))
            conn.execute(text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE"))
    finally:
        if own_engine:
            trunc_engine.dispose()


def seed_test_database(engine: Engine) -> None:
    session = sessionmaker(bind=engine)()
    try:
        seed_database(session)
        session.commit()
    finally:
        session.close()


def fresh_session(engine: Engine) -> tuple[Session, sessionmaker]:
    reset_database()
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    seed_database(session)
    session.commit()
    return session, session_factory
