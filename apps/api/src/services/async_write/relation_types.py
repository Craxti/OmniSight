"""Native async relation type catalog write service."""

from __future__ import annotations

from sqlalchemy import func, select

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.core.constants import CACHE_PREFIXES_CORRELATION, RELATION_TYPES
from src.core.exceptions import ConflictError, DomainValidationError
from src.models import Relation, User
from src.models.relation_type import RelationType
from src.schemas.relation_type import RelationTypeCreate, RelationTypeUpdate
from src.services.async_mutations import commit_entity_mutation_async, log_and_commit_mutation_async
from src.services.base.async_domain import AsyncDomainService
from src.services.domain.relation_types import relation_type_to_dict


class AsyncRelationTypeWriteService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)
        self._types = bundle.relation_types
        self._relations = bundle.relations
        self._audit = bundle.audit

    async def _type_dict(self, type_id: int) -> dict:
        return relation_type_to_dict(await self._types.get_or_raise(type_id))

    async def create_type(self, body: RelationTypeCreate, user: User) -> dict:
        if body.name in RELATION_TYPES:
            raise ConflictError("Relation type name is reserved for system types")
        if await self._types.name_taken(body.name):
            raise ConflictError("Relation type name already exists")
        row = RelationType(
            name=body.name,
            description=body.description,
            is_official=False,
        )
        self._session.add(row)
        await self._session.flush()
        row = await self._types.get_or_raise(row.id)
        await commit_entity_mutation_async(
            self._session,
            self._audit,
            row,
            entity_type="relation_type",
            entity_id=row.id,
            action="create",
            user_email=user.email,
            new_value=relation_type_to_dict(row),
            cache_prefix=CACHE_PREFIXES_CORRELATION,
        )
        return await self._type_dict(row.id)

    async def update_type(self, type_id: int, body: RelationTypeUpdate, user: User) -> dict:
        row = await self._types.get_or_raise(type_id)
        if row.is_official or row.name in RELATION_TYPES:
            raise DomainValidationError("Cannot edit official relation type")
        old = relation_type_to_dict(row)
        data = body.model_dump(exclude_unset=True)
        if "name" in data and data["name"] != row.name:
            if await self._types.name_taken(data["name"], exclude_id=type_id):
                raise ConflictError("Relation type name already exists")
            if await self._count_active_relations(row.name):
                raise ConflictError("Relation type is used by active relations")
        for key, value in data.items():
            setattr(row, key, value)
        await commit_entity_mutation_async(
            self._session,
            self._audit,
            row,
            entity_type="relation_type",
            entity_id=row.id,
            action="update",
            user_email=user.email,
            old_value=old,
            new_value=relation_type_to_dict(row),
            cache_prefix=CACHE_PREFIXES_CORRELATION,
        )
        return await self._type_dict(type_id)

    async def delete_type(self, type_id: int, user: User) -> dict:
        row = await self._types.get_or_raise(type_id)
        if row.is_official or row.name in RELATION_TYPES:
            raise DomainValidationError("Cannot delete official relation type")
        if await self._count_active_relations(row.name):
            raise ConflictError("Relation type is used by active relations")
        old = relation_type_to_dict(row)
        await self._session.delete(row)
        await log_and_commit_mutation_async(
            self._session,
            self._audit,
            entity_type="relation_type",
            entity_id=type_id,
            action="delete",
            user_email=user.email,
            old_value=old,
            cache_prefix=CACHE_PREFIXES_CORRELATION,
        )
        return {"ok": True}

    async def _count_active_relations(self, relation_type: str) -> int:
        stmt = (
            select(func.count())
            .select_from(Relation)
            .where(
                Relation.relation_type == relation_type,
                Relation.is_deleted.is_(False),
                Relation.status != "archived",
            )
        )
        result = await self._session.execute(stmt)
        return int(result.scalar_one())
