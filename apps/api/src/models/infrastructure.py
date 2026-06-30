from datetime import datetime

from sqlalchemy import JSON, DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class CacheEntry(Base):
    __tablename__ = "cache_entries"

    key: Mapped[str] = mapped_column(String(512), primary_key=True)
    value_blob: Mapped[str] = mapped_column(Text)
    expires_at: Mapped[float] = mapped_column()


class RateLimitHit(Base):
    __tablename__ = "rate_limit_hits"
    __table_args__ = (Index("ix_rate_limit_client_hit", "client_key", "hit_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_key: Mapped[str] = mapped_column(String(128), index=True)
    hit_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class IntegrationOutbox(Base):
    __tablename__ = "integration_outbox"
    __table_args__ = (Index("ix_outbox_status_created", "status", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    target_url: Mapped[str] = mapped_column(String(512))
    payload: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class CorrelationIngestLog(Base):
    __tablename__ = "correlation_ingest_logs"
    __table_args__ = (
        Index("ix_correlation_ingest_source", "source"),
        Index("ix_correlation_ingest_created", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    alerts: Mapped[list] = mapped_column(JSON, default=list)
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    alert_count: Mapped[int] = mapped_column(Integer, default=0)
    resolved_count: Mapped[int] = mapped_column(Integer, default=0)
    unresolved_count: Mapped[int] = mapped_column(Integer, default=0)
    chain_related: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_entity", "entity_type", "entity_id"),
        Index("ix_audit_created", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(64))
    user_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    old_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
