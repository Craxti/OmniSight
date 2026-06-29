"""Domain meta HTTP handlers (v1 envelopes)."""

from __future__ import annotations

from src.api.handlers.v1_envelopes import domain_constants_v1_envelope
from src.core.constants import (
    CI_STATUSES,
    CRITICALITY_LEVELS,
    ENVIRONMENTS,
    EXTERNAL_ID_FIELDS,
    RELATION_STATUSES,
    RELATION_TYPE_ALIASES,
    ROLES,
    RSM_OFFICIAL_TYPE_NAMES,
)
from src.services.async_read.relation_types import AsyncRelationTypeReadService


async def domain_constants_payload(service: AsyncRelationTypeReadService) -> dict:
    relation_types = await service.list_keys()
    return {
        "relation_types": relation_types,
        "relation_type_aliases": RELATION_TYPE_ALIASES,
        "relation_statuses": RELATION_STATUSES,
        "ci_statuses": CI_STATUSES,
        "criticality_levels": CRITICALITY_LEVELS,
        "environments": ENVIRONMENTS,
        "external_id_fields": EXTERNAL_ID_FIELDS,
        "roles": ROLES,
        "rsm_official_type_names": RSM_OFFICIAL_TYPE_NAMES,
    }


async def handle_domain_constants(service: AsyncRelationTypeReadService):
    return domain_constants_v1_envelope(await domain_constants_payload(service))
