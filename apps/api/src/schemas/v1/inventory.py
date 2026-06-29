"""v1 inventory list schemas."""

from typing import Any, Literal

from pydantic import BaseModel, Field
from src.schemas.ci import ImportTypePreview
from src.schemas.v1.common import PaginationParams

INVENTORY_SCHEMA_V1 = "rsm-inventory-v1"


class InventoryV1Envelope(BaseModel):
    api_version: Literal["v1"] = "v1"
    schema_version: str = INVENTORY_SCHEMA_V1


class ImportTypePreviewV1Response(InventoryV1Envelope):
    export: ImportTypePreview


class ExportPayloadV1Response(InventoryV1Envelope):
    export: dict[str, Any]


class CIListQueryV1(PaginationParams):
    q: str | None = None
    name: str | None = None
    status: str | None = None
    type_id: int | None = None
    environment: str | None = None
    owner: str | None = None
    hostname: str | None = None
    external_id: str | None = None
    service_code: str | None = None
    application_code: str | None = None
    sort_by: str = Field(default="id")
    sort_dir: str = Field(default="desc", pattern="^(asc|desc)$")
