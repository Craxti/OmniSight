from typing import Annotated

from fastapi import APIRouter, Depends
from src.api.handlers.ci_types import (
    handle_ci_type_create,
    handle_ci_type_delete,
    handle_ci_type_update,
    handle_ci_types_list,
)
from src.core.auth import require_admin, require_viewer
from src.core.deps import get_ci_type_read_port, get_ci_type_write_port
from src.models import User
from src.schemas.ci import CITypeCreate, CITypeUpdate
from src.services.async_read.ci_types import AsyncCiTypeReadService
from src.services.async_write.ci_types import AsyncCiTypeWriteService

from src.core.openapi_tags import TAG_ADMIN_CI_TYPES

router = APIRouter(prefix="/ci/types", tags=[TAG_ADMIN_CI_TYPES])

CiTypeReadSvc = Annotated[AsyncCiTypeReadService, Depends(get_ci_type_read_port)]
CiTypeWriteSvc = Annotated[AsyncCiTypeWriteService, Depends(get_ci_type_write_port)]


@router.get("")
async def list_ci_types_v1(service: CiTypeReadSvc, _: Annotated[User, Depends(require_viewer)]):
    return await handle_ci_types_list(service)


@router.post("")
async def create_ci_type_v1(
    body: CITypeCreate,
    service: CiTypeWriteSvc,
    user: Annotated[User, Depends(require_admin)],
):
    return await handle_ci_type_create(service, body, user)


@router.patch("/{type_id}")
async def patch_ci_type_v1(
    type_id: int,
    body: CITypeUpdate,
    service: CiTypeWriteSvc,
    user: Annotated[User, Depends(require_admin)],
):
    return await handle_ci_type_update(service, type_id, body, user)


@router.delete("/{type_id}")
async def remove_ci_type_v1(
    type_id: int,
    service: CiTypeWriteSvc,
    user: Annotated[User, Depends(require_admin)],
):
    return await handle_ci_type_delete(service, type_id, user)
