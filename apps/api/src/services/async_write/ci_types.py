"""Native async CI type write service."""

from __future__ import annotations

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.core.constants import CACHE_PREFIXES_CORRELATION
from src.core.exceptions import ConflictError, DomainValidationError
from src.models import CIType, User
from src.schemas.ci import CITypeCreate, CITypeUpdate
from src.services.async_ci.lifecycle import hard_delete_recycled_ci_async
from src.services.async_mutations import commit_entity_mutation_async, log_and_commit_mutation_async
from src.services.base.async_domain import AsyncDomainService
from src.services.ci.types import type_to_dict


class AsyncCiTypeWriteService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)
        self._types = bundle.ci_types
        self._ci = bundle.ci
        self._relations = bundle.relations
        self._audit = bundle.audit

    async def _type_dict(self, type_id: int) -> dict:
        return type_to_dict(await self._types.get_or_raise(type_id))

    async def create_type(self, body: CITypeCreate, user: User, *, is_import_draft: bool = False) -> dict:
        if await self._types.name_taken(body.name):
            raise ConflictError("Type name already exists")
        schema = body.attribute_schema or {"properties": {}}
        ci_type = CIType(
            name=body.name,
            description=body.description,
            attribute_schema=schema,
            is_official=False,
            is_import_draft=is_import_draft,
        )
        self._session.add(ci_type)
        await self._session.flush()
        ci_type = await self._types.get_or_raise(ci_type.id)
        await commit_entity_mutation_async(
            self._session,
            self._audit,
            ci_type,
            entity_type="ci_type",
            entity_id=ci_type.id,
            action="create",
            user_email=user.email,
            new_value=type_to_dict(ci_type),
            cache_prefix=CACHE_PREFIXES_CORRELATION,
        )
        return await self._type_dict(ci_type.id)

    async def update_type(self, type_id: int, body: CITypeUpdate, user: User) -> dict:
        ci_type = await self._types.get_or_raise(type_id)
        old = type_to_dict(ci_type)
        data = body.model_dump(exclude_unset=True)
        if "name" in data and data["name"] != ci_type.name:
            if await self._types.name_taken(data["name"], exclude_id=type_id):
                raise ConflictError("Type name already exists")
        for key, value in data.items():
            setattr(ci_type, key, value)
        await commit_entity_mutation_async(
            self._session,
            self._audit,
            ci_type,
            entity_type="ci_type",
            entity_id=ci_type.id,
            action="update",
            user_email=user.email,
            old_value=old,
            new_value=type_to_dict(ci_type),
            cache_prefix=CACHE_PREFIXES_CORRELATION,
        )
        return await self._type_dict(type_id)

    async def delete_type(self, type_id: int, user: User) -> dict:
        ci_type = await self._types.get_or_raise(type_id)
        if ci_type.is_official:
            raise DomainValidationError("Cannot delete official RSM type")
        if await self._ci.count_active_by_type(type_id):
            raise ConflictError("Type is used by active CI elements")
        for ci in await self._ci.list_recycled_by_type(type_id):
            await hard_delete_recycled_ci_async(self._session, ci, rel_repo=self._relations)
        old = type_to_dict(ci_type)
        await self._session.delete(ci_type)
        await log_and_commit_mutation_async(
            self._session,
            self._audit,
            entity_type="ci_type",
            entity_id=type_id,
            action="delete",
            user_email=user.email,
            old_value=old,
            cache_prefix=CACHE_PREFIXES_CORRELATION,
        )
        return {"ok": True}
