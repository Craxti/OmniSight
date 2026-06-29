from sqlalchemy.orm import Session
from src.models import CI
from src.repositories.protocols import CiRepositoryProtocol


def get_ci_or_404(
    db: Session,
    ci_id: int,
    include_deleted: bool = False,
    *,
    ci_repo: CiRepositoryProtocol,
) -> CI:
    return ci_repo.get_or_404(ci_id, include_deleted=include_deleted)


def is_business_service(ci: CI) -> bool:
    return bool(ci.ci_type and ci.ci_type.name == "Business Service")
