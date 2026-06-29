"""CI lifecycle helpers shared across services."""

from sqlalchemy.orm import Session
from src.models import CI
from src.repositories.protocols import RelationRepositoryProtocol


def hard_delete_recycled_ci(
    db: Session,
    ci: CI,
    *,
    rel_repo: RelationRepositoryProtocol,
) -> None:
    """Permanently remove a soft-deleted CI and its relations (recycle-bin purge)."""
    rel_repo.delete_for_ci(ci.id)
    db.delete(ci)
