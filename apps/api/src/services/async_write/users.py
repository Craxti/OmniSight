"""Native async user administration and authentication writes."""

from __future__ import annotations

from src.core.async_repository_bundle import AsyncRepositoryBundle
from src.core.auth import create_access_token, hash_password, verify_password
from src.core.exceptions import ConflictError, DomainValidationError, NotFoundError
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
    UserResponse,
)
from src.services.base.async_domain import AsyncDomainService
from src.services.domain.users import user_response


class AsyncUserWriteService(AsyncDomainService):
    def __init__(self, bundle: AsyncRepositoryBundle) -> None:
        super().__init__(bundle)
        self._repo = bundle.users

    async def authenticate(self, email: str, password: str) -> User | None:
        user = await self._repo.get_by_email(email)
        if not user or not user.is_active or not verify_password(password, user.hashed_password):
            return None
        return user

    async def issue_token(self, body: LoginRequest) -> TokenResponse:
        user = await self.authenticate(body.email, body.password)
        if not user:
            raise DomainValidationError("Invalid credentials")
        return TokenResponse(
            access_token=create_access_token(user.email, user.role),
            must_change_password=user.must_change_password,
        )

    async def _require_by_email(self, email: str) -> User:
        user = await self._repo.get_by_email(email)
        if not user:
            raise NotFoundError("User not found")
        return user

    async def register(self, body: RegisterRequest) -> User:
        if await self._repo.get_by_email(body.email):
            raise ConflictError("User already exists")
        is_first = await self._repo.count_all() == 0
        user = User(
            email=body.email,
            hashed_password=hash_password(body.password),
            role="admin" if is_first else "viewer",
        )
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def change_password(self, user: User, body: ChangePasswordRequest) -> None:
        db_user = await self._require_by_email(user.email)
        if not verify_password(body.current_password, db_user.hashed_password):
            raise DomainValidationError("Invalid current password")
        if body.current_password == body.new_password:
            raise DomainValidationError("New password must differ")
        db_user.hashed_password = hash_password(body.new_password)
        db_user.must_change_password = False
        await self._session.commit()

    async def create_user(self, body: UserCreate) -> UserResponse:
        if await self._repo.get_by_email(body.email):
            raise ConflictError("User exists")
        user = User(
            email=body.email,
            hashed_password=hash_password(body.password),
            role=body.role,
            must_change_password=True,
        )
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user_response(user)

    async def update_role(self, email: str, body: RoleUpdate) -> UserResponse:
        user = await self._require_by_email(email)
        user.role = body.role
        await self._session.commit()
        await self._session.refresh(user)
        return user_response(user)

    async def update_active(self, email: str, body: ActiveUpdate, admin: User) -> UserResponse:
        user = await self._require_by_email(email)
        if user.email == admin.email and not body.is_active:
            raise DomainValidationError("Cannot deactivate yourself")
        if user.role == "admin" and user.is_active and not body.is_active and await self._repo.count_admins() <= 1:
            raise DomainValidationError("Cannot deactivate the last active admin")
        user.is_active = body.is_active
        await self._session.commit()
        await self._session.refresh(user)
        return user_response(user)

    async def delete_user(self, email: str, admin: User) -> dict:
        user = await self._require_by_email(email)
        if user.email == admin.email:
            raise DomainValidationError("Cannot delete yourself")
        if user.role == "admin" and await self._repo.count_admins() <= 1:
            raise DomainValidationError("Cannot delete the last active admin")
        await self._session.delete(user)
        await self._session.commit()
        return {"ok": True}

    async def reset_password(self, email: str, body: PasswordReset) -> dict:
        user = await self._require_by_email(email)
        user.hashed_password = hash_password(body.password)
        user.must_change_password = True
        await self._session.commit()
        return {"ok": True}
