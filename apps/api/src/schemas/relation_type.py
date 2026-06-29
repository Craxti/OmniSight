import re

from pydantic import BaseModel, Field, field_validator

_RELATION_TYPE_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")


class RelationTypeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if not _RELATION_TYPE_NAME_RE.match(normalized):
            raise ValueError("Name must be snake_case: lowercase letters, digits, underscores")
        return normalized


class RelationTypeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=64)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not _RELATION_TYPE_NAME_RE.match(normalized):
            raise ValueError("Name must be snake_case: lowercase letters, digits, underscores")
        return normalized
