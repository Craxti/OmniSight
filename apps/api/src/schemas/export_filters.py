"""Shared export filter parameters for CI/RSM exports."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CiExportFilter:
    type_id: int | None = None
    environment: str | None = None
    owner: str | None = None
    criticality: str | None = None
    business_service_id: int | None = None
    service_code: str | None = None

    def as_dict(self) -> dict[str, int | str | None]:
        return asdict(self)
