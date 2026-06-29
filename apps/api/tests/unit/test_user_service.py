"""AsyncUserWriteService tests."""

import pytest
from src.core.exceptions import ConflictError, DomainValidationError, NotFoundError
from src.schemas.auth import (
    ActiveUpdate,
    ChangePasswordRequest,
    PasswordReset,
    RegisterRequest,
    RoleUpdate,
    UserCreate,
)


@pytest.mark.asyncio
async def test_user_service_uses_injected_repo_for_lookup(user_write_service, admin_user):
    users = await user_write_service._repo.list_ordered()
    emails = {u.email for u in users}
    assert admin_user.email in emails


@pytest.mark.asyncio
async def test_user_service_create_rejects_duplicate(user_write_service, admin_user):
    with pytest.raises(ConflictError, match="exists"):
        await user_write_service.create_user(UserCreate(email=admin_user.email, password="x" * 12, role="viewer"))


@pytest.mark.asyncio
async def test_user_service_register_and_update_role(user_write_service):
    email = "new-user@omnisight.local"
    user = await user_write_service.register(RegisterRequest(email=email, password="password12345"))
    assert user.email == email
    updated = await user_write_service.update_role(email, RoleUpdate(role="editor"))
    assert updated.role == "editor"


@pytest.mark.asyncio
async def test_user_service_reset_password(user_write_service, admin_user):
    result = await user_write_service.reset_password(admin_user.email, PasswordReset(password="newpassword12"))
    assert result["ok"] is True


@pytest.mark.asyncio
async def test_user_service_update_active_not_found(user_write_service, admin_user):
    with pytest.raises(NotFoundError):
        await user_write_service.update_active("missing@omnisight.local", ActiveUpdate(is_active=False), admin_user)


@pytest.mark.asyncio
async def test_user_service_change_password(user_write_service, admin_user):
    await user_write_service.change_password(
        admin_user,
        ChangePasswordRequest(current_password="admin123", new_password="newpassword12"),
    )
    await user_write_service.change_password(
        admin_user,
        ChangePasswordRequest(current_password="newpassword12", new_password="admin123"),
    )


@pytest.mark.asyncio
async def test_user_service_register_conflict(user_write_service, admin_user):
    with pytest.raises(ConflictError, match="already exists"):
        await user_write_service.register(RegisterRequest(email=admin_user.email, password="password12345"))


@pytest.mark.asyncio
async def test_user_service_delete_user(user_write_service, admin_user):
    email = "delete-me@omnisight.local"
    await user_write_service.register(RegisterRequest(email=email, password="password12345"))
    result = await user_write_service.delete_user(email, admin_user)
    assert result["ok"] is True
    assert await user_write_service._repo.get_by_email(email) is None


@pytest.mark.asyncio
async def test_user_service_update_active(user_write_service, admin_user):
    email = "toggle@omnisight.local"
    await user_write_service.register(RegisterRequest(email=email, password="password12345"))
    updated = await user_write_service.update_active(email, ActiveUpdate(is_active=False), admin_user)
    assert updated.is_active is False
    restored = await user_write_service.update_active(email, ActiveUpdate(is_active=True), admin_user)
    assert restored.is_active is True


@pytest.mark.asyncio
async def test_user_service_delete_not_found(user_write_service, admin_user):
    with pytest.raises(NotFoundError):
        await user_write_service.delete_user("nobody@omnisight.local", admin_user)


@pytest.mark.asyncio
async def test_user_service_cannot_delete_self(user_write_service, admin_user):
    with pytest.raises(DomainValidationError, match="yourself"):
        await user_write_service.delete_user(admin_user.email, admin_user)


@pytest.mark.asyncio
async def test_user_service_change_password_invalid(user_write_service, admin_user):
    with pytest.raises(DomainValidationError, match="Invalid"):
        await user_write_service.change_password(
            admin_user,
            ChangePasswordRequest(current_password="wrong", new_password="newpassword12"),
        )


@pytest.mark.asyncio
async def test_user_service_change_password_same_rejected(user_write_service, admin_user):
    with pytest.raises(DomainValidationError, match="differ"):
        await user_write_service.change_password(
            admin_user,
            ChangePasswordRequest(current_password="admin123", new_password="admin123"),
        )


@pytest.mark.asyncio
async def test_user_service_update_role_not_found(user_write_service):
    with pytest.raises(NotFoundError):
        await user_write_service.update_role("missing@omnisight.local", RoleUpdate(role="viewer"))


@pytest.mark.asyncio
async def test_user_service_reset_password_not_found(user_write_service):
    with pytest.raises(NotFoundError):
        await user_write_service.reset_password("missing@omnisight.local", PasswordReset(password="newpassword12"))


@pytest.mark.asyncio
async def test_user_service_cannot_deactivate_self(user_write_service, admin_user):
    with pytest.raises(DomainValidationError, match="yourself"):
        await user_write_service.update_active(admin_user.email, ActiveUpdate(is_active=False), admin_user)


@pytest.mark.asyncio
async def test_user_service_cannot_deactivate_last_admin(user_write_service, admin_user, monkeypatch):
    other = await user_write_service.create_user(
        UserCreate(email="second-admin@omnisight.local", password="x" * 12, role="admin")
    )

    async def _one_admin():
        return 1

    monkeypatch.setattr(user_write_service._repo, "count_admins", _one_admin)
    with pytest.raises(DomainValidationError, match="last active admin"):
        await user_write_service.update_active(other.email, ActiveUpdate(is_active=False), admin_user)


@pytest.mark.asyncio
async def test_user_service_cannot_delete_last_admin(user_write_service, admin_user, monkeypatch):
    other_email = "deletable-admin@omnisight.local"
    await user_write_service.create_user(UserCreate(email=other_email, password="x" * 12, role="admin"))

    async def _one_admin():
        return 1

    monkeypatch.setattr(user_write_service._repo, "count_admins", _one_admin)
    with pytest.raises(DomainValidationError, match="last active admin"):
        await user_write_service.delete_user(other_email, admin_user)
