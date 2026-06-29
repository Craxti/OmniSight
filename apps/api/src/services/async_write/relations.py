"""Native async relation write service."""

from __future__ import annotations

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.core.constants import CACHE_PREFIXES_CORRELATION
from src.core.exceptions import NotFoundError
from src.core.serializers import relation_snapshot
from src.models import Relation, User
from src.schemas.relations import RelationCreate, RelationResponse, RelationUpdate
from src.services.async_mutations import commit_entity_mutation_async, log_and_commit_mutation_async
from src.services.async_relations.validator import AsyncRelationValidator
from src.services.base.async_domain import AsyncDomainService
from src.services.domain.relations import serialize_relation
from src.services.import_validate import validate_relation_status


class AsyncRelationWriteService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)
        self._rel = bundle.relations
        self._audit = bundle.audit
        self._validator = AsyncRelationValidator(bundle.ci, bundle.relations, bundle.relation_types)

    async def _get_relation_or_404(self, relation_id: int) -> Relation:
        rel = await self._rel.get_active(relation_id)
        if not rel:
            raise NotFoundError("Relation not found")
        return rel

    async def _relation_response(self, relation_id: int) -> RelationResponse:
        return serialize_relation(await self._get_relation_or_404(relation_id))

    async def create_relation(self, body: RelationCreate, user: User) -> RelationResponse:
        rel_type = await self._validator.validate_for_create(
            body.source_ci_id,
            body.target_ci_id,
            body.relation_type,
            body.status,
        )
        rel = Relation(
            source_ci_id=body.source_ci_id,
            target_ci_id=body.target_ci_id,
            relation_type=rel_type,
            status=body.status,
            data_source=body.data_source,
        )
        self._session.add(rel)
        await self._session.flush()
        rel = await self._get_relation_or_404(rel.id)
        await commit_entity_mutation_async(
            self._session,
            self._audit,
            rel,
            entity_type="relation",
            entity_id=rel.id,
            action="create",
            user_email=user.email,
            new_value=relation_snapshot(rel),
            cache_prefix=list(CACHE_PREFIXES_CORRELATION),
        )
        return await self._relation_response(rel.id)

    async def update_relation(
        self,
        relation_id: int,
        body: RelationUpdate,
        user: User,
    ) -> RelationResponse:
        rel = await self._get_relation_or_404(relation_id)
        old = relation_snapshot(rel)
        data = body.model_dump(exclude_unset=True)
        if "relation_type" in data:
            data["relation_type"] = await self._validator.normalize_type(data["relation_type"])
        if "status" in data and data["status"] is not None:
            validate_relation_status(data["status"])
        for key, value in data.items():
            setattr(rel, key, value)
        await commit_entity_mutation_async(
            self._session,
            self._audit,
            rel,
            entity_type="relation",
            entity_id=rel.id,
            action="update",
            user_email=user.email,
            old_value=old,
            new_value=relation_snapshot(rel),
            cache_prefix=list(CACHE_PREFIXES_CORRELATION),
        )
        return await self._relation_response(rel.id)

    async def delete_relation(self, relation_id: int, user: User) -> dict:
        rel = await self._get_relation_or_404(relation_id)
        old = relation_snapshot(rel)
        rel.status = "archived"
        rel.is_deleted = True
        await log_and_commit_mutation_async(
            self._session,
            self._audit,
            entity_type="relation",
            entity_id=rel.id,
            action="delete",
            user_email=user.email,
            old_value=old,
            new_value=relation_snapshot(rel),
            cache_prefix=list(CACHE_PREFIXES_CORRELATION),
        )
        return {"ok": True}
