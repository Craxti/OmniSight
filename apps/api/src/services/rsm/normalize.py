from src.core.constants import RELATION_TYPE_ALIASES, RELATION_TYPES
from src.core.exceptions import DomainValidationError


def normalize_relation_type(value: str, *, allowed: frozenset[str] | None = None) -> str:
    normalized = RELATION_TYPE_ALIASES.get(value.lower(), value)
    types = allowed if allowed is not None else frozenset(RELATION_TYPES)
    if normalized not in types:
        raise DomainValidationError(f"Invalid relation type: {value}")
    return normalized
