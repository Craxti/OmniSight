"""Drop and recreate public schema (development recovery)."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import create_engine, text
from src.core.config import settings
from src.core.schema import bootstrap_database


def _terminate_backends(conn) -> int:
    result = conn.execute(
        text(
            """
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = current_database()
              AND pid <> pg_backend_pid()
            """
        )
    )
    return len(result.fetchall())


def _drop_and_recreate_schema(conn) -> None:
    conn.execute(text("SET lock_timeout = '2s'"))
    conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
    conn.execute(text("CREATE SCHEMA public"))


def main() -> None:
    engine = create_engine(
        settings.database_url,
        isolation_level="AUTOCOMMIT",
        connect_args={"connect_timeout": 5},
    )
    with engine.connect() as conn:
        for attempt in range(15):
            terminated = _terminate_backends(conn)
            print(f"terminated {terminated} backends (attempt {attempt + 1})")
            try:
                _drop_and_recreate_schema(conn)
                break
            except Exception as exc:
                if attempt == 14:
                    raise
                print(f"schema reset blocked ({exc}); retrying...")
                time.sleep(0.5)
        else:
            raise RuntimeError("Could not recreate schema; stop uvicorn/pytest and retry.")
    engine.dispose()
    print("Schema recreated.")
    bootstrap_database(seed=True)
    print("Seed applied.")


if __name__ == "__main__":
    main()
