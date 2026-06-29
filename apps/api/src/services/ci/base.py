"""Shared CI domain helpers used by CRUD and import services."""

from __future__ import annotations

from sqlalchemy.orm import Session
from src.core.constants import CI_STATUSES
from src.core.exceptions import DomainValidationError
from src.core.ip_validation import is_valid_ip_address
from src.models import CI
from src.repositories.protocols import CiRepositoryProtocol, CITypeRepositoryProtocol
from src.schemas.ci import CICreate


class CiDomainMixin:
    """CI validation helpers. Subclasses must call ``_init_ci_domain`` from ``__init__``."""

    _db: Session
    _ci_repo: CiRepositoryProtocol
    _type_repo: CITypeRepositoryProtocol

    def _init_ci_domain(
        self,
        db: Session,
        *,
        ci_repo: CiRepositoryProtocol,
        type_repo: CITypeRepositoryProtocol,
    ) -> None:
        self._db = db
        self._ci_repo = ci_repo
        self._type_repo = type_repo

    def resolve_type_id(self, body: CICreate) -> int:
        if body.type_id:
            return self._type_repo.require_by_id(body.type_id).id
        if body.type_name:
            return self._type_repo.require_by_name(body.type_name).id
        raise DomainValidationError("type_id or type_name required")

    @staticmethod
    def validate_status(status: str) -> None:
        if status not in CI_STATUSES:
            raise DomainValidationError(f"Invalid status. Allowed: {CI_STATUSES}")

    @staticmethod
    def validate_ip_fields(
        attributes: dict | None,
        external_ids: dict | None,
    ) -> None:
        for container in (attributes, external_ids):
            if not container:
                continue
            ip = container.get("ip")
            if ip is None:
                continue
            if not is_valid_ip_address(str(ip)):
                raise DomainValidationError("Invalid IP address")

    @staticmethod
    def ci_row_unchanged(existing: CI, body: CICreate, type_id: int) -> bool:
        if existing.type_id != type_id:
            return False
        for field, val in body.model_dump(exclude={"type_id", "type_name"}).items():
            if val is None:
                continue
            if getattr(existing, field) != val:
                return False
        return True
