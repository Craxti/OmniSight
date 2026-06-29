"""Shared autodiscover read serializers."""

from __future__ import annotations

from typing import Any

from src.schemas.autodiscover import AutodiscoverRunSummary, SyncProfileResponse


def list_run_summaries(runs: list[Any]) -> list[AutodiscoverRunSummary]:
    return [
        AutodiscoverRunSummary(
            id=r.id,
            profile_id=r.profile_id,
            status=r.status,
            user_email=r.user_email,
            report=r.report or {},
            created_at=r.created_at.isoformat() if r.created_at else None,
            completed_at=r.completed_at.isoformat() if r.completed_at else None,
        )
        for r in runs
    ]


def list_profile_responses(profiles: list[Any]) -> list[SyncProfileResponse]:
    return [SyncProfileResponse.model_validate(p) for p in profiles]
