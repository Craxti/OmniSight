"""Shared helpers for RSM integration tests."""

from fastapi.testclient import TestClient

from tests.seed_helpers import get_or_create_ci, get_or_create_relation, get_type_map


def seed_chain(client: TestClient, headers: dict):
    types = get_type_map(client, headers)
    db_id = get_or_create_ci(
        client,
        headers,
        types,
        "demo-db",
        "Database",
        hostname="demo-db",
        ip="10.0.0.5",
        externalId="ext-db-1",
        engine="PostgreSQL",
    )
    app_id = get_or_create_ci(
        client,
        headers,
        types,
        "demo-app",
        "Application",
        hostname="app-01",
        serviceCode="PAY",
        applicationCode="PAY-APP",
    )
    biz_id = get_or_create_ci(client, headers, types, "demo-biz", "Business Service", serviceCode="PAY-SVC")

    get_or_create_relation(client, headers, app_id, db_id)
    get_or_create_relation(client, headers, biz_id, app_id)

    return db_id, app_id, biz_id
