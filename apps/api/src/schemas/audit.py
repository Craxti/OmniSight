from typing import Any

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: int | None
    action: str
    user_email: str | None
    old_value: dict[str, Any] | None
    new_value: dict[str, Any] | None
    created_at: str | None = None


class AuditListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int
    skip: int
    limit: int


class RelationValidationResponse(BaseModel):
    valid: bool
    issues: list[dict[str, Any]]
    issue_count: int
