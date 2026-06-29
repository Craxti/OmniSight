"""Shared import/export request schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from src.schemas.ci import ImportTypeMappingEntry


class ImportWithMappingsRequest(BaseModel):
    items: list[dict[str, Any]]
    type_mappings: list[ImportTypeMappingEntry] | None = None
