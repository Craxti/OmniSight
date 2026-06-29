"""Shared CI list/detail read logic (sync + async)."""

from __future__ import annotations

from typing import Any, Protocol

from src.core.serializers import ci_to_detail, ci_to_response
from src.schemas.ci import CIDetailResponse, CIListResponse, CIResponse


class TypeNameResolver(Protocol):
    def get_by_id(self, type_id: int) -> Any: ...


class AsyncTypeNameResolver(Protocol):
    async def get_by_id(self, type_id: int) -> Any: ...


class CiSearchRepo(Protocol):
    def search(self, **kwargs: Any) -> tuple[list[Any], int]: ...

    def list_deleted(self) -> list[Any]: ...

    def get_or_404(self, ci_id: int) -> Any: ...


class AsyncCiSearchRepo(Protocol):
    async def search(self, **kwargs: Any) -> tuple[list[Any], int]: ...

    async def list_deleted(self) -> list[Any]: ...

    async def get_or_404(self, ci_id: int) -> Any: ...

    async def get_detail_or_404(self, ci_id: int) -> Any: ...


def resolve_type_name(type_repo: TypeNameResolver, type_id: int | None) -> str | None:
    if not type_id:
        return None
    ci_type = type_repo.get_by_id(type_id)
    return ci_type.name if ci_type else None


async def resolve_type_name_async(type_repo: AsyncTypeNameResolver, type_id: int | None) -> str | None:
    if not type_id:
        return None
    ci_type = await type_repo.get_by_id(type_id)
    return ci_type.name if ci_type else None


def _normalize_search_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    params = dict(kwargs)
    q = params.pop("q", None)
    name = params.pop("name", None)
    if q or name:
        params["q"] = q or name
    return params


def build_ci_list_response(cis: list[Any], total: int, skip: int, limit: int) -> CIListResponse:
    return CIListResponse(
        items=[ci_to_response(c) for c in cis],
        total=total,
        skip=skip,
        limit=limit,
    )


def list_ci(
    ci_repo: CiSearchRepo,
    type_repo: TypeNameResolver,
    *,
    skip: int = 0,
    limit: int = 50,
    type_id: int | None = None,
    **search_kwargs: Any,
) -> CIListResponse:
    type_name = resolve_type_name(type_repo, type_id)
    params = _normalize_search_kwargs(search_kwargs)
    cis, total = ci_repo.search(type_name=type_name, skip=skip, limit=limit, **params)
    return build_ci_list_response(cis, total, skip, limit)


async def list_ci_async(
    ci_repo: AsyncCiSearchRepo,
    type_repo: AsyncTypeNameResolver,
    *,
    skip: int = 0,
    limit: int = 50,
    type_id: int | None = None,
    **search_kwargs: Any,
) -> CIListResponse:
    type_name = await resolve_type_name_async(type_repo, type_id)
    params = _normalize_search_kwargs(search_kwargs)
    cis, total = await ci_repo.search(type_name=type_name, skip=skip, limit=limit, **params)
    return build_ci_list_response(cis, total, skip, limit)


def list_recycle_bin(ci_repo: CiSearchRepo) -> list[CIResponse]:
    return [ci_to_response(c) for c in ci_repo.list_deleted()]


async def list_recycle_bin_async(ci_repo: AsyncCiSearchRepo) -> list[CIResponse]:
    items = await ci_repo.list_deleted()
    return [ci_to_response(c) for c in items]


def ci_detail(ci_repo: CiSearchRepo, ci_id: int) -> CIDetailResponse:
    return ci_to_detail(ci_repo.get_or_404(ci_id))


async def ci_detail_async(ci_repo: AsyncCiSearchRepo, ci_id: int) -> CIDetailResponse:
    ci = await ci_repo.get_detail_or_404(ci_id)
    return ci_to_detail(ci)
