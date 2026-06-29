from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class SyncConnector(Base):
    __tablename__ = "sync_connectors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    connector_type: Mapped[str] = mapped_column(String(32), index=True)
    server_ci_id: Mapped[int | None] = mapped_column(ForeignKey("cis.id"), nullable=True, index=True)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    credentials: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=30)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    read_only: Mapped[bool] = mapped_column(Boolean, default=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_sync: Mapped[bool] = mapped_column(Boolean, default=False)
    schema_version: Mapped[str] = mapped_column(String(32), default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class SyncProfile(Base):
    __tablename__ = "sync_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    connector_ids: Mapped[list] = mapped_column(JSON, default=list)
    source_types: Mapped[list] = mapped_column(JSON, default=list)
    scope_mode: Mapped[str] = mapped_column(String(32), default="graph")
    scope_config: Mapped[dict] = mapped_column(JSON, default=dict)
    mapping_rules: Mapped[dict] = mapped_column(JSON, default=dict)
    auto_apply_threshold: Mapped[float] = mapped_column(Float, default=0.85)
    schema_version: Mapped[str] = mapped_column(String(32), default="1")
    last_run_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class AutodiscoverRun(Base):
    __tablename__ = "autodiscover_runs"
    __table_args__ = (Index("ix_autodiscover_runs_profile_created", "profile_id", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("sync_profiles.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="draft", index=True)
    user_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    request_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    report: Mapped[dict] = mapped_column(JSON, default=dict)
    discovered_schema: Mapped[dict] = mapped_column(JSON, default=dict)
    previous_schema: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    schema_diff: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    mappings: Mapped[list["AutodiscoverMapping"]] = relationship(back_populates="run")


class AutodiscoverMapping(Base):
    __tablename__ = "autodiscover_mappings"
    __table_args__ = (Index("ix_autodiscover_mappings_run", "run_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("autodiscover_runs.id"), index=True)
    mapping_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    mapping_kind: Mapped[str] = mapped_column(String(32), default="field", index=True)
    ci_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    ci_name: Mapped[str] = mapped_column(String(255))
    target_ci_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    target_ci_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    relation_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    field: Mapped[str] = mapped_column(String(128))
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    current_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    discovered_value: Mapped[str] = mapped_column(Text)
    source_server: Mapped[str] = mapped_column(String(255), default="")
    source_connector: Mapped[str] = mapped_column(String(128), default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(32), default="needs_confirmation")
    selected: Mapped[bool] = mapped_column(Boolean, default=False)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    run: Mapped["AutodiscoverRun"] = relationship(back_populates="mappings")
