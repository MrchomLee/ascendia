"""`qgen-claude`: generar preguntas desde Claude Code, sin API (ver `qgen.claude_code`)."""

from __future__ import annotations

from pathlib import Path

import typer
from etl.db.session import session_scope
from rich.console import Console

from qgen.claude_code import exportar, importar
from qgen.claude_review import exportar_revision, importar_revision
from qgen.cli.generate import _print_summary, _progress_cb
from qgen.db.migration import init_question_tables

app = typer.Typer(help="Generar preguntas desde Claude Code: exportar ventanas e importar respuestas.")
console = Console()


@app.command("exportar")
def exportar_cmd(
    manual_id: int = typer.Argument(..., help="Id del manual (ver `etl-inspect manuals`)."),
    carpeta: Path | None = typer.Option(None, help="Carpeta de intercambio (por defecto data/claude_code/<código>)."),
    limit: int | None = typer.Option(None, help="Exportar a lo más N ventanas."),
) -> None:
    """Escribe la instrucción y las ventanas pendientes para que Claude Code las responda."""
    init_question_tables()
    with session_scope() as session:
        exportacion = exportar(session, manual_id=manual_id, carpeta=carpeta, limit=limit)
    console.print(f"{exportacion.ventanas} ventanas pendientes en {exportacion.carpeta}")


@app.command("importar")
def importar_cmd(
    manual_id: int = typer.Argument(..., help="Id del manual (ver `etl-inspect manuals`)."),
    carpeta: Path | None = typer.Option(None, help="Carpeta de intercambio (por defecto data/claude_code/<código>)."),
) -> None:
    """Revisa y guarda las respuestas de las ventanas pendientes, como una corrida más."""
    init_question_tables()
    with session_scope() as session:
        summary = importar(session, manual_id=manual_id, carpeta=carpeta, progress_cb=_progress_cb)
    if summary is None:
        console.print("Ninguna ventana pendiente tiene respuesta: no se creó corrida.")
        return
    _print_summary(summary)


@app.command("exportar-revision")
def exportar_revision_cmd(
    manual_id: int = typer.Argument(..., help="Id del manual (ver `etl-inspect manuals`)."),
    carpeta: Path | None = typer.Option(None, help="Carpeta de intercambio (por defecto data/claude_code/<código>)."),
) -> None:
    """Escribe la rúbrica y los lotes de preguntas sin decidir para que Claude Code las califique."""
    init_question_tables()
    with session_scope() as session:
        exportacion = exportar_revision(session, manual_id=manual_id, carpeta=carpeta)
    console.print(f"{exportacion.preguntas} preguntas en {exportacion.lotes} lotes en {exportacion.carpeta}")


@app.command("importar-revision")
def importar_revision_cmd(
    manual_id: int = typer.Argument(..., help="Id del manual (ver `etl-inspect manuals`)."),
    carpeta: Path | None = typer.Option(None, help="Carpeta de intercambio (por defecto data/claude_code/<código>)."),
) -> None:
    """Aplica los veredictos: aceptar → valid, rechazar → rejected, dudosa → needs_review."""
    init_question_tables()
    with session_scope() as session:
        resumen = importar_revision(session, manual_id=manual_id, carpeta=carpeta)
    console.print(
        f"[green]{resumen.aceptadas} aceptadas[/], [red]{resumen.rechazadas} rechazadas[/], "
        f"[yellow]{resumen.dudosas} dudosas[/]"
    )
    for qid, motivo in resumen.omitidas:
        console.print(f"  omitida {qid}: {motivo}")
    for nombre, error in resumen.lotes_invalidos:
        console.print(f"[red]  lote {nombre} sin aplicar: {error}[/]")


if __name__ == "__main__":
    app()
