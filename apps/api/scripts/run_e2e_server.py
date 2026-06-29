#!/usr/bin/env python3
"""Start API for Playwright e2e with PostgreSQL and demo seed."""

import os
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
os.chdir(root)
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:7002@localhost:5432/omnisight",
)
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")
port = int(os.environ.get("E2E_API_PORT", "8001"))

sys.path.insert(0, str(root))
from src.core.schema import ensure_application_database_exists, ensure_database_schema, schema_has_tables

ensure_application_database_exists()
if not schema_has_tables():
    ensure_database_schema()

env = {**os.environ, "SKIP_DB_INIT": "1", "SKIP_MIGRATIONS": "1"}
subprocess.run([sys.executable, "scripts/seed_demo.py"], check=True, env=env)
subprocess.run(
    [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", str(port)],
    check=True,
)
