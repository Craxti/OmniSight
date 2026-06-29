"""Helpers for integration tests against the v1 API envelope."""

from __future__ import annotations

from typing import Any

API_V1 = "/api/v1"


def j(response) -> dict[str, Any]:
    return response.json()


def ci(body: dict[str, Any]) -> dict[str, Any]:
    return body["ci"]


def relation(body: dict[str, Any]) -> dict[str, Any]:
    return body["relation"]


def items(body: dict[str, Any]) -> list[dict[str, Any]]:
    return body["items"]


def report(body: dict[str, Any]) -> dict[str, Any]:
    return body["report"]


def export_payload(body: dict[str, Any]) -> dict[str, Any]:
    return body["export"]


def validation(body: dict[str, Any]) -> dict[str, Any]:
    return body["validation"]


def dashboard(body: dict[str, Any]) -> dict[str, Any]:
    return body["dashboard"]


def search(body: dict[str, Any]) -> dict[str, Any]:
    return body["search"]


def audit_items(body: dict[str, Any]) -> list[dict[str, Any]]:
    return body["items"]


def ci_type(body: dict[str, Any]) -> dict[str, Any]:
    return body["ci_type"]
