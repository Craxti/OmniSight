from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, Query, UploadFile
from src.api.handlers.import_export import (
    handle_ci_export_full,
    handle_ci_export_tabular,
    handle_ci_import_csv,
    handle_ci_import_json,
    handle_ci_import_preview,
)
from src.api.handlers.inventory import (
    handle_ci_bulk_status,
    handle_ci_create,
    handle_ci_delete,
    handle_ci_detail,
    handle_ci_list,
    handle_ci_purge,
    handle_ci_recycle_bin,
    handle_ci_relations,
    handle_ci_restore,
    handle_ci_update,
)
from src.core.auth import require_admin, require_editor, require_viewer
from src.core.constants import CI_LIST_SORT_FIELDS
from src.core.deps import (
    get_ci_import_export_read_port,
    get_ci_read_port,
    get_ci_write_port,
    get_topology_read_port,
    get_transactional_ci_import_export_write_port,
)
from src.core.openapi_tags import TAG_ADMIN_CI
from src.models import User
from src.schemas.ci import BulkStatusUpdate, CICreate, CIUpdate
from src.schemas.export_filters import CiExportFilter
from src.schemas.import_export import ImportWithMappingsRequest
from src.schemas.v1.inventory import ImportTypePreviewV1Response
from src.services.async_read.ci import AsyncCiReadService
from src.services.async_read.import_export import AsyncCiImportExportReadService
from src.services.async_read.topology import AsyncTopologyService
from src.services.async_write.ci import AsyncCiWriteService
from src.services.async_write.import_export import AsyncCiImportExportWriteService

router = APIRouter(prefix="/ci", tags=[TAG_ADMIN_CI])

CiReadSvc = Annotated[AsyncCiReadService, Depends(get_ci_read_port)]
WriteCiSvc = Annotated[AsyncCiWriteService, Depends(get_ci_write_port)]
TopologyReadSvc = Annotated[AsyncTopologyService, Depends(get_topology_read_port)]
CiImportExportReadSvc = Annotated[AsyncCiImportExportReadService, Depends(get_ci_import_export_read_port)]
TransactionalCiImportExportSvc = Annotated[
    AsyncCiImportExportWriteService,
    Depends(get_transactional_ci_import_export_write_port),
]


