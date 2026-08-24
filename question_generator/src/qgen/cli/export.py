"""`qgen-export` — empaqueta un manual en un bundle JSON para entregarlo.

Es la salida del lado de contenido: lo que se entrega es este fichero, nunca
`data/manuals.sqlite`. El formato está especificado en `CONTRATO-BUNDLE.md`
(`docs/06-contrato-bundle-de-contenido.md` en el repo de la webapp).
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import typer
from dotenv import load_dotenv
from etl.db.session import session_scope
from rich.console import Console
from rich.table import Table

from qgen.bundle.build import build_bundle, source_digest
from qgen.bundle.spec import bundle_filename, next_version, validate, write_bundle
from qgen.db.migration import init_question_tables

load_dotenv()
app = typer.Typer(help="Exporta un manual a un bundle JSON entregable.")
console = Console()

DEFAULT_OUT = Path("data/bundles")


@app.command()
def main(
    manual_id: int = typer.Argument(..., help="Id del manual (ver `etl-inspect manuals`)."),
    out: Path = typer.Option(DEFAULT_OUT, "--out", "-o", help="Carpeta donde escribir el bundle."),
    run: list[int] = typer.Option([], "--run", help="Limita a estas corridas (repetible)."),
    check: bool = typer.Option(False, "--check", help="Valida y no escribe nada."),
    include_raw: bool = typer.Option(
        False, "--include-raw", help="Incluye la respuesta cruda de Gemini (pesa mucho)."
    ),
    revision: int | None = typer.Option(
        None, "--revision", help="Número de entrega para el nombre del fichero (por defecto, el siguiente libre)."
    ),
    force: bool = typer.Option(False, "--force", help="Sobrescribe si el fichero ya existe."),
) -> None:
    init_question_tables()

    with session_scope() as session:
        try:
            bundle = build_bundle(
                session,
                manual_id=manual_id,
                run_ids=list(run) or None,
                include_raw=include_raw,
            )
        except ValueError as exc:
            console.print(f"[red]{exc}[/]")
            raise typer.Exit(1) from exc

        source_path = bundle["manual"]["source_path"]
        bundle["manual"]["source_sha256"] = source_digest(source_path)

    report = validate(bundle)

    for warning in report.warnings:
        console.print(f"[yellow]aviso[/] {warning}")
    for error in report.errors:
        console.print(f"[red]error[/] {error}")

    if not report.ok:
        console.print(
            f"\n[red]El bundle no cumple el contrato ({len(report.errors)} error(es)); "
            f"no se escribió nada.[/]"
        )
        raise typer.Exit(1)

    code = bundle["manual"]["code"]
    _print_summary(bundle, report)

    if check:
        console.print("\n[green]El bundle cumple el contrato.[/] (--check: no se escribió nada)")
        return

    out.mkdir(parents=True, exist_ok=True)
    number = revision if revision is not None else next_version(out, code)
    target = out / bundle_filename(code, datetime.now(timezone.utc).date(), number)
    if target.exists() and not force:
        console.print(
            f"\n[red]{target} ya existe.[/] Usa --force para sobrescribirlo o --revision "
            f"para darle otro número."
        )
        raise typer.Exit(1)

    written, checksum = write_bundle(target, bundle)
    size_mb = written.stat().st_size / (1024 * 1024)
    console.print(
        f"\n[green]Escrito[/] {written}  ({size_mb:.1f} MB)\n"
        f"         {written.name}.sha256  ({checksum[:16]}…)"
    )
    console.print(
        "\n[dim]Entrega los dos ficheros juntos: sin el .sha256 el importador no puede "
        "comprobar que el bundle llegó entero.[/]"
    )


def _print_summary(bundle: dict, report) -> None:
    manual = bundle["manual"]
    table = Table(title=f"Bundle de {manual['code']} — {manual['title'][:60]}")
    table.add_column("Campo")
    table.add_column("Valor", justify="right")

    counts = report.counts
    rows = [
        ("Nodos", f"{counts['nodes']:,}"),
        ("Chunks", f"{counts['chunks']:,}"),
        ("Corridas", str(counts["runs"])),
        ("Preguntas", f"{counts['questions']:,}"),
        ("  se sirven a alumnos", f"{counts['questions_served']:,}"),
    ]
    for key, value in counts.items():
        if key.startswith("status_"):
            rows.append((f"  {key.removeprefix('status_')}", str(value)))

    cost = sum(r["cost_estimate_usd"] for r in bundle["runs"])
    rows.append(("Costo de las corridas", f"${cost:.4f}"))
    for key, value in rows:
        table.add_row(key, value)
    console.print(table)


if __name__ == "__main__":
    app()
