"""`qgen-bancos-juego` — arma los bancos de preguntas del juego, uno por escuela.

Toma el bundle más reciente de cada manual (`data/bundles`) y los perfiles de
escuela (`perfiles/ASP_*.json`), y escribe `juego/bancos/<CODE>.json` más un
`index.json` con las escuelas: una corrida completa lo reemplaza y una con
`--escuela` lo fusiona con el previo. Primero arma los bancos de todas las
escuelas pedidas; si alguna falla no escribe ningún archivo. La conversión vive en
`qgen.juego.bancos`; aquí solo se leen carpetas, se resume y se escribe.
"""

from __future__ import annotations

import warnings
import zlib
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.markup import escape
from rich.table import Table

from qgen.juego.bancos import (
    banco_de_escuela,
    cargar_bundles,
    cargar_perfil,
    escribir_banco,
    escribir_indice,
    leer_indice,
    ultimos_bundles,
)

app = typer.Typer(help="Arma los bancos de preguntas del juego, uno por escuela.")
console = Console()

DEFAULT_BUNDLES = Path("data/bundles")
DEFAULT_PERFILES = Path("perfiles")
DEFAULT_OUT = Path("juego/bancos")

# Lo que puede salir de leer un bundle (JSON, gzip truncado o roto) o un perfil
# (JSON, una clave que falta): se muestra con el nombre del archivo, sin traceback.
_ERRORES_DE_LECTURA = (ValueError, OSError, KeyError, EOFError, zlib.error)

#: Un mundo con menos preguntas que esto se marca con un aviso (no es error).
MINIMO_SIN_AVISO = 30


@app.command()
def main(
    bundles: Path = typer.Option(
        DEFAULT_BUNDLES, "--bundles", help="Carpeta de los bundles (toma el más reciente de cada manual)."
    ),
    perfiles: Path = typer.Option(
        DEFAULT_PERFILES, "--perfiles", help="Carpeta de los perfiles de escuela."
    ),
    out: Path = typer.Option(DEFAULT_OUT, "--out", "-o", help="Carpeta donde escribir los bancos."),
    escuela: list[str] = typer.Option(
        [], "--escuela", "-e", help="Código de escuela (repetible); por defecto, todos los ASP_*.json."
    ),
    check: bool = typer.Option(False, "--check", help="Arma y resume los bancos; no escribe nada."),
) -> None:
    for carpeta in (bundles, perfiles):
        if not carpeta.is_dir():
            console.print(f"[red]error[/] {escape(str(carpeta))} no es una carpeta.")
            raise typer.Exit(1)

    rutas = _rutas_de_perfiles(perfiles, escuela)
    if not rutas:
        console.print(f"[red]error[/] no hay perfiles ASP_*.json en {escape(str(perfiles))}.")
        raise typer.Exit(1)
    faltan = [str(ruta) for ruta in rutas if not ruta.is_file()]
    if faltan:
        console.print(f"[red]error[/] no existen los perfiles {escape(', '.join(faltan))}.")
        raise typer.Exit(1)

    try:
        por_manual = cargar_bundles(ultimos_bundles(bundles))
    except _ERRORES_DE_LECTURA as exc:
        console.print(f"[red]error[/] no se pudieron leer los bundles: {escape(_mensaje(exc))}")
        raise typer.Exit(1) from exc

    armados: list[dict[str, Any]] = []
    errores = 0
    for ruta in rutas:
        try:
            banco, resumen = _armar(ruta, por_manual)
        except _ERRORES_DE_LECTURA as exc:
            mensaje = _mensaje(exc)
            if not isinstance(exc, ValueError):  # los ValueError ya dicen el perfil
                mensaje = f"{ruta.name}: {mensaje}"
            console.print(f"[red]error[/] {escape(mensaje)}")
            errores += 1
            continue
        _imprimir_resumen(banco, resumen)
        code = banco["escuela"]["code"]
        vacios = [id_mundo for id_mundo, cuenta in resumen["mundos"].items() if cuenta["total"] == 0]
        for id_mundo in vacios:
            console.print(
                f"[red]error[/] {escape(f'{code} · {id_mundo}')}: el mundo quedó sin preguntas."
            )
        errores += len(vacios)
        armados.append(banco)

    if errores:
        console.print(f"\n[red]{errores} error(es); no se escribió nada.[/]")
        raise typer.Exit(1)

    if check:
        console.print(f"\n[green]{len(armados)} banco(s) armados.[/] (--check: no se escribió nada)")
        return

    # Con --escuela el índice se fusiona con el previo, que se lee antes de
    # escribir ningún banco; una corrida completa lo reemplaza.
    fusionar = bool(escuela)
    previas: list[dict[str, Any]] = []
    if fusionar:
        try:
            previas = leer_indice(out)
        except (ValueError, OSError) as exc:
            console.print(
                f"[yellow]aviso[/] {escape(str(exc))} Se reconstruye con las escuelas de esta corrida."
            )

    for banco in armados:
        console.print(f"[green]Escrito[/] {escape(str(escribir_banco(out, banco)))}")
    indice = escribir_indice(out, armados, fusionar=fusionar, previas=previas)
    console.print(f"[green]Escrito[/] {escape(str(indice))}")


