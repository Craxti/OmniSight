"""Tests for CI entity factory."""

from src.schemas.ci import CICreate
from src.services.ci.factory import build_ci_from_autodiscover, build_ci_from_create


def test_build_ci_from_create_maps_all_fields():
    body = CICreate(
        name="app-1",
        type_id=3,
        description="desc",
        status="active",
        criticality="high",
        environment="test",
        owner="ops",
        team="platform",
        attributes={"region": "eu"},
        external_ids={"hostname": "app-1"},
    )
    ci = build_ci_from_create(body, type_id=3)
    assert ci.name == "app-1"
    assert ci.type_id == 3
    assert ci.description == "desc"
    assert ci.owner == "ops"
    assert ci.attributes == {"region": "eu"}


def test_build_ci_from_autodiscover_defaults():
    ci = build_ci_from_autodiscover(
        name="host-1",
        type_id=5,
        attributes={"hostname": "host-1"},
        external_ids={"hostname": "host-1"},
    )
    assert ci.name == "host-1"
    assert ci.type_id == 5
    assert ci.status == "active"
    assert ci.owner == "autodiscover"
    assert ci.environment == "production"
