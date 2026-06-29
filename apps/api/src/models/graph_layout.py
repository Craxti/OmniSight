from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class GraphLayout(Base):
    __tablename__ = "graph_layouts"
    __table_args__ = (UniqueConstraint("root_ci_id", "relation_filter", name="uq_graph_layout_root_filter"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    root_ci_id: Mapped[int] = mapped_column(ForeignKey("cis.id", ondelete="CASCADE"), index=True)
    relation_filter: Mapped[str] = mapped_column(String(64), default="*")
    positions: Mapped[dict] = mapped_column(JSON, default=dict)
    updated_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