@router.get("")
async def list_ci_v1(
    service: CiReadSvc,
    _: Annotated[User, Depends(require_viewer)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    q: str | None = None,
    name: str | None = None,
    status: str | None = None,
    type_id: int | None = None,
    environment: str | None = None,
    owner: str | None = None,
    hostname: str | None = None,
    external_id: str | None = None,
    service_code: str | None = None,
    application_code: str | None = None,
    sort_by: str = Query(default="id", description=f"Sort field: {', '.join(CI_LIST_SORT_FIELDS)}"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
):
    return await handle_ci_list(
        service,
        page=page,
        page_size=page_size,
        q=q,
        name=name,
        status=status,
        type_id=type_id,
        environment=environment,
        owner=owner,
        hostname=hostname,
        external_id=external_id,
        service_code=service_code,
        application_code=application_code,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@router.post("")
async def create_ci_v1(
    body: CICreate,
    service: WriteCiSvc,
    user: Annotated[User, Depends(require_editor)],
):
    return await handle_ci_create(service, body, user)


@router.get("/recycle-bin")
async def recycle_bin_v1(
    service: CiReadSvc,
    _: Annotated[User, Depends(require_viewer)],
):
    return await handle_ci_recycle_bin(service)


@router.post("/bulk/status")
async def bulk_status_v1(
    body: BulkStatusUpdate,
    service: WriteCiSvc,
    user: Annotated[User, Depends(require_editor)],
):
    return await handle_ci_bulk_status(service, body, user)


@router.post("/import/preview", response_model=ImportTypePreviewV1Response)
async def import_preview_v1(
    items: list[dict[str, Any]],
    service: CiImportExportReadSvc,
    _: Annotated[User, Depends(require_admin)],
):
    return await handle_ci_import_preview(service, items)


@router.post("/import")
async def import_json_v1(
    items: list[dict[str, Any]],
    service: TransactionalCiImportExportSvc,
    user: Annotated[User, Depends(require_admin)],
):
    return await handle_ci_import_json(service, items, user)


@router.post("/import/mapped")
async def import_mapped_v1(
    body: ImportWithMappingsRequest,
    service: TransactionalCiImportExportSvc,
    user: Annotated[User, Depends(require_admin)],
):
    return await handle_ci_import_json(
        service,
        body.items,
        user,
        type_mappings=body.type_mappings,
    )


@router.post("/import/csv")
async def import_csv_v1(
    service: TransactionalCiImportExportSvc,
    user: Annotated[User, Depends(require_admin)],
    file: UploadFile = File(...),
):
    content = (await file.read()).decode("utf-8")
    return await handle_ci_import_csv(service, content, user)


@router.get("/export/full")
async def export_full_v1(
    service: CiImportExportReadSvc,
    user: Annotated[User, Depends(require_viewer)],
    type_id: int | None = None,
    environment: str | None = None,
    owner: str | None = None,
    criticality: str | None = None,
    business_service_id: int | None = None,
    service_code: str | None = None,
):
    return await handle_ci_export_full(
        service,
        user,
        CiExportFilter(
            type_id=type_id,
            environment=environment,
            owner=owner,
            criticality=criticality,
            business_service_id=business_service_id,
            service_code=service_code,
        ),
    )


@router.get("/export/csv")
async def export_csv_v1(
    service: CiImportExportReadSvc,
    user: Annotated[User, Depends(require_viewer)],
    type_id: int | None = None,
    environment: str | None = None,
    owner: str | None = None,
    criticality: str | None = None,
    business_service_id: int | None = None,
    service_code: str | None = None,
):
    return await handle_ci_export_tabular(
        service,
        user,
        export_format="csv",
        filters=CiExportFilter(
            type_id=type_id,
            environment=environment,
            owner=owner,
            criticality=criticality,
            business_service_id=business_service_id,
            service_code=service_code,
        ),
    )


@router.get("/export/xlsx")
async def export_xlsx_v1(
    service: CiImportExportReadSvc,
    user: Annotated[User, Depends(require_viewer)],
    type_id: int | None = None,
    environment: str | None = None,
    owner: str | None = None,
    criticality: str | None = None,
    business_service_id: int | None = None,
    service_code: str | None = None,
):
    return await handle_ci_export_tabular(
        service,
        user,
        export_format="xlsx",
        filters=CiExportFilter(
            type_id=type_id,
            environment=environment,
            owner=owner,
            criticality=criticality,
            business_service_id=business_service_id,
            service_code=service_code,
        ),
    )


@router.get("/{ci_id}/relations")
async def ci_relations_v1(
    ci_id: int,
    topology: TopologyReadSvc,
    _: Annotated[User, Depends(require_viewer)],
):
    return await handle_ci_relations(topology, ci_id)


@router.get("/{ci_id}")
async def get_ci_v1(
    ci_id: int,
    service: CiReadSvc,
    _: Annotated[User, Depends(require_viewer)],
):
    return await handle_ci_detail(service, ci_id)


@router.patch("/{ci_id}")
async def update_ci_v1(
    ci_id: int,
    body: CIUpdate,
    service: WriteCiSvc,
    user: Annotated[User, Depends(require_editor)],
):
    return await handle_ci_update(service, ci_id, body, user)


@router.delete("/{ci_id}")
async def delete_ci_v1(
    ci_id: int,
    service: WriteCiSvc,
    user: Annotated[User, Depends(require_editor)],
):
    return await handle_ci_delete(service, ci_id, user)


@router.post("/{ci_id}/restore")
async def restore_ci_v1(
    ci_id: int,
    service: WriteCiSvc,
    user: Annotated[User, Depends(require_editor)],
):
    return await handle_ci_restore(service, ci_id, user)


@router.delete("/{ci_id}/purge")
async def purge_ci_v1(
    ci_id: int,
    service: WriteCiSvc,
    user: Annotated[User, Depends(require_editor)],
):
    return await handle_ci_purge(service, ci_id, user)
