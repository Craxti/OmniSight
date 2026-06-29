"""Unit tests for v1 API response envelopes."""

from src.api.handlers.v1_envelopes import (
    CORRELATION_SCHEMA_V1,
    apply_v1_envelope,
    audit_items_v1_envelope,
    audit_list_v1_envelope,
    auth_items_v1_envelope,
    auth_result_v1_envelope,
    autodiscover_items_v1_envelope,
    business_path_v1_envelope,
    ci_detail_v1_envelope,
    ci_list_v1_envelope,
    ci_mutation_v1_envelope,
    ci_type_list_v1_envelope,
    ci_type_mutation_v1_envelope,
    components_v1_envelope,
    connector_sync_v1_envelope,
    connector_test_v1_envelope,
    connector_v1_envelope,
    correlation_context_v1_envelope,
    correlation_ingest_v1_envelope,
    dashboard_v1_envelope,
    delete_result_v1_envelope,
    domain_constants_v1_envelope,
    export_payload_v1_envelope,
    graph_layout_v1_envelope,
    graph_v1_envelope,
    impact_v1_envelope,
    import_report_v1_envelope,
    relation_detail_v1_envelope,
    relation_validation_v1_envelope,
    relations_list_v1_envelope,
    resolve_v1_envelope,
    resource_search_v1_envelope,
    scan_v1_envelope,
    session_v1_envelope,
    user_v1_envelope,
    wrap_v1,
)
from src.schemas.audit import AuditListResponse, RelationValidationResponse
from src.schemas.ci import CIDetailResponse, CIListResponse, CIResponse
from src.schemas.common import ImportReport
from src.schemas.correlation import (
    CorrelationContextPayload,
    CorrelationIngestResponse,
    CorrelationResolvePayload,
)
from src.schemas.relations import RelationResponse
from src.schemas.resources import ComponentsResponse, ImpactResponse, ResourceGraphResponse
from src.schemas.v1.inventory import INVENTORY_SCHEMA_V1
from src.schemas.v1.meta import META_SCHEMA_V1
from src.schemas.v1.ops import OPS_SCHEMA_V1
from src.schemas.v1.topology import TOPOLOGY_SCHEMA_V1


def test_wrap_v1_adds_api_version():
    body = wrap_v1({"items": [1]})
    assert body["api_version"] == "v1"
    assert body["items"] == [1]


def test_correlation_context_v1_envelope():
    ctx = CorrelationContextPayload(resource_ids=[1], chain_related=True)
    body = correlation_context_v1_envelope(ctx)
    assert body["api_version"] == "v1"
    assert body["schema_version"] == CORRELATION_SCHEMA_V1
    assert body["correlation"]["resource_ids"] == [1]


def test_correlation_ingest_v1_envelope():
    result = CorrelationIngestResponse(
        schema_version="rsm-correlation-v1",
        resolve=CorrelationResolvePayload(
            resolved=[],
            unresolved=[],
            schema_version="rsm-correlation-v1",
        ),
    )
    body = correlation_ingest_v1_envelope(result)
    assert body["api_version"] == "v1"
    assert body["schema_version"] == CORRELATION_SCHEMA_V1


def test_resolve_v1_envelope():
    class _Payload:
        def model_dump(self):
            return {"resolved": [], "unresolved": []}

    body = resolve_v1_envelope(_Payload())
    assert body["api_version"] == "v1"
    assert body["resolved"] == []


def test_ci_list_v1_envelope():
    result = CIListResponse(
        items=[CIResponse(id=1, name="srv", type_id=1, status="active")],
        total=10,
        skip=0,
        limit=5,
    )
    body = ci_list_v1_envelope(result, page=1, page_size=5)
    assert body["api_version"] == "v1"
    assert body["schema_version"] == INVENTORY_SCHEMA_V1
    assert body["pagination"]["total_items"] == 10
    assert len(body["items"]) == 1


def test_relations_list_v1_envelope():
    items = [
        RelationResponse(
            id=1,
            source_ci_id=1,
            target_ci_id=2,
            relation_type="depends_on",
            status="active",
            direction="outgoing",
        )
    ]
    body = relations_list_v1_envelope(items, total=3, page=1, page_size=1)
    assert body["schema_version"] == INVENTORY_SCHEMA_V1
    assert body["pagination"]["total_pages"] == 3


def test_ci_detail_v1_envelope():
    detail = CIDetailResponse(id=5, name="db-01", type_id=1, status="active")
    body = ci_detail_v1_envelope(detail)
    assert body["api_version"] == "v1"
    assert body["schema_version"] == INVENTORY_SCHEMA_V1
    assert body["ci"]["name"] == "db-01"


def test_relation_detail_v1_envelope():
    relation = RelationResponse(
        id=3,
        source_ci_id=1,
        target_ci_id=2,
        relation_type="uses",
        status="active",
        direction="outgoing",
    )
    body = relation_detail_v1_envelope(relation)
    assert body["relation"]["id"] == 3


