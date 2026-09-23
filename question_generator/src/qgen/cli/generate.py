from __future__ import annotations

import typer
from dotenv import load_dotenv
from etl.db.session import session_scope
from rich.console import Console
from rich.table import Table

from qgen.db.migration import init_question_tables
from qgen.gemini.client import MODEL_FLASH, resolve_model
from qgen.pipeline import estimate_only, run_generation

load_dotenv()
app = typer.Typer(help="Generate questions for a manual.")
console = Console()


def _model_option(value: str) -> str:
    try:
        return resolve_model(value)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc


@app.command()
def main(
    manual_id: int = typer.Argument(..., help="Manual id (see `etl-inspect manuals`)."),
    model: str = typer.Option(MODEL_FLASH, callback=_model_option, help="flash | pro | full model name."),
    immediate: bool = typer.Option(True, "--immediate/--batch", help="Execution mode."),
    limit: int | None = typer.Option(None, help="Process at most N windows (dev/iteration)."),
    node_id: int | None = typer.Option(None, "--node-id", help="Generate only the windows of this node id."),
    regenerate: bool = typer.Option(False, "--regenerate", help="Delete and redo the questions of the selected windows."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Estimate cost only, do not call Gemini."),
) -> None:
    init_question_tables()
    mode = "immediate" if immediate else "batch"

    with session_scope() as session:
        if dry_run:
            estimate, n = estimate_only(
                session,
                manual_id=manual_id,
                model_name=model,
                mode=mode,
                limit=limit,
                only_node_id=node_id,
                regenerate=regenerate,
            )
            _print_estimate(estimate, n, mode)
            return

        summary = run_generation(
            session,
            manual_id=manual_id,
            model_name=model,
            mode=mode,
            limit=limit,
            only_node_id=node_id,
            regenerate=regenerate,
            progress_cb=_progress_cb,
        )

    _print_summary(summary)


def _progress_cb(idx: int, total: int, job, resumen: dict | None, error: str | None) -> None:
    etiqueta = f"{job.node_label} [{job.window.key}]"
    if error is not None:
        console.print(f"[red][{idx + 1}/{total}] {etiqueta}  ERROR: {error}[/]")
    else:
        console.print(
            f"[green][{idx + 1}/{total}] {etiqueta}  OK[/] {resumen['guardadas']} preguntas "
            f"({resumen['revision']} a revisar, {resumen['descartes']} descartadas)"
        )


def _print_estimate(estimate, n_windows: int, mode: str) -> None:
    table = Table(title=f"Cost estimate ({mode}, {estimate.model})")
    table.add_column("Field")
    table.add_column("Value", justify="right")
    rows = [
        ("Windows to process", str(n_windows)),
        ("Window tokens", f"{estimate.window_tokens:,}"),
        ("Questions (est.)", str(estimate.n_questions)),
        ("Exercise verifications (est.)", str(estimate.verifications)),
        ("Doc tokens (cached)", f"{estimate.cache_tokens:,}"),
        ("Cache create (one-off)", f"${estimate.cache_create_usd:.4f}"),
        ("Cache storage (1h)", f"${estimate.cache_storage_usd:.4f}"),
        ("Generation", f"${estimate.generation_usd:.4f}"),
        ("Verification", f"${estimate.verification_usd:.4f}"),
        ("TOTAL", f"${estimate.total_usd:.4f}"),
    ]
    for k, v in rows:
        table.add_row(k, v)
    console.print(table)


def _print_summary(summary) -> None:
    table = Table(title=f"Run #{summary.run_id} summary")
    table.add_column("Field")
    table.add_column("Value", justify="right")
    rows = [
        ("Mode", summary.mode),
        ("Model", summary.model),
        ("Profile", summary.profile),
        ("Windows", str(summary.windows_total)),
        ("Windows failed", str(summary.windows_failed)),
        ("Questions saved", str(summary.questions_saved)),
        ("Nodes total", str(summary.nodes_total)),
        ("Nodes completed", str(summary.nodes_completed)),
        ("Actual cost (USD)", f"${summary.actual_cost_usd:.4f}"),
    ]
    if summary.batch_job_id:
        rows.append(("Batch job id", summary.batch_job_id))
    for k, v in rows:
        table.add_row(k, v)
    console.print(table)


if __name__ == "__main__":
    app()
