"""Query parameter normalization tests."""

import pytest
from src.core.constants import CI_LIST_SORT_FIELDS
from src.core.exceptions import DomainValidationError
from src.core.query_params import normalize_ci_list_sort, normalize_sort_direction


def test_normalize_ci_list_sort_accepts_canonical_fields():
    for field in CI_LIST_SORT_FIELDS:
        assert normalize_ci_list_sort(field) == field


def test_normalize_ci_list_sort_rejects_unknown():
    with pytest.raises(DomainValidationError, match="Invalid sort_by"):
        normalize_ci_list_sort("not_a_field")


def test_normalize_sort_direction():
    assert normalize_sort_direction("asc") == "asc"
    assert normalize_sort_direction("desc") == "desc"
    with pytest.raises(DomainValidationError, match="sort_dir"):
        normalize_sort_direction("sideways")