def _mensaje(exc: BaseException) -> str:
    """El texto de un error de lectura; un `KeyError` solo trae la clave."""
    if isinstance(exc, KeyError):
        return f"falta la clave {exc.args[0]!r}."
    return str(exc) or type(exc).__name__


def _rutas_de_perfiles(perfiles: Path, escuelas: list[str]) -> list[Path]:
    """Los perfiles pedidos con `--escuela` (sin repetir), o todos los `ASP_*.json`."""
    if escuelas:
        return [perfiles / f"{code}.json" for code in dict.fromkeys(escuelas)]
    return sorted(perfiles.glob("ASP_*.json"))


def _armar(
    ruta: Path, por_manual: dict[str, dict[str, Any]]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """El banco y el resumen de un perfil; sus avisos salen en amarillo, no como traceback."""
    with warnings.catch_warnings(record=True) as avisos:
        warnings.simplefilter("always")
        try:
            return banco_de_escuela(cargar_perfil(ruta), por_manual)
        finally:
            for aviso in avisos:
                console.print(f"[yellow]aviso[/] {escape(str(aviso.message))}")


def _imprimir_resumen(banco: dict[str, Any], resumen: dict[str, Any]) -> None:
    """Una tabla por escuela y un aviso por cada mundo con menos de `MINIMO_SIN_AVISO`."""
    escuela = banco["escuela"]
    table = Table(title=escape(f"{escuela['code']} — {escuela['name']}"))
    table.add_column("Mundo")
    table.add_column("Materia")
    table.add_column("Manual")
    table.add_column("Preguntas", justify="right")
    table.add_column("n 0/1/2", justify="right")
    table.add_column("Descartadas")
    pocos: list[tuple[str, int]] = []
    for mundo in banco["mundos"]:
        cuenta = resumen["mundos"][mundo["id"]]
        total = cuenta["total"]
        if total == 0:
            preguntas = "[red]0[/]"
        elif total < MINIMO_SIN_AVISO:
            preguntas = f"[yellow]{total:,}[/]"
            pocos.append((mundo["id"], total))
        else:
            preguntas = f"{total:,}"
        descartadas = ", ".join(
            f"{motivo} {n}" for motivo, n in sorted(cuenta["descartadas"].items())
        )
        table.add_row(
            mundo["id"],
            escape(mundo["materia"]),
            mundo["manual"],
            preguntas,
            " / ".join(f"{n:,}" for n in cuenta["por_n"]),
            descartadas or "—",
        )
    console.print(table)
    for id_mundo, total in pocos:
        console.print(
            f"[yellow]aviso[/] {escape(escuela['code'])} · {id_mundo}: "
            f"menos de {MINIMO_SIN_AVISO} preguntas (hay {total})."
        )


if __name__ == "__main__":
    app()
