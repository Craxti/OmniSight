from typing import Annotated

from fastapi import APIRouter, Depends
from src.api.handlers.meta import handle_domain_constants
from src.core.auth import require_viewer
from src.core.deps import get_relation_type_read_port
from src.models import User
from src.services.async_read.relation_types import AsyncRelationTypeReadService

from src.core.openapi_tags import TAG_INTEGRATION_META

router = APIRouter(prefix="/meta", tags=[TAG_INTEGRATION_META])

RelationTypeReadSvc = Annotated[AsyncRelationTypeReadService, Depends(get_relation_type_read_port)]


@router.get("/constants")
async def get_domain_constants_v1(
    service: RelationTypeReadSvc,
    _: Annotated[User, Depends(require_viewer)],
):
    return await handle_domain_constants(service)
