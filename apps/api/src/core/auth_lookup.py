"""Load users for JWT / API-key auth on the async read pool."""

from __future__ import annotations

from src.core import database_async
from src.models import User
from src.repositories.async_orm.user_repository import AsyncUserRepository


async def get_user_by_email(email: str) -> User | None:
    async with database_async.async_read_session() as session:
        return await AsyncUserRepository(session).get_by_email(email)
