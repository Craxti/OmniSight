"""CI entity construction — single place for field mapping."""

from __future__ import annotations

from typing import Any

from src.models import CI
from src.schemas.ci import CICreate


def build_ci_from_create(body: CICreate, type_id: int) -> CI:
    return CI(
        name=body.name,
        type_id=type_id,
        description=body.description,
        status=body.status,
        criticality=body.criticality,
        environment=body.environment,
        owner=body.owner,
        team=body.team,
        attributes=body.attributes,
        external_ids=body.external_ids,
    )


def build_ci_from_autodiscover(
    *,
    name: str,
    type_id: int,
    attributes: dict[str, Any] | None = None,
    external_ids: dict[str, str] | None = None,
) -> CI:
    return CI(
        name=name,
        type_id=type_id,
        status="active",
        criticality="medium",
        environment="production",
        owner="autodiscover",
        attributes=attributes,
        external_ids=external_ids,
    )
