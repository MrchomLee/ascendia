from __future__ import annotations

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from sqlalchemy import select

from etl.db.session import session_scope
from etl.models.schema import Chunk, Manual, Node

load_dotenv()
app = typer.Typer(help="Inspect a populated manuals.sqlite database.")
console = Console()


@app.command()
def manuals() -> None:
    """List every ingested manual."""
    with session_scope() as session:
        rows = session.execute(select(Manual).order_by(Manual.id)).scalars().all()
        if not rows:
            console.print("[yellow]No manuals ingested yet.[/]")
            return
        table = Table(title="Manuals")
        for col in ("id", "code", "title", "extractor", "pages", "ingested_at"):
            table.add_column(col)
        for m in rows:
            table.add_row(
                str(m.id),
                m.code,
                m.title,
                m.extractor_used,
                str(m.page_count),
                m.ingested_at.isoformat(timespec="seconds"),
            )
        console.print(table)


@app.command()
def tree(manual_id: int) -> None:
    """Print the hierarchy of a manual as a tree."""
    with session_scope() as session:
        manual = session.get(Manual, manual_id)
        if manual is None:
            console.print(f"[red]Manual {manual_id} not found.[/]")
            raise typer.Exit(1)
        nodes = (
            session.execute(
                select(Node).where(Node.manual_id == manual_id).order_by(Node.sort_key)
            )
            .scalars()
            .all()
        )
        rich_tree = Tree(f"[bold]{manual.code}[/] — {manual.title}")
        rich_by_id: dict[int, Tree] = {}
        for n in nodes:
            label = f"[cyan]{n.level_label} {n.ordinal}[/] {n.title}  [dim](p.{n.page_start}-{n.page_end or n.page_start})[/]"
            parent_view = rich_by_id.get(n.parent_id) if n.parent_id else rich_tree
            rich_by_id[n.id] = (parent_view or rich_tree).add(label)
        console.print(rich_tree)


@app.command()
def node(node_id: int) -> None:
    """Show a node's breadcrumb plus its chunks (truncated)."""
    with session_scope() as session:
        n = session.get(Node, node_id)
        if n is None:
            console.print(f"[red]Node {node_id} not found.[/]")
            raise typer.Exit(1)
        console.print(f"[bold]{n.breadcrumb}[/]")
        console.print(f"Pages {n.page_start}-{n.page_end or n.page_start}")
        chunks = (
            session.execute(
                select(Chunk).where(Chunk.node_id == node_id).order_by(Chunk.ordinal)
            )
            .scalars()
            .all()
        )
        for c in chunks:
            preview = c.text[:400] + ("…" if len(c.text) > 400 else "")
            console.print(f"\n[dim]chunk {c.ordinal} — {c.char_count} chars, p.{c.page_start}-{c.page_end}[/]")
            console.print(preview)


if __name__ == "__main__":
    app()
