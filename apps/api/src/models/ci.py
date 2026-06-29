from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, Integer, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.relation import Relation


class CIType(Base):
    __tablename__ = "ci_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    attribute_schema: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_official: Mapped[bool] = mapped_column(Boolean, default=True)
    is_import_draft: Mapped[bool] = mapped_column(Boolean, default=False)

    cis: Mapped[list["CI"]] = relationship(back_populates="ci_type")


class CI(Base):
    __tablename__ = "cis"
    __table_args__ = (
        Index("ix_cis_env_status", "environment", "status"),
        Index("ix_cis_owner_name", "owner", "name"),
        Index("ix_cis_search_hostname", "search_hostname"),
        Index("ix_cis_search_ip", "search_ip"),
        Index("ix_cis_search_service_code", "search_service_code"),
        Index("ix_cis_search_external_id", "search_external_id"),
        Index(
            "uq_cis_name_active",
            "name",
            unique=True,
            postgresql_where=text("is_deleted = false"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    type_id: Mapped[int] = mapped_column(ForeignKey("ci_types.id"))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(64), default="active", index=True)
    criticality: Mapped[str | None] = mapped_column(String(32), nullable=True)
    environment: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    team: Mapped[str | None] = mapped_column(String(255), nullable=True)
    attributes: Mapped[dict | None] = mapped_column(JSON, default=dict)
    external_ids: Mapped[dict | None] = mapped_column(JSON, default=dict)
    search_hostname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    search_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    search_service_code: Mapped[str | None] = mapped_column(String(128), nullable=True)
    search_application_code: Mapped[str | None] = mapped_column(String(128), nullable=True)
    search_external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    ci_type: Mapped["CIType"] = relationship(back_populates="cis")
    outgoing_relations: Mapped[list["Relation"]] = relationship(
        back_populates="source_ci",
        foreign_keys="Relation.source_ci_id",
    )
    incoming_relations: Mapped[list["Relation"]] = relationship(
        back_populates="target_ci",
        foreign_keys="Relation.target_ci_id",
    )
