#!/usr/bin/env python3
"""Seed ~50k CIs + chain relations for PostgreSQL NFR benchmark (§9)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.database import SessionLocal, engine
from src.core.schema import ensure_database_schema
from tests.helpers.scale_seed import TARGET, ensure_scale_seed


def main() -> int:
    ensure_database_schema()
    try:
        ensure_scale_seed(engine, target=TARGET, verbose=True)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1
    SessionLocal().close()
    print("OK: scale seed complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
