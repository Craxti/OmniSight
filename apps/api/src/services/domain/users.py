"""Shared user list read serializers."""

from __future__ import annotations

from typing import Any

from src.schemas.auth import UserResponse


def user_response(user: Any) -> UserResponse:
    return UserResponse(
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        must_change_password=user.must_change_password,
    )


def list_user_responses(users: list[Any]) -> list[UserResponse]:
    return [user_response(u) for u in users]
