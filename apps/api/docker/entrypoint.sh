#!/bin/sh
set -e

echo "Waiting for database..."
python - <<'PY'
import sys
import time

from sqlalchemy import create_engine, text

from src.core.config import settings

deadline = time.time() + 60
last_error = None
while time.time() < deadline:
    try:
        with create_engine(settings.database_url, pool_pre_ping=True).connect() as conn:
            conn.execute(text("SELECT 1"))
        sys.exit(0)
    except Exception as exc:
        last_error = exc
        time.sleep(2)
print(f"Database not ready: {last_error}", file=sys.stderr)
sys.exit(1)
PY

if [ "${ENSURE_SCHEMA_ON_START:-${RUN_MIGRATIONS_ON_START:-true}}" = "true" ]; then
  echo "Ensuring database schema..."
  python scripts/deploy_db.py ${SEED_ON_START:+--seed}
else
  echo "Skipping schema init (ENSURE_SCHEMA_ON_START=false)"
fi

WORKERS="${UVICORN_WORKERS:-1}"
echo "Starting API (workers=${WORKERS})..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers "${WORKERS}" --proxy-headers --forwarded-allow-ips='*'
