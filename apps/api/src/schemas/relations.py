from pydantic import BaseModel


class RelationCreate(BaseModel):
    source_ci_id: int
    target_ci_id: int
    relation_type: str
    status: str = "active"
    data_source: str | None = None


class RelationUpdate(BaseModel):
    relation_type: str | None = None
    status: str | None = None
    data_source: str | None = None


class RelationResponse(BaseModel):
    id: int
    source_ci_id: int
    target_ci_id: int
    source_name: str | None = None
    target_name: str | None = None
    relation_type: str
    status: str
    data_source: str | None = None
    direction: str
    created_at: str | None = None
    last_changed_at: str | None = None


class RelationImportItem(BaseModel):
    source_ci_id: int | None = None
    target_ci_id: int | None = None
    source_name: str | None = None
    target_name: str | None = None
    relation_type: str
    status: str = "active"
    data_source: str | None = None


class RelationImportRequest(BaseModel):
    relations: list[RelationImportItem]
