from datetime import UTC, datetime, timedelta
from typing import Annotated

import bcrypt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from src.core.auth_lookup import get_user_by_email
from src.core.config import settings
from src.models import User

INTEGRATION_EMAIL = "integration@omnisight.local"

bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
webhook_secret_header = APIKeyHeader(name="X-Webhook-Secret", auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(email: str, role: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": email, "role": role, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


async def _resolve_user_from_token(token: str | None) -> User | None:
    if not token:
        return None
    payload = decode_token(token)
    email = payload.get("sub")
    if not email:
        return None
    user = await get_user_by_email(email)
    if not user or not user.is_active:
        return None
    return user


async def get_current_user_optional(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(bearer_scheme)] = None,
    api_key: Annotated[str | None, Security(api_key_header)] = None,
    webhook_secret: Annotated[str | None, Security(webhook_secret_header)] = None,
) -> User | None:
    if api_key and api_key == settings.api_key:
        integration = await get_user_by_email(settings.integration_user_email)
        if integration:
            return integration
    if webhook_secret and webhook_secret == settings.webhook_secret:
        integration = await get_user_by_email(settings.integration_user_email)
        if integration:
            return integration
    token = credentials.credentials if credentials else None
    return await _resolve_user_from_token(token)


def get_current_user(user: Annotated[User | None, Depends(get_current_user_optional)]) -> User:
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


def require_roles(*roles: str):
    def checker(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return checker


require_viewer = require_roles("viewer", "editor", "admin")
require_editor = require_roles("editor", "admin")
require_admin = require_roles("admin")
