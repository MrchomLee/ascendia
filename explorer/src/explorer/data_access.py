"""Read-only data access for the Streamlit explorer.

All functions open and close their own session to avoid detached-instance
issues with Streamlit's caching. Returns are Pydantic models (serializable,
hashable) so `@st.cache_data` works.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from etl.db.session import session_scope
from etl.extraction.types import ExtractionResult
from etl.models.schema import Chunk, Manual, Node
from etl.quality.report import QualityReport, build_report


class ManualSummary(BaseModel):
    id: int
    code: str
    title: str
    branch: str | None
    extractor_used: str
    page_count: int
    node_count: int
    chunk_count: int
    ingested_at: datetime


class ManualDetail(BaseModel):
    id: int
    code: str
    title: str
    edition: str | None
    branch: str | None
    source_path: str
    page_count: int
    extractor_used: str
    ingested_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class NodeSummary(BaseModel):
    id: int
    manual_id: int
    parent_id: int | None
    level: int
    level_label: str
    ordinal: str
    title: str
    breadcrumb: str
    page_start: int
    page_end: int | None
    sort_key: str
    is_anexo: bool
    chunk_count: int = 0


class ChunkSummary(BaseModel):
    id: int
    node_id: int
    manual_id: int
    ordinal: int
    text: str
    char_count: int
    page_start: int
    page_end: int
    has_table: bool
    has_image_ref: bool


class GlobalKPIs(BaseModel):
    manual_count: int
    node_count: int
    chunk_count: int
    last_ingested_at: datetime | None


@st.cache_data(ttl=30, show_spinner=False)
def list_manuals() -> list[ManualSummary]:
    with session_scope() as session:
        node_counts = dict(
            session.execute(
                select(Node.manual_id, func.count(Node.id)).group_by(Node.manual_id)
            ).all()
        )
        chunk_counts = dict(
            session.execute(
                select(Chunk.manual_id, func.count(Chunk.id)).group_by(Chunk.manual_id)
            ).all()
        )
        rows = session.execute(select(Manual).order_by(Manual.id)).scalars().all()
        return [
            ManualSummary(
                id=m.id,
                code=m.code,
                title=m.title,
                branch=m.branch,
                extractor_used=m.extractor_used,
                page_count=m.page_count,
                node_count=node_counts.get(m.id, 0),
                chunk_count=chunk_counts.get(m.id, 0),
                ingested_at=m.ingested_at,
            )
            for m in rows
        ]


@st.cache_data(ttl=30, show_spinner=False)
def get_global_kpis() -> GlobalKPIs:
    with session_scope() as session:
        manual_count = session.execute(select(func.count(Manual.id))).scalar_one()
        node_count = session.execute(select(func.count(Node.id))).scalar_one()
        chunk_count = session.execute(select(func.count(Chunk.id))).scalar_one()
        last = session.execute(
            select(Manual.ingested_at).order_by(Manual.ingested_at.desc()).limit(1)
        ).scalar_one_or_none()
        return GlobalKPIs(
            manual_count=manual_count,
            node_count=node_count,
            chunk_count=chunk_count,
            last_ingested_at=last,
        )


@st.cache_data(ttl=30, show_spinner=False)
def get_manual(manual_id: int) -> ManualDetail | None:
    with session_scope() as session:
        m = session.get(Manual, manual_id)
        if m is None:
            return None
        return ManualDetail(
            id=m.id,
            code=m.code,
            title=m.title,
            edition=m.edition,
            branch=m.branch,
            source_path=m.source_path,
            page_count=m.page_count,
            extractor_used=m.extractor_used,
            ingested_at=m.ingested_at,
            metadata=m.metadata_json or {},
        )


@st.cache_data(ttl=30, show_spinner=False)
def get_tree(manual_id: int) -> list[NodeSummary]:
    with session_scope() as session:
        chunk_counts = dict(
            session.execute(
                select(Chunk.node_id, func.count(Chunk.id))
                .where(Chunk.manual_id == manual_id)
                .group_by(Chunk.node_id)
            ).all()
        )
        rows = (
            session.execute(
                select(Node).where(Node.manual_id == manual_id).order_by(Node.sort_key)
            )
            .scalars()
            .all()
        )
        return [
            NodeSummary(
                id=n.id,
                manual_id=n.manual_id,
                parent_id=n.parent_id,
                level=n.level,
                level_label=n.level_label,
                ordinal=n.ordinal,
                title=n.title,
                breadcrumb=n.breadcrumb,
                page_start=n.page_start,
                page_end=n.page_end,
                sort_key=n.sort_key,
                is_anexo=n.is_anexo,
                chunk_count=chunk_counts.get(n.id, 0),
            )
            for n in rows
        ]


@st.cache_data(ttl=30, show_spinner=False)
def get_node(node_id: int) -> NodeSummary | None:
    with session_scope() as session:
        n = session.get(Node, node_id)
        if n is None:
            return None
        chunk_count = session.execute(
            select(func.count(Chunk.id)).where(Chunk.node_id == node_id)
        ).scalar_one()
        return NodeSummary(
            id=n.id,
            manual_id=n.manual_id,
            parent_id=n.parent_id,
            level=n.level,
            level_label=n.level_label,
            ordinal=n.ordinal,
            title=n.title,
            breadcrumb=n.breadcrumb,
            page_start=n.page_start,
            page_end=n.page_end,
            sort_key=n.sort_key,
            is_anexo=n.is_anexo,
            chunk_count=chunk_count,
        )


@st.cache_data(ttl=30, show_spinner=False)
def get_chunks_for_node(node_id: int) -> list[ChunkSummary]:
    with session_scope() as session:
        rows = (
            session.execute(
                select(Chunk).where(Chunk.node_id == node_id).order_by(Chunk.ordinal)
            )
            .scalars()
            .all()
        )
        return [_chunk_to_summary(c) for c in rows]


@st.cache_data(ttl=30, show_spinner=False)
def get_chunks_for_manual(
    manual_id: int, *, limit: int = 1000, offset: int = 0
) -> list[ChunkSummary]:
    with session_scope() as session:
        rows = (
            session.execute(
                select(Chunk)
                .where(Chunk.manual_id == manual_id)
                .order_by(Chunk.id)
                .limit(limit)
                .offset(offset)
            )
            .scalars()
            .all()
        )
        return [_chunk_to_summary(c) for c in rows]


def _chunk_to_summary(c: Chunk) -> ChunkSummary:
    return ChunkSummary(
        id=c.id,
        node_id=c.node_id,
        manual_id=c.manual_id,
        ordinal=c.ordinal,
        text=c.text,
        char_count=c.char_count,
        page_start=c.page_start,
        page_end=c.page_end,
        has_table=c.has_table,
        has_image_ref=c.has_image_ref,
    )


@st.cache_data(ttl=30, show_spinner=False)
def get_quality_report_dict(manual_id: int) -> dict[str, Any] | None:
    """Returns the QualityReport as a plain dict (cache-friendly)."""
    with session_scope() as session:
        try:
            report: QualityReport = build_report(session, manual_id)
        except ValueError:
            return None
        return report.model_dump()


@st.cache_data(ttl=300, show_spinner=False)
def get_extraction_cache(manual_id: int, processed_dir_str: str) -> dict | None:
    """Reads `data/processed/<code>.<extractor>.json` for a manual.

    Returns the raw dict (not deserialized to ExtractionResult) so it stays
    cache-serializable. Caller can pass it back through model_validate.
    """
    detail = get_manual(manual_id)
    if detail is None:
        return None
    candidate_stem = Path(detail.source_path).stem
    processed_dir = Path(processed_dir_str)
    candidates = list(processed_dir.glob(f"{candidate_stem}*.json"))
    if not candidates:
        candidates = list(processed_dir.glob(f"*{detail.code.replace(' ', '*')}*.json"))
    if not candidates:
        return None
    chosen = sorted(candidates)[0]
    try:
        return json.loads(chosen.read_text(encoding="utf-8"))
    except Exception:
        return None


def deserialize_extraction(raw: dict) -> ExtractionResult:
    return ExtractionResult.model_validate(raw)


def get_node_siblings(node: NodeSummary) -> list[NodeSummary]:
    """Siblings = nodes sharing the same parent_id (or root nodes if parent is None)."""
    tree = get_tree(node.manual_id)
    return [n for n in tree if n.parent_id == node.parent_id and n.id != node.id]


def get_node_children(node: NodeSummary) -> list[NodeSummary]:
    tree = get_tree(node.manual_id)
    return [n for n in tree if n.parent_id == node.id]


def get_node_ancestors(node: NodeSummary) -> list[NodeSummary]:
    tree = get_tree(node.manual_id)
    by_id = {n.id: n for n in tree}
    chain: list[NodeSummary] = []
    current = by_id.get(node.parent_id) if node.parent_id else None
    while current is not None:
        chain.append(current)
        current = by_id.get(current.parent_id) if current.parent_id else None
    return list(reversed(chain))
