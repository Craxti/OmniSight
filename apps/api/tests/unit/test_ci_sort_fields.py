"""Ensure CI sort fields stay aligned across API and repository layers."""

from src.core.constants import CI_LIST_SORT_FIELDS
from src.repositories.queries.ci import _SORT_COLUMNS


def test_ci_list_sort_fields_match_repository_columns():
    assert frozenset(CI_LIST_SORT_FIELDS) == frozenset(_SORT_COLUMNS)
