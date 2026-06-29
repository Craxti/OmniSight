"""Auth HTTP handlers (v1 envelopes)."""

from __future__ import annotations

from fastapi import HTTPException, status
from src.api.handlers.v1_envelopes import (
    auth_items_v1_envelope,
    auth_result_v1_envelope,
    session_v1_envelope,
    user_v1_envelope,
)
from src.core.auth import create_access_token
from src.core.exceptions import DomainValidationError
from src.models import User
from src.schemas.auth import (
    ActiveUpdate,
    ChangePasswordRequest,
    LoginRequest,
    PasswordReset,
    RegisterRequest,
    RoleUpdate,
    TokenResponse,
    UserCreate,
)
from src.services.async_read.users import AsyncUserReadService
from src.services.async_write.users import AsyncUserWriteService
from src.services.domain.users import user_response


async def handle_issue_token(body: LoginRequest, service: AsyncUserWriteService):
    try:
        token = await service.issue_token(body)
    except DomainValidationError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials") from None
    return session_v1_envelope(token)


async def handle_register(body: RegisterRequest, service: AsyncUserWriteService):
    user = await service.register(body)
    token = TokenResponse(
        access_token=create_access_token(user.email, user.role),
        must_change_password=user.must_change_password,
    )
    return session_v1_envelope(token)


async def handle_me(user: User):
    return user_v1_envelope(user_response(user))


async def handle_change_password(service: AsyncUserWriteService, user: User, body: ChangePasswordRequest):
    await service.change_password(user, body)
    return auth_result_v1_envelope()


async def handle_list_users(service: AsyncUserReadService):
    items = await service.list_users()
    return auth_items_v1_envelope(items)


async def handle_create_user(service: AsyncUserWriteService, body: UserCreate):
    result = await service.create_user(body)
    return user_v1_envelope(result)


async def handle_update_role(service: AsyncUserWriteService, email: str, body: RoleUpdate):
    result = await service.update_role(email, body)
    return user_v1_envelope(result)


async def handle_update_active(service: AsyncUserWriteService, email: str, body: ActiveUpdate, admin: User):
    result = await service.update_active(email, body, admin)
    return user_v1_envelope(result)


async def handle_delete_user(service: AsyncUserWriteService, email: str, admin: User):
    result = await service.delete_user(email, admin)
    return auth_result_v1_envelope(result)


async def handle_reset_password(service: AsyncUserWriteService, email: str, body: PasswordReset):
    result = await service.reset_password(email, body)
    return auth_result_v1_envelope(result)
