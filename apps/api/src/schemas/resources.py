from pydantic import BaseModel, Field
from src.schemas.audit import AuditLogResponse
from src.schemas.ci import CIResponse
from src.schemas.correlation import GraphNodeResponse
from src.schemas.relations import RelationResponse


class OkResponse(BaseModel):
    ok: bool = True


class ResourceSearchResponse(BaseModel):
    items: list[CIResponse]
    total: int
    match_mode: str = "exact"


class ResourceGraphResponse(BaseModel):
    root_id: int
    depth: int
    nodes: list[GraphNodeResponse]
    edges: list[RelationResponse]


class ImpactedServiceItem(BaseModel):
    id: int
    name: str
    criticality: str | None = None


class ImpactResponse(BaseModel):
    ci_id: int
    impacted_business_services: list[ImpactedServiceItem]
    count: int


class ComponentsResponse(BaseModel):
    ci_id: int
    components: list[CIResponse]
    count: int


class BusinessPathResponse(BaseModel):
    path: list[CIResponse]


class GraphLayoutPosition(BaseModel):
    x: float
    y: float


class GraphLayoutResponse(BaseModel):
    root_ci_id: int
    relation_filter: str = "*"
    positions: dict[str, GraphLayoutPosition] = Field(default_factory=dict)


class GraphLayoutUpdate(BaseModel):
    relation_filter: str = "*"
    positions: dict[str, GraphLayoutPosition] = Field(default_factory=dict)


class GlobalSearchResponse(BaseModel):
    cis: list[CIResponse]
    query: str


class DashboardModelWarning(BaseModel):
    type: str
    message: str
    count: int


class DashboardModelHealth(BaseModel):
    valid: bool
    issue_count: int
    warning_count: int = 0
    warnings: list[DashboardModelWarning] = Field(default_factory=list)
    external_id_coverage_pct: float = 100.0
    correlation_ready: bool = True


class DashboardOverviewResponse(BaseModel):
    total_ci: int
    total_relations: int
    by_status: dict[str, int]
    by_type: dict[str, int]
    model_health: DashboardModelHealth
    recent_audit: list[AuditLogResponse]
