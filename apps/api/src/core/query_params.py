"""Shared API query-parameter normalization."""

from __future__ import annotations

from src.core.constants import CI_LIST_SORT_FIELDS
from src.core.exceptions import DomainValidationError

_CI_SORT_FIELDS_SET = frozenset(CI_LIST_SORT_FIELDS)


def normalize_ci_list_sort(sort_by: str) -> str:
    """Validate CI list sort field against the canonical allow-list."""
    if sort_by not in _CI_SORT_FIELDS_SET:
        raise DomainValidationError(f"Invalid sort_by. Allowed: {sorted(CI_LIST_SORT_FIELDS)}")
    return sort_by


def normalize_sort_direction(sort_dir: str) -> str:
    if sort_dir not in ("asc", "desc"):
        raise DomainValidationError("Invalid sort_dir. Allowed: asc, desc")
    return sort_dir
