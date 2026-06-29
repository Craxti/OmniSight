from typing import Annotated

from fastapi import APIRouter, Depends
from src.api.handlers.dashboard import handle_dashboard_overview
from src.core.auth import require_viewer
from src.core.deps import get_dashboard_read_port
from src.models import User
from src.services.async_read.dashboard import AsyncDashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard v1"])

DashboardSvc = Annotated[AsyncDashboardService, Depends(get_dashboard_read_port)]


@router.get("/overview")
async def dashboard_overview_v1(
    service: DashboardSvc,
    _: Annotated[User, Depends(require_viewer)],
):
    return await handle_dashboard_overview(service)
