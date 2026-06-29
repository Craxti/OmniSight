from typing import Annotated

from fastapi import APIRouter, Depends, Query
from src.api.handlers.audit import handle_audit_list, handle_entity_audit
from src.core.auth import require_viewer
from src.core.deps import get_audit_read_port
from src.models import User
from src.services.async_read.audit import AsyncAuditReadService

from src.core.openapi_tags import TAG_ADMIN_AUDIT

router = APIRouter(prefix="/audit", tags=[TAG_ADMIN_AUDIT])

AuditSvc = Annotated[AsyncAuditReadService, Depends(get_audit_read_port)]


@router.get("")
async def list_audit_v1(
    service: AuditSvc,
    _: Annotated[User, Depends(require_viewer)],
    entity_type: str | None = None,
    action: str | None = None,
    user_email: str | None = Query(default=None),
    date_from: str | None = Query(default=None, description="ISO date YYYY-MM-DD"),
    date_to: str | None = Query(default=None, description="ISO date YYYY-MM-DD"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
):
    return await handle_audit_list(
        service,
        page=page,
        page_size=page_size,
        entity_type=entity_type,
        action=action,
        user_email=user_email,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/{entity_type}/{entity_id}")
async def entity_audit_v1(
    entity_type: str,
    entity_id: int,
    service: AuditSvc,
    _: Annotated[User, Depends(require_viewer)],
):
    return await handle_entity_audit(service, entity_type, entity_id)
