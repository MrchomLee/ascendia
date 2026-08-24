"""CLI for monitoring + finalizing batch runs.

Usage patterns
--------------
1) Just check what's running (no API calls, only DB):
       qgen-batch-status

2) Check / advance one run. Polls Gemini, and if the job is in a terminal
   state, parses + persists the questions in the same call:
       qgen-batch-status <run_id>

3) Same as (2) but block until the job is done (polls every N seconds):
       qgen-batch-status <run_id> --wait

4) Check without persisting (DB-only inspection):
       qgen-batch-status <run_id> --no-finalize
"""

from __future__ import annotations

import time

import typer
from dotenv import load_dotenv
from etl.db.session import session_scope
from rich.console import Console
from rich.table import Table
from sqlalchemy import select

from qgen.db.migration import init_question_tables
from qgen.gemini.batch import is_terminal_state, poll_batch
from qgen.models.schema import GenerationRun
from qgen.pipeline import finalize_batch_run

load_dotenv()
app = typer.Typer(help="Inspect / advance batch generation runs.")
console = Console()


@app.command()
def main(
    run_id: int | None = typer.Argument(
        None,
        help="Specific run id. Omit to list all batch runs in 'running' state.",
    ),
    finalize: bool = typer.Option(
        True,
        "--finalize/--no-finalize",
        help="When ON (default) and the Gemini job is in a terminal state, "
        "parse responses + persist questions in this same call.",
    ),
    wait: bool = typer.Option(
        False,
        "--wait",
        help="Block and poll until the job reaches a terminal state.",
    ),
    poll_interval: int = typer.Option(
        30, "--poll-interval", help="Seconds between polls when --wait is on."
    ),
) -> None:
    init_question_tables()
    with session_scope() as session:
        if run_id is None:
            stmt = (
                select(GenerationRun)
                .where(GenerationRun.mode == "batch")
                .where(GenerationRun.status == "running")
                .order_by(GenerationRun.id.desc())
            )
            runs = session.execute(stmt).scalars().all()
            _print_running(runs)
            return

        run = session.get(GenerationRun, run_id)
        if run is None:
            console.print(f"[red]Run {run_id} not found.[/]")
            raise typer.Exit(1)

        if not run.batch_job_id:
            console.print(f"[yellow]Run {run_id} has no batch_job_id — was this an immediate run?[/]")
            _print_run_card(run, gemini_state="N/A (no batch)")
            return

        if run.status in ("succeeded", "partial", "failed"):
            console.print(f"[green]Run {run_id} already finalized — status {run.status}.[/]")
            _print_run_card(run, gemini_state=run.status)
            return

        if wait:
            _wait_loop(session, run, poll_interval=poll_interval, do_finalize=finalize)
            return

        _check_once(session, run, do_finalize=finalize)


def _check_once(session, run: GenerationRun, *, do_finalize: bool) -> None:
    job = poll_batch(run.batch_job_id)
    state = _state_name(job)
    is_done = is_terminal_state(job)

    if not is_done:
        console.print(
            f"[yellow]Run {run.id}: still in progress.[/] "
            f"Gemini state: [bold]{state}[/]. "
            f"Wait a bit and run the same command again, "
            f"or pass [cyan]--wait[/] to poll automatically."
        )
        _print_run_card(run, gemini_state=state)
        return

    if not do_finalize:
        console.print(
            f"[green]Run {run.id}: terminal state {state}.[/] "
            f"Pass without [cyan]--no-finalize[/] to parse + persist."
        )
        _print_run_card(run, gemini_state=state)
        return

    summary = finalize_batch_run(session, run.id)
    refreshed = session.get(GenerationRun, run.id)
    console.print(
        f"[bold green]Run {run.id} finalized.[/] "
        f"Status: [bold]{refreshed.status}[/]  •  "
        f"{summary.nodes_completed}/{summary.nodes_total} questions persisted, "
        f"{summary.nodes_failed} failed  •  cost: ${summary.actual_cost_usd:.4f}"
    )
    _print_run_card(refreshed, gemini_state=state)


def _wait_loop(session, run: GenerationRun, *, poll_interval: int, do_finalize: bool) -> None:
    console.print(
        f"Polling Gemini for run {run.id} every {poll_interval}s. "
        f"Press Ctrl-C to stop and check later with [cyan]qgen-batch-status {run.id}[/]."
    )
    while True:
        try:
            job = poll_batch(run.batch_job_id)
        except Exception as exc:
            console.print(f"[red]Poll error: {exc}[/]. Retrying in {poll_interval}s...")
            time.sleep(poll_interval)
            continue

        state = _state_name(job)
        if is_terminal_state(job):
            console.print(f"[green]Reached terminal state: {state}[/]")
            if do_finalize:
                summary = finalize_batch_run(session, run.id)
                refreshed = session.get(GenerationRun, run.id)
                console.print(
                    f"[bold green]Run {run.id} finalized.[/] "
                    f"Status: [bold]{refreshed.status}[/]  •  "
                    f"{summary.nodes_completed}/{summary.nodes_total} persisted, "
                    f"{summary.nodes_failed} failed  •  cost: ${summary.actual_cost_usd:.4f}"
                )
                _print_run_card(refreshed, gemini_state=state)
            else:
                _print_run_card(run, gemini_state=state)
            return

        console.print(f"  [{time.strftime('%H:%M:%S')}] state={state} — sleeping {poll_interval}s")
        time.sleep(poll_interval)


def _state_name(job) -> str:
    state = getattr(getattr(job, "state", None), "name", None) or str(getattr(job, "state", ""))
    return state or "(unknown)"


def _print_running(runs) -> None:
    if not runs:
        console.print(
            "No batch runs in 'running' state. "
            "Submit one with [cyan]qgen-generate <manual_id> --batch[/]."
        )
        return
    table = Table(title="Batch runs in 'running' state (DB view; doesn't poll Gemini)")
    for col in ("run_id", "manual_id", "model", "nodes_total", "started_at", "batch_job_id"):
        table.add_column(col)
    for r in runs:
        table.add_row(
            str(r.id), str(r.manual_id), r.model, str(r.nodes_total),
            r.started_at.isoformat(timespec="seconds"),
            r.batch_job_id or "",
        )
    console.print(table)
    console.print(
        "[dim]Tip:[/] check one with [cyan]qgen-batch-status <run_id>[/] "
        "(polls Gemini and persists if done)."
    )


def _print_run_card(run: GenerationRun, *, gemini_state: str) -> None:
    table = Table(title=f"Run {run.id}")
    table.add_column("Field")
    table.add_column("Value")
    for k, v in [
        ("manual_id", str(run.manual_id)),
        ("model", run.model),
        ("mode", run.mode),
        ("DB status", run.status),
        ("Gemini state", gemini_state),
        ("nodes_total", str(run.nodes_total)),
        ("nodes_completed", str(run.nodes_completed)),
        ("nodes_failed", str(run.nodes_failed)),
        ("batch_job_id", run.batch_job_id or ""),
        ("started_at", run.started_at.isoformat(timespec="seconds") if run.started_at else ""),
        ("completed_at", run.completed_at.isoformat(timespec="seconds") if run.completed_at else ""),
        ("cost_usd", f"${run.cost_estimate_usd:.4f}"),
    ]:
        table.add_row(k, v)
    console.print(table)


if __name__ == "__main__":
    app()
