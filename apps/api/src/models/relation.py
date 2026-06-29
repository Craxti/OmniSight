from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.ci import CI


class Relation(Base):
    __tablename__ = "relations"
    __table_args__ = (Index("ix_relations_src_tgt_type", "source_ci_id", "target_ci_id", "relation_type"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_ci_id: Mapped[int] = mapped_column(ForeignKey("cis.id"), index=True)
    target_ci_id: Mapped[int] = mapped_column(ForeignKey("cis.id"), index=True)
    relation_type: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(64), default="active")
    data_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    source_ci: Mapped["CI"] = relationship(back_populates="outgoing_relations", foreign_keys=[source_ci_id])
    target_ci: Mapped["CI"] = relationship(back_populates="incoming_relations", foreign_keys=[target_ci_id])
