"""Seed ~50k CIs for PostgreSQL NFR scale tests (§9)."""

from __future__ import annotations

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from src.core.seed import seed_database
from src.models import CI, CIType
from src.services.rsm.indexed_ids import sync_search_indexes

TARGET = 50_000
BATCH = 500


def _existing_count(db: Session) -> int:
    return db.query(CI).filter(CI.is_deleted.is_(False), CI.name.like("scale-%")).count()


def ensure_scale_seed(engine: Engine, *, target: int = TARGET, verbose: bool = False) -> int:
    """Ensure scale benchmark CIs exist on the given engine. Returns total scale CI count."""
    session = sessionmaker(bind=engine)()
    try:
        seed_database(session)
        session.commit()

        server_type = session.query(CIType).filter(CIType.name == "Server").first()
        if not server_type:
            raise RuntimeError("Server CI type missing")

        current = _existing_count(session)
        if current >= target:
            if verbose:
                print(f"Scale data already present: {current} CIs (target {target})")
            return current

        if verbose:
            print(f"Seeding scale CIs: {current} → {target} …")
        created = 0
        for i in range(current, target):
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
            session.add(ci)
            created += 1
            if created % BATCH == 0:
                session.commit()
                if verbose:
                    print(f"  … {current + created}/{target}")

        session.commit()
        if verbose:
            print(f"Created {created} scale CIs")

        anchor = session.query(CI).filter(CI.name == "scale-bench-anchor").first()
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
            session.add(anchor)
            session.flush()
            session.commit()
            if verbose:
                print(f"Anchor CI id={anchor.id} (hostname=app-01)")

        return _existing_count(session)
    finally:
        session.close()
