import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, func, select, text
from sqlalchemy.exc import DBAPIError, OperationalError
from src.core.database_async import async_write_session
from src.models import RateLimitHit

logger = logging.getLogger("omnisight.api")


async def _allow_postgres_async(session, client_key: str, max_requests: int, window_seconds: int) -> bool:
    locked = await session.scalar(
        text("SELECT pg_try_advisory_xact_lock(hashtext(:client_key))"),
        {"client_key": client_key},
    )
    if not locked:
        return True

    cutoff = datetime.now(UTC) - timedelta(seconds=window_seconds)
    await session.execute(delete(RateLimitHit).where(RateLimitHit.hit_at < cutoff))
    count = await session.scalar(
        select(func.count(RateLimitHit.id)).where(
            RateLimitHit.client_key == client_key,
            RateLimitHit.hit_at >= cutoff,
        )
    )
    if int(count or 0) >= max_requests:
        return False
    session.add(RateLimitHit(client_key=client_key))
    return True


async def allow_request(client_key: str, max_requests: int, window_seconds: int) -> bool:
    try:
        async with async_write_session() as session:
            async with session.begin():
                return await _allow_postgres_async(session, client_key, max_requests, window_seconds)
    except (TimeoutError, OperationalError, DBAPIError) as exc:
        logger.warning("rate_limit_unavailable: %s", exc)
        return True
