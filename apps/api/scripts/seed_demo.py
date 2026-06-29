#!/usr/bin/env python3
"""Seed demo data for RSM correlation scenario (§3.2)."""

import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.database import SessionLocal
from src.core.fixture_paths import fixture_path
from src.core.seed import seed_database
from src.models import CI, CIType, Relation, SyncConnector
from src.services.rsm.indexed_ids import sync_search_indexes

_EXTERNAL_ID_KEYS = ("hostname", "ip", "externalId", "serviceCode", "applicationCode")


def _upsert_ci(db, types: dict[str, int], item: dict) -> int:
    name = item["name"]
    type_name = item["type_name"]
    attrs = {**(item.get("attributes") or {}), **(item.get("external_ids") or {})}
    external_ids = {k: v for k, v in attrs.items() if k in _EXTERNAL_ID_KEYS}
    existing = db.query(CI).filter(CI.name == name, CI.is_deleted.is_(False)).first()
    if existing:
        existing.type_id = types[type_name]
        existing.status = item.get("status", existing.status)
        existing.criticality = item.get("criticality", existing.criticality)
        existing.environment = item.get("environment", existing.environment)
        existing.owner = item.get("owner", existing.owner)
        existing.team = item.get("team", existing.team)
        existing.attributes = attrs
        existing.external_ids = external_ids
        sync_search_indexes(existing)
        db.flush()
        return existing.id
    ci = CI(
        name=name,
        type_id=types[type_name],
        status=item.get("status", "active"),
        criticality=item.get("criticality"),
        environment=item.get("environment"),
        owner=item.get("owner"),
        team=item.get("team"),
        attributes=attrs,
        external_ids={k: v for k, v in attrs.items() if k in _EXTERNAL_ID_KEYS},
    )
    sync_search_indexes(ci)
    db.add(ci)
    db.flush()
    return ci.id


def _upsert_relation(db, *, source_id: int, target_id: int, relation_type: str, data_source: str = "demo-seed") -> None:
    exists = (
        db.query(Relation)
        .filter(
            Relation.source_ci_id == source_id,
            Relation.target_ci_id == target_id,
            Relation.relation_type == relation_type,
            Relation.is_deleted.is_(False),
        )
        .first()
    )
    if not exists:
        db.add(
            Relation(
                source_ci_id=source_id,
                target_ci_id=target_id,
                relation_type=relation_type,
                status="active",
                data_source=data_source,
            )
        )


def _seed_from_fixture(db, types: dict[str, int], elements_path: Path, relations_path: Path) -> dict[str, int]:
    if not elements_path.is_file() or not relations_path.is_file():
        return {}

    with elements_path.open(encoding="utf-8") as fh:
        elements = json.load(fh).get("elements", [])
    with relations_path.open(encoding="utf-8") as fh:
        relations = json.load(fh).get("relations", [])

    ids: dict[str, int] = {}
    for item in elements:
        ids[item["name"]] = _upsert_ci(db, types, item)

    for rel in relations:
        source_id = ids.get(rel["source_name"])
        target_id = ids.get(rel["target_name"])
        if not source_id or not target_id:
            src = db.query(CI).filter(CI.name == rel["source_name"], CI.is_deleted.is_(False)).first()
            tgt = db.query(CI).filter(CI.name == rel["target_name"], CI.is_deleted.is_(False)).first()
            source_id = src.id if src else None
            target_id = tgt.id if tgt else None
        if source_id and target_id:
            _upsert_relation(db, source_id=source_id, target_id=target_id, relation_type=rel["relation_type"])

    return ids


def _link_server_host_connector(db, *, server_ci_id: int, hostname: str, snapshot_path: Path) -> None:
    name = f"host-{hostname}"
    existing = db.query(SyncConnector).filter(SyncConnector.name == name).first()
    if existing:
        existing.server_ci_id = server_ci_id
        existing.config = {"mode": "snapshot", "snapshot_path": str(snapshot_path)}
        existing.enabled = True
        return
    db.add(
        SyncConnector(
            name=name,
            connector_type="host",
            server_ci_id=server_ci_id,
            config={"mode": "snapshot", "snapshot_path": str(snapshot_path)},
            enabled=True,
        )
    )


async def _ensure_default_sync_assets() -> None:
    from src.core.database_async import async_write_session
    from src.services.autodiscover.runtime.seed import ensure_default_sync_assets_async

    async with async_write_session() as session:
        await ensure_default_sync_assets_async(session)
        await session.commit()


def main():
    if os.environ.get("SKIP_DB_INIT") != "1" and os.environ.get("SKIP_MIGRATIONS") != "1":
        from src.core.schema import ensure_database_schema

        ensure_database_schema()
    db = SessionLocal()
    seed_database(db)

    types = {t.name: t.id for t in db.query(CIType).all()}
    ids = _seed_from_fixture(
        db,
        types,
        fixture_path("demo_pay_elements.import.json"),
        fixture_path("demo_pay_relations.import.json"),
    )

    db.commit()
    asyncio.run(_ensure_default_sync_assets())
    from src.core.cache import cache_invalidate_prefix

    cache_invalidate_prefix("resolve:")

    inventory = fixture_path("host_snapshot_pay_srv.json")
    pay_srv = db.query(CI).filter(CI.name == "demo-pay-srv", CI.is_deleted.is_(False)).first()
    if pay_srv and inventory.is_file():
        hostname = (pay_srv.external_ids or {}).get("hostname") or (pay_srv.attributes or {}).get("hostname")
        if hostname:
            _link_server_host_connector(
                db,
                server_ci_id=pay_srv.id,
                hostname=str(hostname),
                snapshot_path=inventory,
            )
    db.commit()
    print("Demo data seeded:", ids)
    db.close()


if __name__ == "__main__":
    main()
