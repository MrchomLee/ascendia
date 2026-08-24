"""Full-text search over chunks using SQLite FTS5.

We create a virtual table `chunks_fts` mirroring `chunks.text` plus enough
metadata to render results without a join. Triggers keep it in sync with
inserts/updates/deletes on `chunks`.

`init_fts` is idempotent — safe to call on every Streamlit page load.
"""

from __future__ import annotations

from pydantic import BaseModel
from sqlalchemy import text

from etl.db.session import session_scope


class SearchHit(BaseModel):
    chunk_id: int
    node_id: int
    manual_id: int
    snippet: str
    rank: float
    page_start: int
    page_end: int


_INIT_SQL = [
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
        text,
        chunk_id UNINDEXED,
        node_id UNINDEXED,
        manual_id UNINDEXED,
        page_start UNINDEXED,
        page_end UNINDEXED,
        tokenize = "unicode61 remove_diacritics 2"
    )
    """,
    """
    CREATE TRIGGER IF NOT EXISTS chunks_fts_insert
    AFTER INSERT ON chunks
    BEGIN
        INSERT INTO chunks_fts(text, chunk_id, node_id, manual_id, page_start, page_end)
        VALUES (NEW.text, NEW.id, NEW.node_id, NEW.manual_id, NEW.page_start, NEW.page_end);
    END
    """,
    """
    CREATE TRIGGER IF NOT EXISTS chunks_fts_delete
    AFTER DELETE ON chunks
    BEGIN
        DELETE FROM chunks_fts WHERE chunk_id = OLD.id;
    END
    """,
    """
    CREATE TRIGGER IF NOT EXISTS chunks_fts_update
    AFTER UPDATE ON chunks
    BEGIN
        DELETE FROM chunks_fts WHERE chunk_id = OLD.id;
        INSERT INTO chunks_fts(text, chunk_id, node_id, manual_id, page_start, page_end)
        VALUES (NEW.text, NEW.id, NEW.node_id, NEW.manual_id, NEW.page_start, NEW.page_end);
    END
    """,
]


def init_fts() -> None:
    """Create FTS5 virtual table + triggers if missing, then backfill any
    chunks that were ingested before FTS existed."""
    with session_scope() as session:
        for stmt in _INIT_SQL:
            session.execute(text(stmt))
        # backfill: only chunks not already in FTS
        session.execute(
            text(
                """
                INSERT INTO chunks_fts(text, chunk_id, node_id, manual_id, page_start, page_end)
                SELECT c.text, c.id, c.node_id, c.manual_id, c.page_start, c.page_end
                FROM chunks c
                WHERE NOT EXISTS (
                    SELECT 1 FROM chunks_fts f WHERE f.chunk_id = c.id
                )
                """
            )
        )


def query(
    q: str,
    *,
    manual_id: int | None = None,
    limit: int = 50,
) -> list[SearchHit]:
    if not q.strip():
        return []
    with session_scope() as session:
        sql = """
            SELECT chunk_id, node_id, manual_id, page_start, page_end,
                   snippet(chunks_fts, 0, '<mark>', '</mark>', '…', 16) AS snippet,
                   bm25(chunks_fts) AS rank
            FROM chunks_fts
            WHERE chunks_fts MATCH :q
        """
        params: dict[str, object] = {"q": _sanitize(q)}
        if manual_id is not None:
            sql += " AND manual_id = :manual_id"
            params["manual_id"] = manual_id
        sql += " ORDER BY rank LIMIT :limit"
        params["limit"] = limit

        rows = session.execute(text(sql), params).all()
        return [
            SearchHit(
                chunk_id=r.chunk_id,
                node_id=r.node_id,
                manual_id=r.manual_id,
                page_start=r.page_start,
                page_end=r.page_end,
                snippet=r.snippet,
                rank=float(r.rank),
            )
            for r in rows
        ]


def _sanitize(q: str) -> str:
    """FTS5 has reserved chars; we wrap free-form input as a phrase if needed."""
    q = q.strip()
    if not q:
        return q
    # if the user provides their own boolean/MATCH syntax (AND/OR/NEAR, quotes), keep it
    if any(token in q for token in (' AND ', ' OR ', ' NEAR(', '"')):
        return q
    # otherwise quote each whitespace-separated token as a phrase to allow accents/punct
    tokens = [t for t in q.split() if t]
    return " ".join(f'"{t}"' for t in tokens)
