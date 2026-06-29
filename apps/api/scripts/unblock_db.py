"""Unblock main PostgreSQL database (terminate stuck backends)."""

import psycopg2
from sqlalchemy.engine.url import make_url
from src.core.config import settings

target = make_url(settings.database_url)
conn = psycopg2.connect(
    host=target.host or "127.0.0.1",
    port=target.port or 5432,
    user=target.username,
    password=target.password,
    dbname=target.database,
    connect_timeout=5,
)
conn.autocommit = True
cur = conn.cursor()
cur.execute(
    """
    SELECT pg_terminate_backend(pid)
    FROM pg_stat_activity
    WHERE datname = %s
      AND pid <> pg_backend_pid()
    """,
    (target.database,),
)
terminated = cur.fetchall()
print(f"terminated {len(terminated)} backends on {target.database}")
conn.close()
