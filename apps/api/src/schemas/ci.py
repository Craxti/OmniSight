from typing import Any

from pydantic import BaseModel, Field


class CICreate(BaseModel):
    name: str
    type_id: int | None = None
    type_name: str | None = None
    description: str | None = None
    status: str = "active"
    criticality: str | None = None
    environment: str | None = None
    owner: str | None = None
    team: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    external_ids: dict[str, Any] = Field(default_factory=dict)


class CIUpdate(BaseModel):
    name: str | None = None
    type_id: int | None = None
    description: str | None = None
    status: str | None = None
    criticality: str | None = None
    environment: str | None = None
    owner: str | None = None
    team: str | None = None
    attributes: dict[str, Any] | None = None
    external_ids: dict[str, Any] | None = None


class CIResponse(BaseModel):
    id: int
    name: str
    type: str | None = None
    type_id: int
    description: str | None = None
    status: str
    criticality: str | None = None
    environment: str | None = None
    owner: str | None = None
    team: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    external_ids: dict[str, Any] = Field(default_factory=dict)
    last_changed_at: str | None = None
    created_at: str | None = None


class CIDetailResponse(CIResponse):
    relations: dict[str, Any] | None = None


class CIListResponse(BaseModel):
    items: list[CIResponse]
    total: int
    skip: int
    limit: int


class BulkStatusUpdate(BaseModel):
    ci_ids: list[int]
    status: str


class CITypeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: str | None = None
    attribute_schema: dict[str, Any] | None = None


class CITypeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = None
    attribute_schema: dict[str, Any] | None = None


class ImportTypeDraft(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: str | None = None
    attribute_schema: dict[str, Any] | None = None


class ImportTypeProposal(BaseModel):
    source_type: str
    item_count: int
    status: str
    matched_type_id: int | None = None
    matched_type_name: str | None = None
    suggestion_confidence: float | None = None
    draft: ImportTypeDraft | None = None


class ImportTypePreview(BaseModel):
    proposals: list[ImportTypeProposal]
    existing_types: list[dict[str, Any]]
    missing_type_items: int = 0
    needs_mapping: bool = False


class ImportTypeMappingEntry(BaseModel):
    source_type: str
    action: str
    target_type_id: int | None = None
    draft: ImportTypeDraft | None = None


class ImportTypeMappingResult(BaseModel):
    created_types: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
