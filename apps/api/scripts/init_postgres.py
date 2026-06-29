#!/usr/bin/env python3
"""Create OmniSight PostgreSQL role and database on localhost."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"

HOST = os.environ.get("POSTGRES_HOST", "127.0.0.1")
PORT = int(os.environ.get("POSTGRES_PORT", "5432"))
ADMIN_USER = os.environ.get("POSTGRES_USER", "postgres")
ADMIN_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "")
DB_NAME = os.environ.get("OMNISIGHT_DB", "omnisight")
DB_USER = os.environ.get("OMNISIGHT_USER", "omnisight")
DB_PASSWORD = os.environ.get("OMNISIGHT_PASSWORD", "omnisight")


def database_url() -> str:
    return f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{HOST}:{PORT}/{DB_NAME}"


def write_env() -> None:
    lines: list[str] = []
    if ENV_PATH.exists():
        lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
    url = database_url()
    updated = False
    for i, line in enumerate(lines):
        if line.startswith("DATABASE_URL="):
            lines[i] = f"DATABASE_URL={url}"
            updated = True
            break
    if not updated:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append(f"DATABASE_URL={url}")
    if not any(line.startswith("SECRET_KEY=") for line in lines):
        lines.append("SECRET_KEY=change-me-in-production")
    if not any(line.startswith("API_KEY=") for line in lines):
        lines.append("API_KEY=omnisight-api-key-dev")
    if not any(line.startswith("WEBHOOK_SECRET=") for line in lines):
        lines.append("WEBHOOK_SECRET=omnisight-webhook-secret-dev")
    if not any(line.startswith("CORS_ORIGINS=") for line in lines):
        lines.append("CORS_ORIGINS=http://localhost:5173,http://localhost:3000")
    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not ADMIN_PASSWORD:
        print(
            "Укажите пароль суперпользователя PostgreSQL:\n"
            "  PowerShell: $env:POSTGRES_PASSWORD = 'ваш_пароль'\n"
            "  python scripts/init_postgres.py",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            user=ADMIN_USER,
            password=ADMIN_PASSWORD,
            dbname="postgres",
        )
    except psycopg2.Error as exc:
        print(f"Не удалось подключиться к PostgreSQL ({ADMIN_USER}@{HOST}:{PORT}): {exc}", file=sys.stderr)
        sys.exit(1)

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (DB_USER,))
    if not cur.fetchone():
        cur.execute(
            sql.SQL("CREATE ROLE {} WITH LOGIN PASSWORD %s").format(sql.Identifier(DB_USER)),
            (DB_PASSWORD,),
        )
        print(f"Создан пользователь: {DB_USER}")

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    if not cur.fetchone():
        cur.execute(
            sql.SQL("CREATE DATABASE {} OWNER {} ENCODING 'UTF8'").format(
                sql.Identifier(DB_NAME),
                sql.Identifier(DB_USER),
            )
        )
        print(f"Создана база: {DB_NAME}")

    cur.execute(
        sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
            sql.Identifier(DB_NAME),
            sql.Identifier(DB_USER),
        )
    )

    cur.close()
    conn.close()

    write_env()
    print(f"Готово. DATABASE_URL записан в {ENV_PATH}")
    print(database_url())


if __name__ == "__main__":
    main()
