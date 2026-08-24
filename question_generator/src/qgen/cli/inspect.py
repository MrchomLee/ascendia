from __future__ import annotations

import typer
from dotenv import load_dotenv
from etl.db.session import session_scope
from etl.models.schema import Node
from rich.console import Console
from rich.panel import Panel
from sqlalchemy import select

from qgen.models.schema import Question, QuestionOption

from qgen.db.migration import init_question_tables

load_dotenv()
app = typer.Typer(help="Inspect a generated question.")
console = Console()


@app.command()
def main(question_id: int) -> None:
    init_question_tables()
    with session_scope() as session:
        q = session.get(Question, question_id)
        if q is None:
            console.print(f"[red]Question {question_id} not found.[/]")
            raise typer.Exit(1)
        node = session.get(Node, q.node_id)
        options = (
            session.execute(
                select(QuestionOption).where(QuestionOption.question_id == q.id).order_by(QuestionOption.order_in_question)
            )
            .scalars()
            .all()
        )

        header = f"[bold cyan]Question #{q.id}[/]  (run {q.run_id}, node {q.node_id})"
        body_lines = [
            f"[bold]Breadcrumb:[/] {node.breadcrumb if node else ''}",
            f"[bold]Pages:[/] {node.page_start}-{node.page_end or node.page_start}" if node else "",
            "",
            f"[bold]Pregunta:[/] {q.question_text}",
            "",
        ]
        for opt in options:
            color = {
                "correct": "green",
                "confusa": "yellow",
                "distractor": "cyan",
            }.get(opt.role, "white")
            body_lines.append(f"  [{color}]({opt.role})[/]  {opt.text}")
        body_lines.append("")
        body_lines.append(f"[bold]Justificación:[/] {q.justification}")
        body_lines.append("")
        body_lines.append(f"[dim]validation_status: {q.validation_status}  created_at: {q.created_at.isoformat(timespec='seconds')}[/]")

        console.print(Panel("\n".join(line for line in body_lines if line is not None), title=header, expand=True))


if __name__ == "__main__":
    app()
