from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile
from src.api.handlers.import_export import (
    handle_relations_export_json,
    handle_relations_export_tabular,
    handle_relations_import_csv,
    handle_relations_import_json,
)
from src.api.handlers.inventory import (
    handle_relation_create,
    handle_relation_delete,
    handle_relation_detail,
    handle_relation_update,
    handle_relations_list,
    handle_relations_validate,
)
from src.core.auth import require_admin, require_editor, require_viewer
from src.core.deps import (
    get_relation_import_export_read_port,
    get_relation_import_export_write_port,
    get_relation_read_port,
    get_relation_write_port,
)
from src.models import User
from src.schemas.relations import RelationCreate, RelationImportRequest, RelationUpdate
from src.services.async_read.import_export import AsyncRelationImportExportReadService
from src.services.async_read.relations import AsyncRelationReadService
from src.services.async_write.import_export import AsyncRelationImportExportWriteService
from src.services.async_write.relations import AsyncRelationWriteService

from src.core.openapi_tags import TAG_ADMIN_RELATIONS

router = APIRouter(prefix="/relations", tags=[TAG_ADMIN_RELATIONS])

RelationReadSvc = Annotated[AsyncRelationReadService, Depends(get_relation_read_port)]
RelationWriteSvc = Annotated[AsyncRelationWriteService, Depends(get_relation_write_port)]
RelationImportExportReadSvc = Annotated[
    AsyncRelationImportExportReadService,
    Depends(get_relation_import_export_read_port),
]
RelationImportExportSvc = Annotated[
    AsyncRelationImportExportWriteService,
    Depends(get_relation_import_export_write_port),
]


@router.get("")
async def list_relations_v1(
    service: RelationReadSvc,
    _: Annotated[User, Depends(require_viewer)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=500),
    q: str | None = None,
    relation_type: str | None = None,
    status: str | None = None,
    data_source: str | None = None,
    source_name: str | None = None,
    target_name: str | None = None,
):
    return await handle_relations_list(
        service,
        page=page,
        page_size=page_size,
        q=q,
        relation_type=relation_type,
        status=status,
        data_source=data_source,
        source_name=source_name,
        target_name=target_name,
    )


@router.get("/validate")
async def validate_relations_v1(
    service: RelationReadSvc,
    _: Annotated[User, Depends(require_viewer)],
):
    return await handle_relations_validate(service)


@router.get("/export")
async def export_relations_json_v1(
    service: RelationReadSvc,
    _: Annotated[User, Depends(require_viewer)],
):
    return await handle_relations_export_json(service)


@router.get("/export/csv")
async def export_relations_csv_v1(
    service: RelationImportExportReadSvc,
    user: Annotated[User, Depends(require_viewer)],
):
    return await handle_relations_export_tabular(service, user, export_format="csv")


@router.get("/export/xlsx")
async def export_relations_xlsx_v1(
    service: RelationImportExportReadSvc,
    user: Annotated[User, Depends(require_viewer)],
):
    return await handle_relations_export_tabular(service, user, export_format="xlsx")


@router.post("/import/json")
async def import_relations_json_v1(
    body: RelationImportRequest,
    service: RelationImportExportSvc,
    user: Annotated[User, Depends(require_admin)],
):
    return await handle_relations_import_json(service, body, user)


@router.post("/import/csv")
async def import_relations_csv_v1(
    service: RelationImportExportSvc,
    user: Annotated[User, Depends(require_admin)],
    file: UploadFile = File(...),
):
    content = (await file.read()).decode("utf-8")
    return await handle_relations_import_csv(service, content, user)


@router.post("")
async def create_relation_v1(
    body: RelationCreate,
    service: RelationWriteSvc,
    user: Annotated[User, Depends(require_editor)],
):
    return await handle_relation_create(service, body, user)


@router.get("/{relation_id}")
async def get_relation_v1(
    relation_id: int,
    service: RelationReadSvc,
    _: Annotated[User, Depends(require_viewer)],
):
    return await handle_relation_detail(service, relation_id)


@router.patch("/{relation_id}")
async def update_relation_v1(
    relation_id: int,
    body: RelationUpdate,
    service: RelationWriteSvc,
    user: Annotated[User, Depends(require_editor)],
):
    return await handle_relation_update(service, relation_id, body, user)


@router.delete("/{relation_id}")
async def delete_relation_v1(
    relation_id: int,
    service: RelationWriteSvc,
    user: Annotated[User, Depends(require_editor)],
):
    return await handle_relation_delete(service, relation_id, user)
