from __future__ import annotations

import typer
from dotenv import load_dotenv
from etl.db.session import session_scope
from etl.models.schema import Chunk, Manual
from rich.console import Console
from rich.table import Table
from sqlalchemy import func, select

from qgen.models.schema import GenerationRun, Question

from qgen.db.migration import init_question_tables

load_dotenv()
app = typer.Typer(help="Stats over generation runs and coverage.")
console = Console()


@app.command()
def main(
    manual_id: int | None = typer.Argument(None, help="Filter by manual id (omit for global)."),
) -> None:
    init_question_tables()
    with session_scope() as session:
        manuals_stmt = select(Manual)
        if manual_id is not None:
            manuals_stmt = manuals_stmt.where(Manual.id == manual_id)
        manuals = session.execute(manuals_stmt.order_by(Manual.id)).scalars().all()

        table = Table(title="Manual coverage")
        for col in ("manual_id", "code", "nodes_with_chunks", "questions", "coverage_pct", "validated", "runs"):
            table.add_column(col)

        for m in manuals:
            n_with_chunks = session.execute(
                select(func.count(func.distinct(Chunk.node_id))).where(Chunk.manual_id == m.id)
            ).scalar_one()
            n_questions = session.execute(
                select(func.count(func.distinct(Question.node_id))).where(Question.manual_id == m.id)
            ).scalar_one()
            n_validated = session.execute(
                select(func.count(Question.id)).where(Question.manual_id == m.id).where(Question.validation_status == "valid")
            ).scalar_one()
            n_runs = session.execute(
                select(func.count(GenerationRun.id)).where(GenerationRun.manual_id == m.id)
            ).scalar_one()
            cov = (100.0 * n_questions / n_with_chunks) if n_with_chunks else 0.0
            table.add_row(
                str(m.id), m.code, str(n_with_chunks),
                str(n_questions), f"{cov:.1f}%",
                f"{n_validated}/{n_questions}",
                str(n_runs),
            )
        console.print(table)

        runs = session.execute(
            (select(GenerationRun) if manual_id is None else
             select(GenerationRun).where(GenerationRun.manual_id == manual_id))
            .order_by(GenerationRun.id.desc())
            .limit(10)
        ).scalars().all()
        if runs:
            t2 = Table(title="Recent runs (last 10)")
            for col in ("run_id", "manual_id", "model", "mode", "status", "completed/total", "cost_usd"):
                t2.add_column(col)
            for r in runs:
                t2.add_row(
                    str(r.id), str(r.manual_id), r.model, r.mode, r.status,
                    f"{r.nodes_completed}/{r.nodes_total}",
                    f"${r.cost_estimate_usd:.4f}",
                )
            console.print(t2)


if __name__ == "__main__":
    app()
