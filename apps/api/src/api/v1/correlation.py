from typing import Annotated

from fastapi import APIRouter, Depends
from src.api.handlers.correlation import handle_correlation_context, handle_correlation_ingest
from src.core.auth import get_current_user
from src.core.deps import get_correlation_read_port, get_correlation_write_port
from src.core.openapi_tags import TAG_INTEGRATION_CORRELATION
from src.models import User
from src.schemas.correlation import ChainCheckRequest, ChainCheckResponse, CorrelationContextRequest
from src.schemas.v1.correlation import CorrelationIngestRequestV1
from src.services.async_read.correlation import AsyncCorrelationReadService
from src.services.async_write.correlation import AsyncCorrelationWriteService

router = APIRouter(prefix="/correlation", tags=[TAG_INTEGRATION_CORRELATION])

CorrelationReadSvc = Annotated[AsyncCorrelationReadService, Depends(get_correlation_read_port)]
CorrelationWriteSvc = Annotated[AsyncCorrelationWriteService, Depends(get_correlation_write_port)]


@router.post("/chain-check", response_model=ChainCheckResponse)
async def correlation_chain_check_v1(
    body: ChainCheckRequest,
    service: CorrelationReadSvc,
    _: Annotated[User, Depends(get_current_user)],
):
    return await service.chain_check(body.resource_ids)


@router.post("/context")
async def correlation_context_v1(
    body: CorrelationContextRequest,
    service: CorrelationReadSvc,
    _: Annotated[User, Depends(get_current_user)],
):
    return await handle_correlation_context(service, body.resource_ids, body.depth)


@router.post("/ingest")
async def correlation_ingest_v1(
    body: CorrelationIngestRequestV1,
    service: CorrelationWriteSvc,
    _: Annotated[User, Depends(get_current_user)],
):
    alerts = [a.model_dump(exclude_none=True) for a in body.alerts]
    return await handle_correlation_ingest(
        service,
        alerts,
        source=body.source,
        depth=body.depth,
        page=body.page,
        page_size=body.page_size,
        webhook_url=body.webhook_url,
        dispatch_webhook=body.dispatch_webhook,
    )
