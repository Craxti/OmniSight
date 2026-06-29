"""Name-based app-to-database matching fallback."""

from __future__ import annotations

import re

from src.services.autodiscover.discovery.constants import APP_SUFFIXES, DB_SUFFIXES
from src.services.autodiscover.discovery.inference.core import make_connection


def app_stem(name: str) -> str:
    lowered = name.lower()
    for suffix in APP_SUFFIXES:
        if lowered.endswith(suffix):
            return lowered[: -len(suffix)].rstrip("-_")
    return re.sub(r"-?(api|service|app|worker|web)$", "", lowered).rstrip("-_")


def db_stem(name: str) -> str:
    lowered = name.lower()
    for suffix in DB_SUFFIXES:
        if lowered.endswith(suffix):
            return lowered[: -len(suffix)].rstrip("-_")
    return lowered.rstrip("-_")


def score_app_db_match(app_name: str, db_name: str) -> int:
    app_core = app_stem(app_name)
    db_core = db_stem(db_name)
    if not app_core or not db_core:
        return 0
    if app_core == db_core:
        return 100
    if db_name.lower() == f"{app_core}-db":
        return 98
    left_tokens = [t for t in re.split(r"[-_]", app_core) if t]
    right_tokens = [t for t in re.split(r"[-_]", db_core) if t]
    common = 0
    for left, right in zip(left_tokens, right_tokens, strict=False):
        if left != right:
            break
        common += 1
    if common >= 2:
        return 70 + common * 10
    return 0


def best_name_db_matches(app_name: str, dbs: list[str], *, min_score: int = 90) -> list[str]:
    scored = [(score_app_db_match(app_name, db), db) for db in dbs]
    scored = [(score, db) for score, db in scored if score >= min_score]
    if not scored:
        return []
    best = max(score for score, _ in scored)
    return [db for score, db in scored if score == best]


def infer_name_fallback_connections(
    processes: list[dict],
    *,
    apps_with_evidence: set[str],
    existing: set[tuple[str, str, str]],
) -> list[dict]:
    dbs = [str(p["hostname"]) for p in processes if p.get("entity_type") == "Database" and p.get("hostname")]
    connections: list[dict] = []
    for proc in processes:
        if proc.get("entity_type") not in ("Application", "Container"):
            continue
        app_name = str(proc["hostname"])
        if app_name in apps_with_evidence:
            continue
        for db in best_name_db_matches(app_name, dbs):
            key = (app_name, db, "depends_on")
            if key not in existing:
                connections.append(
                    make_connection(
                        source_hostname=app_name,
                        target_hostname=db,
                        relation_type="depends_on",
                        source="name",
                    )
                )
    return connections
