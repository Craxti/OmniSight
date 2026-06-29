"""Data models for host discovery."""

from __future__ import annotations


class ContainerMeta:
    __slots__ = ("env", "labels")

    def __init__(self, env: list[str] | None = None, labels: dict[str, str] | None = None) -> None:
        self.env = env or []
        self.labels = labels or {}
