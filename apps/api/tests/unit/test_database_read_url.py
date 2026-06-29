"""Tests for DATABASE_READ_URL wiring."""

from __future__ import annotations

from src.core.database_async import _to_async_url


def test_to_async_url_converts_postgres_read_replica():
    url = "postgresql+psycopg2://user:pass@replica:5432/omnisight"
    assert _to_async_url(url) == "postgresql+asyncpg://user:pass@replica:5432/omnisight"
