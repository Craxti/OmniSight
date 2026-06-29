"""CI list/search SELECT builders."""

from __future__ import annotations

from sqlalchemy import String, cast, func, select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql import Select

from src.core.constants import CI_LIST_SORT_FIELDS
from src.core.query_params import normalize_ci_list_sort, normalize_sort_direction
from src.models import CI, CIType, Relation

_SORT_COLUMNS = {
    "id": CI.id,
    "name": CI.name,
    "status": CI.status,
    "environment": CI.environment,
    "owner": CI.owner,
    "created_at": CI.created_at,
    "updated_at": CI.updated_at,
}
assert frozenset(_SORT_COLUMNS) == frozenset(CI_LIST_SORT_FIELDS)


def apply_ci_list_filters(
    stmt: Select,
    *,
    q: str | None = None,
    type_name: str | None = None,
    status: str | None = None,
    environment: str | None = None,
    owner: str | None = None,
    hostname: str | None = None,
    ip: str | None = None,
    external_id: str | None = None,
    service_code: str | None = None,
    application_code: str | None = None,
    cmdb_id: str | None = None,
    include_deleted: bool = False,
) -> Select:
    if not include_deleted:
        stmt = stmt.where(CI.is_deleted.is_(False))
    if type_name:
        stmt = stmt.join(CIType).where(CIType.name == type_name)
    if status:
        stmt = stmt.where(CI.status == status)
    if environment:
        stmt = stmt.where(CI.environment == environment)
    if owner:
        stmt = stmt.where(CI.owner.ilike(f"%{owner}%"))
    if hostname:
        stmt = stmt.where(CI.search_hostname == hostname)
    if ip:
        stmt = stmt.where(CI.search_ip == ip)
    if external_id:
        stmt = stmt.where(CI.search_external_id == external_id)
    if service_code:
        stmt = stmt.where(CI.search_service_code == service_code)
    if application_code:
        stmt = stmt.where(CI.search_application_code == application_code)
    if cmdb_id:
        try:
            stmt = stmt.where(CI.id == int(cmdb_id))
        except (TypeError, ValueError):
            stmt = stmt.where(CI.id == -1)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            (CI.name.ilike(like))
            | (CI.description.ilike(like))
            | (CI.owner.ilike(like))
            | (CI.search_hostname.ilike(like))
            | (cast(CI.attributes, String).ilike(like))
        )
    return stmt


def ci_base_select(*, include_deleted: bool = False) -> Select:
    stmt = select(CI).options(joinedload(CI.ci_type))
    return apply_ci_list_filters(stmt, include_deleted=include_deleted)


def ci_detail_load_options():
    return (
        joinedload(CI.ci_type),
        selectinload(CI.outgoing_relations).joinedload(Relation.source_ci),
        selectinload(CI.outgoing_relations).joinedload(Relation.target_ci),
        selectinload(CI.incoming_relations).joinedload(Relation.source_ci),
        selectinload(CI.incoming_relations).joinedload(Relation.target_ci),
    )


def ci_detail_select(ci_id: int, *, include_deleted: bool = False) -> Select:
    stmt = select(CI).options(*ci_detail_load_options()).where(CI.id == ci_id)
    if not include_deleted:
        stmt = stmt.where(CI.is_deleted.is_(False))
    return stmt


def ci_search_select(
    *,
    q: str | None = None,
    type_name: str | None = None,
    status: str | None = None,
    environment: str | None = None,
    owner: str | None = None,
    hostname: str | None = None,
    ip: str | None = None,
    external_id: str | None = None,
    service_code: str | None = None,
    application_code: str | None = None,
    cmdb_id: str | None = None,
    sort_by: str = "id",
    sort_dir: str = "desc",
    skip: int = 0,
    limit: int = 50,
) -> Select:
    normalize_ci_list_sort(sort_by)
    normalize_sort_direction(sort_dir)
    column = _SORT_COLUMNS[sort_by]
    stmt = ci_base_select()
    stmt = apply_ci_list_filters(
        stmt,
        q=q,
        type_name=type_name,
        status=status,
        environment=environment,
        owner=owner,
        hostname=hostname,
        ip=ip,
        external_id=external_id,
        service_code=service_code,
        application_code=application_code,
        cmdb_id=cmdb_id,
    )
    order = column.desc() if sort_dir == "desc" else column.asc()
    return stmt.order_by(order).offset(skip).limit(limit)


def ci_search_count_select(**filters) -> Select:
    stmt = select(func.count()).select_from(CI)
    return apply_ci_list_filters(stmt, include_deleted=False, **filters)
