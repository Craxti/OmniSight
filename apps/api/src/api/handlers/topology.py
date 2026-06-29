"""Resource topology HTTP handlers (v1 envelopes)."""

from __future__ import annotations

from fastapi import Response, status
from src.api.handlers.v1_envelopes import (
    business_path_v1_envelope,
    components_v1_envelope,
    graph_layout_v1_envelope,
    graph_v1_envelope,
    impact_v1_envelope,
)
from src.models import User
from src.schemas.resources import GraphLayoutUpdate
from src.services.async_read.graph_layout import AsyncGraphLayoutReadService
from src.services.async_read.topology import AsyncTopologyService
from src.services.async_write.graph_layout import AsyncGraphLayoutWriteService
from src.services.domain.graph_layout import layout_response


async def handle_resource_graph(service: AsyncTopologyService, resource_id: int, *, depth: int = 2):
    result = await service.graph(resource_id, depth=depth)
    return graph_v1_envelope(result)


async def handle_resource_impact(service: AsyncTopologyService, resource_id: int):
    result = await service.impact(resource_id)
    return impact_v1_envelope(result)


async def handle_resource_components(service: AsyncTopologyService, resource_id: int):
    result = await service.components(resource_id)
    return components_v1_envelope(result)


async def handle_business_path(service: AsyncTopologyService, resource_id: int):
    result = await service.business_path(resource_id)
    return business_path_v1_envelope(result)


async def handle_get_graph_layout(
    service: AsyncGraphLayoutReadService,
    resource_id: int,
    relation_filter: str,
):
    positions = await service.get_layout(resource_id, relation_filter)
    layout = layout_response(resource_id, relation_filter, positions)
    return graph_layout_v1_envelope(layout)


async def handle_save_graph_layout(
    service: AsyncGraphLayoutWriteService,
    resource_id: int,
    body: GraphLayoutUpdate,
    user: User,
):
    positions = {node_id: pos.model_dump() for node_id, pos in body.positions.items()}
    merged = await service.merge_layout(
        resource_id,
        body.relation_filter,
        positions,
        user.email,
    )
    layout = layout_response(resource_id, body.relation_filter, merged)
    return graph_layout_v1_envelope(layout)


async def handle_clear_graph_layout(service: AsyncGraphLayoutWriteService, resource_id: int, relation_filter: str):
    await service.clear_layout(resource_id, relation_filter)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
