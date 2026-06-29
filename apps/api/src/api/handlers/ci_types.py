"""CI type HTTP handlers (v1 envelopes)."""

from __future__ import annotations

from src.api.handlers.v1_envelopes import (
    ci_type_list_v1_envelope,
    ci_type_mutation_v1_envelope,
    delete_result_v1_envelope,
)
from src.models import User
from src.schemas.ci import CITypeCreate, CITypeUpdate
from src.services.async_read.ci_types import AsyncCiTypeReadService
from src.services.async_write.ci_types import AsyncCiTypeWriteService


async def handle_ci_types_list(service: AsyncCiTypeReadService):
    items = await service.list_types()
    return ci_type_list_v1_envelope(items)


async def handle_ci_type_create(service: AsyncCiTypeWriteService, body: CITypeCreate, user: User):
    result = await service.create_type(body, user)
    return ci_type_mutation_v1_envelope(result)


async def handle_ci_type_update(service: AsyncCiTypeWriteService, type_id: int, body: CITypeUpdate, user: User):
    result = await service.update_type(type_id, body, user)
    return ci_type_mutation_v1_envelope(result)


async def handle_ci_type_delete(service: AsyncCiTypeWriteService, type_id: int, user: User):
    result = await service.delete_type(type_id, user)
    return delete_result_v1_envelope(result)
