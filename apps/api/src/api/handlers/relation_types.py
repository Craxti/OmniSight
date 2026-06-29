"""Relation type catalog HTTP handlers (v1 envelopes)."""

from __future__ import annotations

from src.api.handlers.v1_envelopes import (
    delete_result_v1_envelope,
    relation_type_list_v1_envelope,
    relation_type_mutation_v1_envelope,
)
from src.models import User
from src.schemas.relation_type import RelationTypeCreate, RelationTypeUpdate
from src.services.async_read.relation_types import AsyncRelationTypeReadService
from src.services.async_write.relation_types import AsyncRelationTypeWriteService


async def handle_relation_types_list(service: AsyncRelationTypeReadService):
    items = await service.list_types()
    return relation_type_list_v1_envelope(items)


async def handle_relation_type_create(service: AsyncRelationTypeWriteService, body: RelationTypeCreate, user: User):
    result = await service.create_type(body, user)
    return relation_type_mutation_v1_envelope(result)


async def handle_relation_type_update(
    service: AsyncRelationTypeWriteService,
    type_id: int,
    body: RelationTypeUpdate,
    user: User,
):
    result = await service.update_type(type_id, body, user)
    return relation_type_mutation_v1_envelope(result)


async def handle_relation_type_delete(service: AsyncRelationTypeWriteService, type_id: int, user: User):
    result = await service.delete_type(type_id, user)
    return delete_result_v1_envelope(result)
