"""`qgen-claude`: generar preguntas desde Claude Code, sin API (ver `qgen.claude_code`)."""

from __future__ import annotations

from pathlib import Path

import typer
from etl.db.session import session_scope
from rich.console import Console

from qgen.claude_code import exportar, importar
from qgen.claude_correccion import cargar_ejemplos, exportar_correccion, importar_correccion
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
    ruta: list[str] = typer.Option(
        [], "--ruta", help="Solo los nodos cuya ruta casa con esta expresión regular (se puede repetir): el alcance de un temario.",
    ),
) -> None:
    """Escribe la instrucción y las ventanas pendientes para que Claude Code las responda."""
    init_question_tables()
    with session_scope() as session:
        exportacion = exportar(session, manual_id=manual_id, carpeta=carpeta, limit=limit, rutas=ruta or None)
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
    console.print(
        f"{exportacion.preguntas} preguntas ({exportacion.solo_clasificar} solo para clasificar) "
        f"en {exportacion.lotes} lotes en {exportacion.carpeta}"
    )


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
        f"[yellow]{resumen.dudosas} dudosas[/], {resumen.reclasificadas} reclasificadas, "
        f"{resumen.solo_clasificadas} solo clasificadas"
    )
    for qid, motivo in resumen.omitidas:
        console.print(f"  omitida {qid}: {motivo}")
    for nombre, error in resumen.lotes_invalidos:
        console.print(f"[red]  lote {nombre} sin aplicar: {error}[/]")


if __name__ == "__main__":
    app()


@app.command("exportar-correccion")
def exportar_correccion_cmd(
    manual_id: int = typer.Argument(..., help="Id del manual (ver `etl-inspect manuals`)."),
    ejemplos: Path | None = typer.Option(None, help="JSON con las preguntas que corrigió el usuario (antes, observación, después)."),
    run: int | None = typer.Option(None, help="Solo las preguntas de esta corrida."),
    carpeta: Path | None = typer.Option(None, help="Carpeta de intercambio (por defecto data/claude_code/<código>)."),
    rehacer: bool = typer.Option(False, help="Incluir también las que ya se corrigieron."),
) -> None:
    """Escribe las reglas, los ejemplos del usuario y un lote por ventana para corregir las preguntas."""
    init_question_tables()
    with session_scope() as session:
        exp = exportar_correccion(
            session, manual_id=manual_id, carpeta=carpeta, ejemplos=cargar_ejemplos(ejemplos), run_id=run, rehacer=rehacer,
        )
    console.print(f"{exp.preguntas} preguntas en {exp.lotes} lotes ({exp.ejemplos} ejemplos) en {exp.carpeta}")


@app.command("importar-correccion")
def importar_correccion_cmd(
    manual_id: int = typer.Argument(..., help="Id del manual (ver `etl-inspect manuals`)."),
    carpeta: Path | None = typer.Option(None, help="Carpeta de intercambio (por defecto data/claude_code/<código>)."),
    modelo: str = typer.Option("claude-opus-5-5", help="Quién corrigió (queda en la pregunta)."),
    rehacer: bool = typer.Option(False, help="Aplicar también sobre las que ya se corrigieron."),
) -> None:
    """Aplica las decisiones: sin cambios, corregir (guarda la versión original) o descartar (rejected)."""
    init_question_tables()
    with session_scope() as session:
        r = importar_correccion(session, manual_id=manual_id, carpeta=carpeta, model_name=modelo, rehacer=rehacer)
    console.print(
        f"{r.sin_cambios} sin cambios, [green]{r.corregidas} corregidas[/], [red]{r.descartadas} descartadas[/], "
        f"{r.reclasificadas} cambiaron de nivel"
    )
    for qid, aviso in r.avisos:
        console.print(f"  [yellow]aviso {qid}: {aviso}[/]")
    for qid, motivo in r.omitidas:
        console.print(f"  omitida {qid}: {motivo}")
    for nombre, error in r.lotes_invalidos:
        console.print(f"[red]  lote {nombre} sin aplicar: {error}[/]")
