from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from src.schemas.ci import CIResponse
from src.schemas.relations import RelationResponse


class AlertIdentifier(BaseModel):
    hostname: str | None = None
    ip: str | None = None
    serviceCode: str | None = None
    applicationCode: str | None = None
    externalId: str | None = None
    cmdbId: str | None = None


class ResolveRequest(BaseModel):
    alerts: list[AlertIdentifier]


class CorrelationContextRequest(BaseModel):
    resource_ids: list[int]
    depth: int = 3


class ChainCheckRequest(BaseModel):
    """FR 39: проверка принадлежности объектов одной depends_on-цепочке."""

    resource_ids: list[int]


class ChainCheckResponse(BaseModel):
    resource_ids: list[int]
    chain_related: bool
    chain_algorithm: str = "depends_on_directed"


class CorrelationIngestRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "alerts": [
                        {"hostname": "app-01"},
                        {"ip": "10.0.0.5"},
                        {"externalId": "ext-db-1"},
                        {"serviceCode": "PAY", "applicationCode": "PAY-APP"},
                    ],
                    "source": "monitoring-system",
                    "depth": 3,
                }
            ]
        }
    )
    alerts: list[AlertIdentifier]
    source: str | None = None
    depth: int = 3


class CorrelationMatchResult(BaseModel):
    alert: dict[str, Any]
    resolved: bool
    ambiguous: bool = False
    resource: CIResponse | None = None
    match_count: int | None = None


class CorrelationResolvePayload(BaseModel):
    resolved: list[CorrelationMatchResult]
    unresolved: list[CorrelationMatchResult]
    schema_version: str
    pagination: dict[str, int] | None = None


class GraphNodeResponse(CIResponse):
    depth: int = 0


class GraphDataResponse(BaseModel):
    nodes: list[GraphNodeResponse] = Field(default_factory=list)
    edges: list[RelationResponse] = Field(default_factory=list)


class CorrelationEnrichmentItem(BaseModel):
    resource_id: int
    name: str
    type: str | None = None
    criticality: str | None = None
    environment: str | None = None
    owner: str | None = None
    team: str | None = None
    external_ids: dict[str, Any] = Field(default_factory=dict)
    impacted_services: list[dict[str, Any]] = Field(default_factory=list)


class CorrelationContextPayload(BaseModel):
    resource_ids: list[int] = Field(default_factory=list)
    chain_related: bool = False
    chain_algorithm: str = "depends_on_directed"
    graph: GraphDataResponse = Field(default_factory=GraphDataResponse)
    direct_relations: list[RelationResponse] = Field(default_factory=list)
    potential_root_cause_zone: list[CIResponse] = Field(default_factory=list)
    enrichment: list[CorrelationEnrichmentItem] = Field(default_factory=list)


class CorrelationContextResponse(BaseModel):
    schema_version: str
    correlation: CorrelationContextPayload


class CorrelationIngestResponse(BaseModel):
    source: str | None = None
    schema_version: str
    resolve: CorrelationResolvePayload
    correlation: CorrelationContextPayload = Field(default_factory=CorrelationContextPayload)
    enrichment: list[CorrelationEnrichmentItem] = Field(default_factory=list)
    potential_root_cause_zone: list[CIResponse] = Field(default_factory=list)
    webhook: dict[str, Any] | None = None
    ingest_log_id: int | None = None


class CorrelationIngestLogSummary(BaseModel):
    id: int
    source: str | None = None
    alert_count: int
    resolved_count: int
    unresolved_count: int
    chain_related: bool
    created_at: str | None = None


class CorrelationIngestLogDetail(CorrelationIngestLogSummary):
    alerts: list[dict[str, Any]] = Field(default_factory=list)
    result: dict[str, Any] = Field(default_factory=dict)


class CorrelationIngestLogListResponse(BaseModel):
    items: list[CorrelationIngestLogSummary]
    total: int
    skip: int
    limit: int
