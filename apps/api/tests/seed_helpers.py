"""Shared test seed helpers (v1 API)."""

from __future__ import annotations

from fastapi.testclient import TestClient
from src.core.constants import EXTERNAL_ID_FIELDS_SET

from tests.v1_helpers import API_V1, ci, items, relation

_EXTERNAL_KEYS = tuple(k for k in EXTERNAL_ID_FIELDS_SET if k != "cmdbId")


def get_type_map(client: TestClient, headers: dict) -> dict[str, int]:
    body = client.get(f"{API_V1}/ci/types", headers=headers).json()
    return {t["name"]: t["id"] for t in items(body)}


def find_ci_id_by_name(client: TestClient, headers: dict, name: str) -> int | None:
    response = client.get(f"{API_V1}/ci", params={"q": name, "page_size": 100}, headers=headers)
    assert response.status_code == 200, response.text
    for item in items(response.json()):
        if item["name"] == name:
            return item["id"]
    return None


def create_ci(client: TestClient, headers: dict, types: dict[str, int], name: str, type_name: str, **attrs) -> int:
    body = {
        "name": name,
        "type_id": types[type_name],
        "status": "active",
        "criticality": "high",
        "environment": "production",
        "owner": "ops",
        "team": "platform",
        "attributes": attrs,
        "external_ids": {k: v for k, v in attrs.items() if k in _EXTERNAL_KEYS},
    }
    response = client.post(f"{API_V1}/ci", json=body, headers=headers)
    if response.status_code == 409:
        existing_id = find_ci_id_by_name(client, headers, name)
        assert existing_id is not None, response.text
        return existing_id
    assert response.status_code == 200, response.text
    return ci(response.json())["id"]


def get_or_create_ci(
    client: TestClient, headers: dict, types: dict[str, int], name: str, type_name: str, **attrs
) -> int:
    existing_id = find_ci_id_by_name(client, headers, name)
    if existing_id is not None:
        return existing_id
    return create_ci(client, headers, types, name, type_name, **attrs)


def create_relation(
    client: TestClient,
    headers: dict,
    source_id: int,
    target_id: int,
    relation_type: str = "depends_on",
) -> int:
    response = client.post(
        f"{API_V1}/relations",
        json={
            "source_ci_id": source_id,
            "target_ci_id": target_id,
            "relation_type": relation_type,
            "status": "active",
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return relation(response.json())["id"]


def find_relation_id(
    client: TestClient,
    headers: dict,
    source_id: int,
    target_id: int,
    relation_type: str = "depends_on",
) -> int | None:
    response = client.get(f"{API_V1}/relations", params={"page_size": 500}, headers=headers)
    assert response.status_code == 200, response.text
    for item in items(response.json()):
        if (
            item["source_ci_id"] == source_id
            and item["target_ci_id"] == target_id
            and item["relation_type"] == relation_type
        ):
            return item["id"]
    return None


def get_or_create_relation(
    client: TestClient,
    headers: dict,
    source_id: int,
    target_id: int,
    relation_type: str = "depends_on",
) -> int:
    existing_id = find_relation_id(client, headers, source_id, target_id, relation_type)
    if existing_id is not None:
        return existing_id
    return create_relation(client, headers, source_id, target_id, relation_type)
