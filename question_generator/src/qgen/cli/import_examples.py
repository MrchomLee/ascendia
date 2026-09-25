"""Comando CLI para importar un banco de preguntas de referencia (ejemplos oro) a la base de datos."""

from __future__ import annotations

from pathlib import Path
import typer
from rich.console import Console

from etl.db.session import session_scope
from qgen.db.migration import init_question_tables
from qgen.reference.importer import import_reference_questions, load_reference_file

app = typer.Typer(help="Importador de preguntas de ejemplo para Few-Shot Prompting.")
console = Console()


@app.command()
def main(
    file_path: Path = typer.Argument(..., help="Ruta al archivo JSON, JSONL, CSV o XLSX (una hoja por nivel) con preguntas de ejemplo."),
    profile: str = typer.Option("global", "--profile", "-p", help="Perfil al que asociar las preguntas (ej. algebra_baldor, ley_organica)."),
    source_tag: str | None = typer.Option(None, "--source-tag", "-t", help="Etiqueta de origen (ej. examen_2024, banco_oficial)."),
) -> None:
    """Carga un archivo de preguntas de ejemplo y las guarda en la base de datos."""
    console.print(f"[bold blue]Procesando archivo de referencia:[/bold blue] {file_path}")

    init_question_tables()

    try:
        raw_data = load_reference_file(file_path)
    except Exception as e:
        console.print(f"[bold red]Error al leer el archivo:[/bold red] {e}")
        raise typer.Exit(code=1)

    with session_scope() as session:
        created = import_reference_questions(
            session,
            raw_data,
            default_profile=profile,
            default_source_tag=source_tag,
        )
        console.print(f"[bold green]Exito:[/bold green] Se importaron {len(created)} preguntas de ejemplo para el perfil '[yellow]{profile}[/yellow]'.")


if __name__ == "__main__":
    app()
