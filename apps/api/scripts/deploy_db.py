"""Database deploy: Alembic migrations and optional base seed."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.schema import bootstrap_database


def deploy(*, seed: bool = False) -> None:
    print("Ensuring database schema (Alembic)...")
    bootstrap_database(seed=seed)
    print("Done.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create DB schema if missing and optionally seed")
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Apply base seed (admin user, CI types, search index backfill)",
    )
    args = parser.parse_args()
    deploy(seed=args.seed)


if __name__ == "__main__":
    main()