def test_ci_mutation_v1_envelope():
    ci = CIResponse(id=2, name="new-ci", type_id=1, status="active")
    body = ci_mutation_v1_envelope(ci)
    assert body["ci"]["name"] == "new-ci"


def test_delete_result_v1_envelope():
    body = delete_result_v1_envelope({"ok": True})
    assert body["result"]["ok"] is True


def test_relation_validation_v1_envelope():
    validation = RelationValidationResponse(valid=True, issues=[], issue_count=0)
    body = relation_validation_v1_envelope(validation)
    assert body["validation"]["valid"] is True


def test_import_report_v1_envelope():
    report = ImportReport(created=2, updated=1, skipped=0, errors=["warn"])
    body = import_report_v1_envelope(report)
    assert body["api_version"] == "v1"
    assert body["schema_version"] == INVENTORY_SCHEMA_V1
    assert body["report"]["created"] == 2
    assert body["report"]["errors"] == ["warn"]


def test_export_payload_v1_envelope():
    body = export_payload_v1_envelope({"needs_mapping": True, "proposals": []})
    assert body["api_version"] == "v1"
    assert body["export"]["needs_mapping"] is True


def test_ci_type_list_v1_envelope():
    items = [{"id": 1, "name": "Server", "is_official": True}]
    body = ci_type_list_v1_envelope(items)
    assert body["schema_version"] == INVENTORY_SCHEMA_V1
    assert body["items"][0]["name"] == "Server"
    assert body["pagination"]["total_items"] == 1


def test_ci_type_mutation_v1_envelope():
    body = ci_type_mutation_v1_envelope({"id": 2, "name": "Custom"})
    assert body["ci_type"]["name"] == "Custom"


def test_topology_v1_envelopes():
    graph = ResourceGraphResponse(root_id=1, depth=2, nodes=[], edges=[])
    assert graph_v1_envelope(graph)["schema_version"] == TOPOLOGY_SCHEMA_V1
    impact = ImpactResponse(ci_id=1, impacted_business_services=[], count=0)
    assert impact_v1_envelope(impact)["impact"]["ci_id"] == 1
    components = ComponentsResponse(ci_id=1, components=[], count=0)
    assert components_v1_envelope(components)["components"]["count"] == 0
    assert business_path_v1_envelope({"path": []})["business_path"]["path"] == []
    assert graph_layout_v1_envelope({"root_ci_id": 3, "positions": {}})["layout"]["root_ci_id"] == 3


def test_resource_search_and_meta_v1_envelopes():
    body = resource_search_v1_envelope({"items": [], "total": 0, "match_mode": "exact"})
    assert body["search"]["match_mode"] == "exact"
    meta = domain_constants_v1_envelope({"roles": ["admin"]})
    assert meta["schema_version"] == META_SCHEMA_V1
    assert meta["constants"]["roles"] == ["admin"]


def test_ops_v1_envelopes():
    dash = dashboard_v1_envelope({"total_ci": 1, "recent_audit": []})
    assert dash["schema_version"] == OPS_SCHEMA_V1
    assert dash["dashboard"]["total_ci"] == 1
    listed = audit_list_v1_envelope(
        AuditListResponse(items=[], total=0, skip=0, limit=25),
        page=1,
        page_size=25,
    )
    assert listed["pagination"]["total_items"] == 0
    items = audit_items_v1_envelope([])
    assert items["items"] == []


def test_autodiscover_v1_envelopes():
    from src.schemas.v1.autodiscover import AUTODISCOVER_SCHEMA_V1

    listed = autodiscover_items_v1_envelope([{"id": 1}])
    assert listed["schema_version"] == AUTODISCOVER_SCHEMA_V1
    assert listed["items"][0]["id"] == 1
    assert connector_v1_envelope({"id": 2})["connector"]["id"] == 2
    assert scan_v1_envelope({"run_id": 3})["scan"]["run_id"] == 3
    assert apply_v1_envelope({"applied": 1})["apply"]["applied"] == 1
    assert connector_test_v1_envelope({"ok": True})["test"]["ok"] is True
    assert connector_sync_v1_envelope({"run_id": 4})["sync"]["run_id"] == 4


def test_auth_v1_envelopes():
    from src.schemas.v1.auth import AUTH_SCHEMA_V1

    session = session_v1_envelope({"access_token": "t", "token_type": "bearer"})
    assert session["schema_version"] == AUTH_SCHEMA_V1
    assert session["session"]["access_token"] == "t"
    user = user_v1_envelope({"email": "a@b.c", "role": "admin"})
    assert user["user"]["email"] == "a@b.c"
    listed = auth_items_v1_envelope([{"email": "x@y.z"}])
    assert listed["items"][0]["email"] == "x@y.z"
    assert auth_result_v1_envelope()["result"]["ok"] is True
