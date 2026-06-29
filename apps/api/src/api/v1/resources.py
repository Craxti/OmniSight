from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from src.api.handlers.inventory import handle_ci_detail, handle_ci_relations
from src.api.handlers.resources import handle_resolve_batch
from src.api.handlers.search import handle_resource_search
from src.api.handlers.topology import (
    handle_business_path,
    handle_clear_graph_layout,
    handle_get_graph_layout,
    handle_resource_components,
    handle_resource_graph,
    handle_resource_impact,
    handle_save_graph_layout,
)
from src.core.auth import get_current_user, require_editor, require_viewer
from src.core.deps import (
    get_ci_read_port,
    get_correlation_read_port,
    get_graph_layout_read_port,
    get_graph_layout_write_port,
    get_search_read_port,
    get_topology_read_port,
)
from src.models import User
from src.schemas.resources import GraphLayoutUpdate
from src.schemas.v1.correlation import ResolveRequestV1
from src.services.async_read.ci import AsyncCiReadService
from src.services.async_read.correlation import AsyncCorrelationReadService
from src.services.async_read.graph_layout import AsyncGraphLayoutReadService
from src.services.async_read.search import AsyncSearchService
from src.services.async_read.topology import AsyncTopologyService
from src.services.async_write.graph_layout import AsyncGraphLayoutWriteService

from src.core.openapi_tags import TAG_INTEGRATION_RESOURCES

router = APIRouter(prefix="/resources", tags=[TAG_INTEGRATION_RESOURCES])

CiReadSvc = Annotated[AsyncCiReadService, Depends(get_ci_read_port)]
CorrelationReadSvc = Annotated[AsyncCorrelationReadService, Depends(get_correlation_read_port)]
TopologyReadSvc = Annotated[AsyncTopologyService, Depends(get_topology_read_port)]
GraphLayoutReadSvc = Annotated[AsyncGraphLayoutReadService, Depends(get_graph_layout_read_port)]
WriteGraphLayoutSvc = Annotated[AsyncGraphLayoutWriteService, Depends(get_graph_layout_write_port)]
SearchSvc = Annotated[AsyncSearchService, Depends(get_search_read_port)]


def _relation_filter_param(relation_filter: str = Query(default="", alias="relation_filter")) -> str:
    return relation_filter


@router.post("/resolve")
async def resolve_v1(
    body: ResolveRequestV1,
    service: CorrelationReadSvc,
    _: Annotated[User, Depends(get_current_user)],
):
    alerts = [a.model_dump(exclude_none=True) for a in body.alerts]
    return await handle_resolve_batch(
        service,
        alerts,
        page=body.page,
        page_size=body.page_size,
    )


@router.get("/search")
async def search_resources_v1(
    service: SearchSvc,
    _: Annotated[User, Depends(require_viewer)],
    hostname: str | None = None,
    ip: str | None = None,
    externalId: str | None = None,
    serviceCode: str | None = None,
    applicationCode: str | None = None,
    cmdbId: str | None = None,
    type_name: str | None = None,
    owner: str | None = None,
    q: str | None = None,
):
    return await handle_resource_search(
        service,
        q=q,
        hostname=hostname,
        ip=ip,
        external_id=externalId,
        service_code=serviceCode,
        application_code=applicationCode,
        cmdb_id=cmdbId,
        type_name=type_name,
        owner=owner,
        limit=100,
    )


@router.get("/{resource_id}/relations")
async def resource_relations_v1(
    resource_id: int,
    topology: TopologyReadSvc,
    _: Annotated[User, Depends(require_viewer)],
):
    """§8: прямые связи объекта РСМ."""
    return await handle_ci_relations(topology, resource_id)


@router.get("/{resource_id}")
async def resource_detail_v1(
    resource_id: int,
    service: CiReadSvc,
    _: Annotated[User, Depends(require_viewer)],
):
    """§8: карточка объекта РСМ."""
    return await handle_ci_detail(service, resource_id)


@router.get("/{resource_id}/graph")
async def resource_graph_v1(
    resource_id: int,
    service: TopologyReadSvc,
    _: Annotated[User, Depends(require_viewer)],
    depth: int = Query(default=2, ge=1, le=10),
):
    return await handle_resource_graph(service, resource_id, depth=depth)


@router.get("/{resource_id}/impact")
async def resource_impact_v1(
    resource_id: int,
    service: TopologyReadSvc,
    _: Annotated[User, Depends(require_viewer)],
):
    return await handle_resource_impact(service, resource_id)


@router.get("/{resource_id}/components")
async def resource_components_v1(
    resource_id: int,
    service: TopologyReadSvc,
    _: Annotated[User, Depends(require_viewer)],
):
    return await handle_resource_components(service, resource_id)


@router.get("/{resource_id}/business-path")
async def business_path_v1(
    resource_id: int,
    service: TopologyReadSvc,
    _: Annotated[User, Depends(require_viewer)],
):
    return await handle_business_path(service, resource_id)


@router.get("/{resource_id}/graph-layout")
async def get_graph_layout_v1(
    resource_id: int,
    service: GraphLayoutReadSvc,
    _: Annotated[User, Depends(require_viewer)],
    relation_filter: Annotated[str, Depends(_relation_filter_param)],
):
    return await handle_get_graph_layout(service, resource_id, relation_filter)


@router.put("/{resource_id}/graph-layout")
async def save_graph_layout_v1(
    resource_id: int,
    body: GraphLayoutUpdate,
    service: WriteGraphLayoutSvc,
    user: Annotated[User, Depends(require_editor)],
):
    return await handle_save_graph_layout(service, resource_id, body, user)


@router.delete("/{resource_id}/graph-layout", status_code=status.HTTP_204_NO_CONTENT)
async def clear_graph_layout_v1(
    resource_id: int,
    service: WriteGraphLayoutSvc,
    _: Annotated[User, Depends(require_editor)],
    relation_filter: Annotated[str, Depends(_relation_filter_param)],
):
    return await handle_clear_graph_layout(service, resource_id, relation_filter)
