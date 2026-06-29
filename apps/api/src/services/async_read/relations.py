from __future__ import annotations

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.core.exceptions import NotFoundError
from src.schemas.audit import RelationValidationResponse
from src.services.base.async_domain import AsyncDomainService
from src.services.domain.relations import serialize_relation, serialize_relations, serialize_relations_page
from src.services.rsm.async_validation import validate_relations_async


class AsyncRelationReadService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)

    async def list_relations_page(self, **kwargs) -> tuple[list, int]:
        skip = kwargs.pop("skip", 0)
        limit = kwargs.pop("limit", 100)
        rows, total = await self._bundle.relations.list_active_page(skip=skip, limit=limit, **kwargs)
        return serialize_relations_page(rows, total)

    async def list_relations(self) -> list:
        rows = await self._bundle.relations.list_active()
        return serialize_relations(rows)

    async def get_relation(self, relation_id: int):
        rel = await self._bundle.relations.get_active(relation_id)
        if not rel:
            raise NotFoundError("Relation not found")
        return serialize_relation(rel)

    async def validate_model(self) -> RelationValidationResponse:
        payload = await validate_relations_async(
            ci_repo=self._bundle.ci,
            rel_repo=self._bundle.relations,
        )
        return RelationValidationResponse.model_validate(payload)

    async def list_for_export(self):
        return await self._bundle.relations.list_active()
