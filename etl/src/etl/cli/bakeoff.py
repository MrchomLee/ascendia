from __future__ import annotations

from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from etl.pipeline import run_pipeline

load_dotenv()
app = typer.Typer(help="Run Docling and Unstructured on the same PDF and compare.")
console = Console()


@app.command()
def main(
    pdf: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    out: Path = typer.Option(Path("bakeoff_report.md"), help="Where to write the markdown report."),
    skip_unstructured: bool = typer.Option(
        False,
        "--skip-unstructured",
        help="Useful while Unstructured cannot install on Python 3.14.",
    ),
    ocr: bool = typer.Option(
        False,
        "--ocr",
        help="Enable OCR. Default OFF — assumes the PDF has a native text layer (much faster, much less RAM).",
    ),
    profile: str | None = typer.Option(
        None,
        "--profile",
        help="DocumentProfile: manual | codigo_legal | ley_organica. Default: auto-detect.",
    ),
) -> None:
    """Run both extractors with persistence disabled and emit a comparison."""
    results: dict[str, dict] = {}

    for name in ("docling",) + (() if skip_unstructured else ("unstructured",)):
        console.print(
            f"[bold cyan]Running {name}... (ocr={ocr}, profile={profile or 'auto'})[/]"
        )
        try:
            summary, extraction, tree, chunks = run_pipeline(
                pdf,
                extractor_name=name,  # type: ignore[arg-type]
                persist=False,
                use_cache=True,
                do_ocr=ocr,
                profile=profile,
            )
            results[name] = {
                "summary": summary.model_dump(),
                "element_count": len(extraction.elements),
                "title_count": sum(
                    1 for e in extraction.elements if e.kind.value in {"title", "heading"}
                ),
                "table_count": sum(1 for e in extraction.elements if e.kind.value == "table"),
                "leaf_count": sum(
                    1
                    for n in tree.nodes
                    if not any(c.parent_local_id == n.local_id for c in tree.nodes)
                ),
                "chunks": len(chunks),
                "error": None,
            }
        except Exception as exc:
            results[name] = {"error": f"{type(exc).__name__}: {exc}"}

    _print_table(results)
    out.write_text(_render_markdown(pdf, results), encoding="utf-8")
    console.print(f"[green]Report written to[/] {out}")


def _print_table(results: dict[str, dict]) -> None:
    table = Table(title="Bake-off summary")
    table.add_column("Metric")
    for name in results:
        table.add_column(name)

    metrics = [
        "page_count",
        "elapsed_seconds",
        "profile",
        "profile_auto_detected",
        "toc_found",
        "toc_entries",
        "node_count",
        "chunk_count",
        "unattached_elements",
        "dropped_elements",
    ]
    for m in metrics:
        row = [m]
        for name in results:
            r = results[name]
            if r.get("error"):
                row.append("[red]error[/]")
            else:
                row.append(str(r["summary"].get(m)))
        table.add_row(*row)
    console.print(table)


def _render_markdown(pdf: Path, results: dict[str, dict]) -> str:
    lines = [
        f"# Bake-off report — {pdf.name}",
        "",
        "| Metric | " + " | ".join(results.keys()) + " |",
        "|---|" + "---|" * len(results),
    ]
    metrics = [
        "page_count",
        "elapsed_seconds",
        "profile",
        "profile_auto_detected",
        "toc_found",
        "toc_entries",
        "node_count",
        "chunk_count",
        "unattached_elements",
        "dropped_elements",
    ]
    for m in metrics:
        cells = [m]
        for name, r in results.items():
            if r.get("error"):
                cells.append("error")
            else:
                cells.append(str(r["summary"].get(m)))
        lines.append("| " + " | ".join(cells) + " |")

    lines.append("")
    for name, r in results.items():
        if r.get("error"):
            lines.append(f"## {name} — failed\n\n```\n{r['error']}\n```\n")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    app()
