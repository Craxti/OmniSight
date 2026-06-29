from typing import Annotated

from fastapi import APIRouter, Depends
from src.api.handlers.auth import (
    handle_change_password,
    handle_create_user,
    handle_delete_user,
    handle_issue_token,
    handle_list_users,
    handle_me,
    handle_register,
    handle_reset_password,
    handle_update_active,
    handle_update_role,
)
from src.core.auth import get_current_user, require_admin
from src.core.deps import get_user_read_port, get_user_write_port
from src.core.openapi_tags import TAG_ADMIN_AUTH
from src.models import User
from src.schemas.auth import (
    ActiveUpdate,
    ChangePasswordRequest,
    LoginRequest,
    PasswordReset,
    RegisterRequest,
    RoleUpdate,
    UserCreate,
)
from src.services.async_read.users import AsyncUserReadService
from src.services.async_write.users import AsyncUserWriteService

router = APIRouter(prefix="/auth", tags=[TAG_ADMIN_AUTH])

UserSvc = Annotated[AsyncUserWriteService, Depends(get_user_write_port)]
UserReadSvc = Annotated[AsyncUserReadService, Depends(get_user_read_port)]

_TOKEN_DESC = (
    "Возвращает JWT (`access_token`) в поле `session` для заголовка `Authorization: Bearer <token>`. "
    "В Swagger: кнопка **Authorize** → вставьте значение `access_token` (без слова Bearer). "
    "Демо-учётка: `admin@omnisight.local` / `admin123`."
)


@router.post("/login", summary="Вход (JWT)")
async def login_v1(body: LoginRequest, service: UserSvc):
    return await handle_issue_token(body, service)


@router.post("/token", summary="Получить JWT для Swagger и API", description=_TOKEN_DESC)
async def issue_token_v1(body: LoginRequest, service: UserSvc):
    return await handle_issue_token(body, service)


@router.post("/register")
async def register_v1(body: RegisterRequest, service: UserSvc):
    return await handle_register(body, service)


@router.get("/me")
async def me_v1(user: Annotated[User, Depends(get_current_user)]):
    return await handle_me(user)


@router.post("/change-password")
async def change_password_v1(
    body: ChangePasswordRequest,
    service: UserSvc,
    user: Annotated[User, Depends(get_current_user)],
):
    return await handle_change_password(service, user, body)


@router.get("/users")
async def list_users_v1(service: UserReadSvc, _: Annotated[User, Depends(require_admin)]):
    return await handle_list_users(service)


@router.post("/users")
async def create_user_v1(
    body: UserCreate,
    service: UserSvc,
    _: Annotated[User, Depends(require_admin)],
):
    return await handle_create_user(service, body)


@router.patch("/users/{email}/role")
async def update_role_v1(
    email: str,
    body: RoleUpdate,
    service: UserSvc,
    _: Annotated[User, Depends(require_admin)],
):
    return await handle_update_role(service, email, body)


@router.patch("/users/{email}/active")
async def update_active_v1(
    email: str,
    body: ActiveUpdate,
    service: UserSvc,
    admin: Annotated[User, Depends(require_admin)],
):
    return await handle_update_active(service, email, body, admin)


@router.delete("/users/{email}")
async def delete_user_v1(
    email: str,
    service: UserSvc,
    admin: Annotated[User, Depends(require_admin)],
):
    return await handle_delete_user(service, email, admin)


@router.post("/users/{email}/reset-password")
async def reset_password_v1(
    email: str,
    body: PasswordReset,
    service: UserSvc,
    _: Annotated[User, Depends(require_admin)],
):
    return await handle_reset_password(service, email, body)
