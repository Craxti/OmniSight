"""CI field application helpers for autodiscover apply."""

from __future__ import annotations

from src.models import CI
from src.services.autodiscover.normalize import EXTERNAL_ID_FIELDS, TOP_LEVEL_FIELDS


def apply_field(ci: CI, field: str, value: str) -> None:
    if field in TOP_LEVEL_FIELDS:
        setattr(ci, field, value)
        return
    if field in EXTERNAL_ID_FIELDS:
        ext = dict(ci.external_ids or {})
        ext[field] = value
        ci.external_ids = ext
        attrs = dict(ci.attributes or {})
        attrs[field] = value
        ci.attributes = attrs
        return
    if field.startswith("attributes."):
        key = field.split(".", 1)[1]
        attrs = dict(ci.attributes or {})
        attrs[key] = value
        ci.attributes = attrs
        return
    attrs = dict(ci.attributes or {})
    attrs[field] = value
    ci.attributes = attrs
