"""Maps in-memory pipeline objects (HierarchyTree, ConsolidatedChunk) to ORM rows."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from etl.chunking.consolidator import ConsolidatedChunk
from etl.hierarchy.assembler import HierarchyTree
from etl.models.schema import Chunk, Manual, Node


def persist_manual(
    session: Session,
    *,
    code: str,
    title: str,
    edition: str | None,
    branch: str | None,
    source_path: Path,
    page_count: int,
    extractor_used: str,
    tree: HierarchyTree,
    chunks: list[ConsolidatedChunk],
    extra_metadata: dict | None = None,
) -> Manual:
    """Persist a fully-processed manual.

    The whole transaction commits at session_scope close.
    """
    manual = Manual(
        code=code,
        title=title,
        edition=edition,
        branch=branch,
        source_path=str(source_path),
        page_count=page_count,
        extractor_used=extractor_used,
        ingested_at=datetime.now(timezone.utc),
        metadata_json=extra_metadata or {},
    )
    session.add(manual)
    session.flush()  # need manual.id

    local_to_db: dict[int, int] = {}
    for hn in sorted(tree.nodes, key=lambda n: n.sort_key):
        parent_db_id = (
            local_to_db.get(hn.parent_local_id)
            if hn.parent_local_id is not None
            else None
        )
        node = Node(
            manual_id=manual.id,
            parent_id=parent_db_id,
            level=hn.level,
            level_label=hn.level_label,
            ordinal=hn.ordinal,
            title=hn.title,
            breadcrumb=hn.breadcrumb,
            page_start=hn.page_start,
            page_end=hn.page_end,
            sort_key=hn.sort_key,
            is_anexo=hn.is_anexo,
            metadata_json=hn.metadata,
        )
        session.add(node)
        session.flush()
        local_to_db[hn.local_id] = node.id

    for c in chunks:
        node_db_id = local_to_db.get(c.node_local_id)
        if node_db_id is None:
            continue
        session.add(
            Chunk(
                node_id=node_db_id,
                manual_id=manual.id,
                ordinal=c.ordinal,
                text=c.text,
                char_count=c.char_count,
                page_start=c.page_start,
                page_end=c.page_end,
                has_table=c.has_table,
                has_image_ref=c.has_image_ref,
                metadata_json=c.metadata,
            )
        )
    return manual
