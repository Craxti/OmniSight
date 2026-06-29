"""Alembic migration integration tests."""

from src.core.migrations import alembic_config, ensure_migrations_applied


def test_alembic_config_uses_database_url():
    cfg = alembic_config()
    url = cfg.get_main_option("sqlalchemy.url")
    assert url
    assert url.startswith("postgresql")


def test_ensure_migrations_applied_on_test_db(test_engine):
    url = test_engine.url.render_as_string(hide_password=False)
    created = ensure_migrations_applied(url)
    assert created is False
    from src.core.schema import schema_has_tables

    assert schema_has_tables(test_engine) is True
