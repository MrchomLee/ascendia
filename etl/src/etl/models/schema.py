"""SQLAlchemy 2.0 schema for the manuals corpus.

Designed to run on SQLite (MVP) and PostgreSQL (later) without changes.
Uses adjacency-list trees (parent_id) plus a materialized `sort_key` column
for deterministic ordering without recursive CTEs at read time.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Manual(Base):
    __tablename__ = "manuals"
    __table_args__ = (UniqueConstraint("code", "edition", name="uq_manuals_code_edition"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(512))
    edition: Mapped[str | None] = mapped_column(String(64), nullable=True)
    branch: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_path: Mapped[str] = mapped_column(String(1024))
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    extractor_used: Mapped[str] = mapped_column(String(32))
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    nodes: Mapped[list[Node]] = relationship(back_populates="manual", cascade="all, delete-orphan")


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    manual_id: Mapped[int] = mapped_column(ForeignKey("manuals.id", ondelete="CASCADE"), index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("nodes.id", ondelete="CASCADE"), nullable=True, index=True)

    level: Mapped[int] = mapped_column(Integer)
    level_label: Mapped[str] = mapped_column(String(32))
    ordinal: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(1024))
    breadcrumb: Mapped[str] = mapped_column(Text)
    page_start: Mapped[int] = mapped_column(Integer)
    page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sort_key: Mapped[str] = mapped_column(String(64), index=True)
    is_anexo: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    manual: Mapped[Manual] = relationship(back_populates="nodes")
    parent: Mapped[Node | None] = relationship(remote_side="Node.id", back_populates="children")
    children: Mapped[list[Node]] = relationship(back_populates="parent", cascade="all, delete-orphan")
    chunks: Mapped[list[Chunk]] = relationship(back_populates="node", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    node_id: Mapped[int] = mapped_column(ForeignKey("nodes.id", ondelete="CASCADE"), index=True)
    manual_id: Mapped[int] = mapped_column(ForeignKey("manuals.id", ondelete="CASCADE"), index=True)
    ordinal: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    char_count: Mapped[int] = mapped_column(Integer)
    page_start: Mapped[int] = mapped_column(Integer)
    page_end: Mapped[int] = mapped_column(Integer)
    has_table: Mapped[bool] = mapped_column(Boolean, default=False)
    has_image_ref: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    node: Mapped[Node] = relationship(back_populates="chunks")
