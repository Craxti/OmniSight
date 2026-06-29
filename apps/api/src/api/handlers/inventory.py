"""CI and relations HTTP handlers (v1 envelopes)."""

from __future__ import annotations

from typing import Any

from src.api.handlers.v1_envelopes import (
    ci_detail_v1_envelope,
    ci_items_v1_envelope,
    ci_list_v1_envelope,
    ci_mutation_v1_envelope,
    delete_result_v1_envelope,
    relation_detail_v1_envelope,
    relation_items_v1_envelope,
    relation_mutation_v1_envelope,
    relation_validation_v1_envelope,
    relations_list_v1_envelope,
)
from src.models import User
from src.schemas.ci import BulkStatusUpdate, CICreate, CIUpdate
from src.schemas.relations import RelationCreate, RelationUpdate
from src.services.async_read.ci import AsyncCiReadService
from src.services.async_read.relations import AsyncRelationReadService
from src.services.async_read.topology import AsyncTopologyService
from src.services.async_write.ci import AsyncCiWriteService
from src.services.async_write.relations import AsyncRelationWriteService


async def handle_ci_list(
    service: AsyncCiReadService,
    *,
    page: int = 1,
    page_size: int = 50,
    **filters: Any,
):
    skip = (page - 1) * page_size
    result = await service.list_ci(skip=skip, limit=page_size, **filters)
    return ci_list_v1_envelope(result, page=page, page_size=page_size)


async def handle_ci_detail(service: AsyncCiReadService, ci_id: int):
    detail = await service.get_ci_detail(ci_id)
    return ci_detail_v1_envelope(detail)


async def handle_relations_list(
    service: AsyncRelationReadService,
    *,
    page: int = 1,
    page_size: int = 100,
    **filters: Any,
):
    skip = (page - 1) * page_size
    items, total = await service.list_relations_page(skip=skip, limit=page_size, **filters)
    return relations_list_v1_envelope(items, total=total, page=page, page_size=page_size)


async def handle_ci_relations(topology: AsyncTopologyService, ci_id: int):
    relations = await topology.direct_relations(ci_id)
    return relation_items_v1_envelope(relations)


async def handle_relation_detail(service: AsyncRelationReadService, relation_id: int):
    relation = await service.get_relation(relation_id)
    return relation_detail_v1_envelope(relation)


async def handle_ci_create(service: AsyncCiWriteService, body: CICreate, user: User):
    ci = await service.create_ci(body, user)
    return ci_mutation_v1_envelope(ci)


async def handle_ci_update(service: AsyncCiWriteService, ci_id: int, body: CIUpdate, user: User):
    ci = await service.update_ci(ci_id, body, user)
    return ci_mutation_v1_envelope(ci)


async def handle_ci_delete(service: AsyncCiWriteService, ci_id: int, user: User):
    result = await service.delete_ci(ci_id, user)
    return delete_result_v1_envelope(result)


async def handle_relation_create(service: AsyncRelationWriteService, body: RelationCreate, user: User):
    relation = await service.create_relation(body, user)
    return relation_mutation_v1_envelope(relation)


async def handle_relation_update(
    service: AsyncRelationWriteService,
    relation_id: int,
    body: RelationUpdate,
    user: User,
):
    relation = await service.update_relation(relation_id, body, user)
    return relation_mutation_v1_envelope(relation)


async def handle_relation_delete(service: AsyncRelationWriteService, relation_id: int, user: User):
    result = await service.delete_relation(relation_id, user)
    return delete_result_v1_envelope(result)


async def handle_relations_validate(service: AsyncRelationReadService):
    validation = await service.validate_model()
    return relation_validation_v1_envelope(validation)


async def handle_ci_recycle_bin(service: AsyncCiReadService):
    items = await service.list_recycle_bin()
    return ci_items_v1_envelope(items)


async def handle_ci_restore(service: AsyncCiWriteService, ci_id: int, user: User):
    ci = await service.restore_ci(ci_id, user)
    return ci_mutation_v1_envelope(ci)


async def handle_ci_purge(service: AsyncCiWriteService, ci_id: int, user: User):
    result = await service.purge_ci(ci_id, user)
    return delete_result_v1_envelope(result)


async def handle_ci_bulk_status(service: AsyncCiWriteService, body: BulkStatusUpdate, user: User):
    result = await service.bulk_status(body, user)
    return delete_result_v1_envelope(result)
