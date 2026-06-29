"""Import-time validation for CI and relations (FR 23, §6)."""

from sqlalchemy.orm import Session
from src.core.constants import FIELD_TO_SEARCH_COLUMN, RELATION_STATUSES
from src.core.exceptions import DomainValidationError
from src.repositories.protocols import CiRepositoryProtocol
from src.services.rsm.depends_on_cycle import would_create_depends_on_cycle


def validate_relation_status(status: str) -> None:
    if status not in RELATION_STATUSES:
        raise DomainValidationError(f"Invalid relation status. Allowed: {RELATION_STATUSES}")


def find_external_id_conflict(
    db: Session,
    external_ids: dict,
    *,
    exclude_ci_id: int | None = None,
    ci_repo: CiRepositoryProtocol,
) -> str | None:
    """Return error if any external id is already used by another active CI."""
    for field, col_name in FIELD_TO_SEARCH_COLUMN.items():
        val = external_ids.get(field)
        if val is None or not str(val).strip():
            continue
        other = ci_repo.find_by_search_field(col_name, str(val), exclude_ci_id=exclude_ci_id)
        if other:
            return f"Duplicate {field}={val!r} already used by CI '{other.name}'"
    return None


def validate_relation_endpoints(
    db: Session,
    source_id: int,
    target_id: int,
    *,
    ci_repo: CiRepositoryProtocol,
) -> list[str]:
    errors: list[str] = []
    source = ci_repo.get_active(source_id)
    target = ci_repo.get_active(target_id)
    if not source:
        errors.append(f"Source CI {source_id} not found")
    elif source.status == "archived":
        errors.append(f"Source CI '{source.name}' is archived")
    if not target:
        errors.append(f"Target CI {target_id} not found")
    elif target.status == "archived":
        errors.append(f"Target CI '{target.name}' is archived")
    if source_id == target_id:
        errors.append("Self-referencing relation is not allowed")
    return errors


__all__ = [
    "find_external_id_conflict",
    "validate_relation_endpoints",
    "validate_relation_status",
    "would_create_depends_on_cycle",
]
