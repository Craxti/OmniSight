#!/usr/bin/env python3
"""Seed ~50k CIs + chain relations for PostgreSQL NFR benchmark (§9)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.core.schema import ensure_database_schema
from src.core.seed import seed_database
from src.models import CI, CIType
from src.services.rsm.indexed_ids import sync_search_indexes

TARGET = 50_000
BATCH = 500


def _existing_count(db: Session) -> int:
    return db.query(CI).filter(CI.is_deleted.is_(False), CI.name.like("scale-%")).count()


def main() -> int:
    ensure_database_schema()
    db = SessionLocal()
    seed_database(db)

    server_type = db.query(CIType).filter(CIType.name == "Server").first()
    if not server_type:
        print("ERROR: Server CI type missing")
        return 1

    current = _existing_count(db)
    if current >= TARGET:
        print(f"Scale data already present: {current} CIs (target {TARGET})")
        db.close()
        return 0

    print(f"Seeding scale CIs: {current} → {TARGET} …")
    created = 0
    for i in range(current, TARGET):
        name = f"scale-host-{i:05d}"
        hostname = f"scale-{i:05d}.local"
        ip = f"10.{(i // 256) % 256}.{(i % 256)}.{i % 200 + 1}"
        ci = CI(
            name=name,
            type_id=server_type.id,
            status="active",
            environment="production",
            owner="scale-bench",
            criticality="low",
            attributes={"hostname": hostname, "ip": ip},
            external_ids={"hostname": hostname, "ip": ip},
        )
        sync_search_indexes(ci)
        db.add(ci)
        created += 1
        if created % BATCH == 0:
            db.commit()
            print(f"  … {current + created}/{TARGET}")

    db.commit()
    print(f"Created {created} scale CIs")

    # Anchor CI for benchmark resolve/search
    anchor = db.query(CI).filter(CI.name == "scale-bench-anchor").first()
    if not anchor:
        anchor = CI(
            name="scale-bench-anchor",
            type_id=server_type.id,
            status="active",
            environment="production",
            owner="scale-bench",
            attributes={"hostname": "app-01", "ip": "10.0.0.5"},
            external_ids={"hostname": "app-01", "ip": "10.0.0.5"},
        )
        sync_search_indexes(anchor)
        db.add(anchor)
        db.flush()
        db.commit()
        print(f"Anchor CI id={anchor.id} (hostname=app-01)")

    db.close()
    print("OK: scale seed complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
