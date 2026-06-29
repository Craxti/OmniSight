import pytest
from src.core.exceptions import DomainValidationError
from src.services.rsm.normalize import normalize_relation_type


def test_normalize_relation_type_canonical():
    assert normalize_relation_type("depends_on") == "depends_on"
    assert normalize_relation_type("uses") == "uses"


def test_normalize_relation_type_alias():
    assert normalize_relation_type("depends on") == "depends_on"
    assert normalize_relation_type("DEPENDS ON") == "depends_on"
    assert normalize_relation_type("part of") == "part_of"


def test_normalize_relation_type_invalid():
    with pytest.raises(DomainValidationError, match="Invalid relation type"):
        normalize_relation_type("unknown_type")
