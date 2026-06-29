"""Shared import/export streaming and audit helpers."""

from __future__ import annotations

from typing import Any

from fastapi.responses import StreamingResponse
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.orm import Session
from src.core.exceptions import ConflictError, DomainValidationError, NotFoundError
from src.models import User
from src.repositories.protocols import AuditRepositoryProtocol
from src.schemas.common import ImportReport

IMPORT_ROW_ERRORS = (
    DomainValidationError,
    ConflictError,
    NotFoundError,
    PydanticValidationError,
    KeyError,
    ValueError,
)


def csv_streaming_response(content: str, filename: str) -> StreamingResponse:
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def xlsx_streaming_response(buf, filename: str) -> StreamingResponse:
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


class ImportExportAuditMixin:
    _db: Session
    _audit_repo: AuditRepositoryProtocol

    def log_export_audit(
        self,
        user: User,
        action: str,
        count: int,
        *,
        extra: dict[str, Any] | None = None,
    ) -> None:
        payload: dict[str, Any] = {"count": count}
        if extra:
            payload.update(extra)
        self._audit_repo.log(
            entity_type="export",
            entity_id=None,
            action=action,
            user_email=user.email,
            new_value=payload,
        )
        self._db.commit()

    def log_import_audit(self, user: User, action: str, report: ImportReport) -> None:
        self._audit_repo.log(
            entity_type="import",
            entity_id=None,
            action=action,
            user_email=user.email,
            new_value=report.model_dump(),
        )
        self._db.commit()
