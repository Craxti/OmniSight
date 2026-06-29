"""Default autodiscover profile mapping rules."""

from __future__ import annotations

from src.core.constants import FIELD_ALIASES

DEFAULT_MAPPING_RULES = {
    "synonyms": {k: v for k, v in FIELD_ALIASES.items() if k in {"host", "ip_address", "external_id"}},
    "templates": {
        "Server": ["hostname", "ip", "os", "environment", "owner"],
        "Application": ["hostname", "ip", "serviceCode", "applicationCode"],
        "Database": ["hostname", "ip", "externalId", "engine"],
        "Network Element": ["hostname", "externalId"],
    },
}
