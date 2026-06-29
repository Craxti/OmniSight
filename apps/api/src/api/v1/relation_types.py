from typing import Annotated

from fastapi import APIRouter, Depends
from src.api.handlers.relation_types import (
    handle_relation_type_create,
    handle_relation_type_delete,
    handle_relation_type_update,
    handle_relation_types_list,
)
from src.core.auth import require_admin, require_viewer
from src.core.deps import get_relation_type_read_port, get_relation_type_write_port
from src.core.openapi_tags import TAG_ADMIN_RELATION_TYPES
from src.models import User
from src.schemas.relation_type import RelationTypeCreate, RelationTypeUpdate
from src.services.async_read.relation_types import AsyncRelationTypeReadService
from src.services.async_write.relation_types import AsyncRelationTypeWriteService

router = APIRouter(prefix="/relation/types", tags=[TAG_ADMIN_RELATION_TYPES])

RelationTypeReadSvc = Annotated[AsyncRelationTypeReadService, Depends(get_relation_type_read_port)]
RelationTypeWriteSvc = Annotated[AsyncRelationTypeWriteService, Depends(get_relation_type_write_port)]


@router.get("")
async def list_relation_types_v1(service: RelationTypeReadSvc, _: Annotated[User, Depends(require_viewer)]):
    return await handle_relation_types_list(service)


@router.post("")
async def create_relation_type_v1(
    body: RelationTypeCreate,
    service: RelationTypeWriteSvc,
    user: Annotated[User, Depends(require_admin)],
):
    return await handle_relation_type_create(service, body, user)


@router.patch("/{type_id}")
async def patch_relation_type_v1(
    type_id: int,
    body: RelationTypeUpdate,
    service: RelationTypeWriteSvc,
    user: Annotated[User, Depends(require_admin)],
):
    return await handle_relation_type_update(service, type_id, body, user)


@router.delete("/{type_id}")
async def remove_relation_type_v1(
    type_id: int,
    service: RelationTypeWriteSvc,
    user: Annotated[User, Depends(require_admin)],
):
    return await handle_relation_type_delete(service, type_id, user)
