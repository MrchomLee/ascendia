from __future__ import annotations

from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console

from etl.db.init_db import init_db
from etl.pipeline import run_pipeline

load_dotenv()
app = typer.Typer(help="Ingest a PDF manual into the SQLite corpus.")
console = Console()


@app.command()
def main(
    pdf: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    extractor: str = typer.Option("docling", help="Extractor to use: docling | unstructured"),
    code: str | None = typer.Option(None, help="Manual code, e.g. 'DN M 1455'."),
    title: str | None = typer.Option(None, help="Manual title."),
    edition: str | None = typer.Option(None),
    branch: str | None = typer.Option(None, help="Ejército | Fuerza Aérea | Armada"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Force re-running the extractor."),
    ocr: bool = typer.Option(False, "--ocr", help="Enable OCR (default off — assumes native text layer)."),
    profile: str | None = typer.Option(
        None,
        "--profile",
        help="DocumentProfile: manual | codigo_legal | ley_organica. Default: auto-detect.",
    ),
) -> None:
    init_db()
    console.print(
        f"[bold cyan]Ingesting[/] {pdf} with [bold]{extractor}[/] "
        f"(ocr={ocr}, profile={profile or 'auto'})..."
    )
    summary, _extraction, _tree, _chunks = run_pipeline(
        pdf,
        extractor_name=extractor,  # type: ignore[arg-type]
        code=code,
        title=title,
        edition=edition,
        branch=branch,
        use_cache=not no_cache,
        do_ocr=ocr,
        profile=profile,
    )
    console.print(summary.model_dump_json(indent=2))
    console.print(f"[green]Done.[/] Manual id: {summary.manual_id}")


if __name__ == "__main__":
    app()
