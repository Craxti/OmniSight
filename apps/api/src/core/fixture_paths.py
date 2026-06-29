"""Paths to shared repo-level JSON fixtures."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def fixture_path(name: str) -> Path:
    return repo_root() / "fixtures" / name
