from __future__ import annotations

from datetime import date, datetime
from typing import Any

from src.core.constants import EXTERNAL_ID_FIELDS_SET, FIELD_ALIASES
from src.core.ip_validation import is_valid_ip_address

EXTERNAL_ID_FIELDS = EXTERNAL_ID_FIELDS_SET
TOP_LEVEL_FIELDS = frozenset({"environment", "owner", "criticality", "team"})


def normalize_field_key(key: str, rules: dict | None = None) -> str:
    synonyms = (rules or {}).get("synonyms", {})
    if key in synonyms:
        return str(synonyms[key])
    if key in FIELD_ALIASES:
        return FIELD_ALIASES[key]
    return key


def normalize_value(value: Any, field: str) -> str | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    text = str(value).strip()
    if not text:
        return None
    if field == "ip":
        return text
    if field in {"serviceCode", "applicationCode", "externalId"}:
        return text.upper() if field != "externalId" else text
    return text


def is_valid_ip(value: str) -> bool:
    return is_valid_ip_address(value)
