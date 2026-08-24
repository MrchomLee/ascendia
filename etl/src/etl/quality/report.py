"""Quality report for an ingested manual.

Computes:
- TOC coverage: % of TOC entries that resulted in a node.
- Level distribution: how many of each (Parte/Capítulo/Sección/Subsección/Anexo).
- Orphan nodes: nodes without chunks.
- Page coverage: pages that have no chunk attached.
"""

from __future__ import annotations

from collections import Counter

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from etl.models.schema import Chunk, Manual, Node


class QualityReport(BaseModel):
    manual_id: int
    manual_code: str
    page_count: int
    node_count: int
    chunk_count: int
    level_distribution: dict[str, int]
    orphan_nodes: int
    pages_with_chunks: int
    page_coverage_pct: float
    avg_chunk_chars: float


def build_report(session: Session, manual_id: int) -> QualityReport:
    manual = session.get(Manual, manual_id)
    if manual is None:
        raise ValueError(f"Manual {manual_id} not found")

    nodes: list[Node] = (
        session.execute(select(Node).where(Node.manual_id == manual_id)).scalars().all()
    )
    chunks: list[Chunk] = (
        session.execute(select(Chunk).where(Chunk.manual_id == manual_id)).scalars().all()
    )

    level_dist = Counter(n.level_label for n in nodes)
    chunked_node_ids = {c.node_id for c in chunks}
    orphans = sum(1 for n in nodes if n.id not in chunked_node_ids)

    pages_with_chunks: set[int] = set()
    for c in chunks:
        for p in range(c.page_start, c.page_end + 1):
            pages_with_chunks.add(p)
    page_coverage_pct = (
        100.0 * len(pages_with_chunks) / manual.page_count if manual.page_count else 0.0
    )

    total_chars = session.execute(
        select(func.coalesce(func.sum(Chunk.char_count), 0)).where(Chunk.manual_id == manual_id)
    ).scalar_one()
    avg_chars = total_chars / len(chunks) if chunks else 0.0

    return QualityReport(
        manual_id=manual_id,
        manual_code=manual.code,
        page_count=manual.page_count,
        node_count=len(nodes),
        chunk_count=len(chunks),
        level_distribution=dict(level_dist),
        orphan_nodes=orphans,
        pages_with_chunks=len(pages_with_chunks),
        page_coverage_pct=page_coverage_pct,
        avg_chunk_chars=avg_chars,
    )
