"""`etl-escanear`: leer un libro escaneado (sin capa de texto) con PaddleOCR-VL y el OCR de Windows.

    etl-escanear todo data/raw_pdfs/libro.pdf --paginas 15-40

hace los seis pasos seguidos; cada paso también se puede correr solo (por ejemplo, después de
corregir ajustes.json se vuelve a correr `segmentar`, `ocr` y `borrador`, y solo se leen los
recortes que cambiaron).
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from etl.escaneo.borrador import armar_borrador
from etl.escaneo.carpeta import Carpeta
from etl.escaneo.dudas import hoja_para_ver, listar_dudas
from etl.escaneo.maquetacion import detectar_regiones, segmentar
from etl.escaneo.ocr import leer_con_paddle, leer_con_windows
from etl.escaneo.paginas import extraer_paginas

app = typer.Typer(help=__doc__, no_args_is_help=True)
consola = Console()

PDF = typer.Argument(..., exists=True, dir_okay=False, readable=True, help="El PDF escaneado.")
CARPETA = typer.Option(None, "--carpeta", help="Carpeta de trabajo (por defecto data/processed/escaneo/<nombre del PDF>).")


def _carpeta(pdf: Path, carpeta: Path | None) -> Carpeta:
    c = Carpeta.para_pdf(pdf, carpeta)
    c.raiz.mkdir(parents=True, exist_ok=True)
    return c


@app.command("paginas")
def paginas_cmd(pdf: Path = PDF, paginas: str = typer.Option(None, help="Páginas del PDF, p. ej. 15-40,52 (desde 1)."),
                carpeta: Path = CARPETA, rehacer: bool = typer.Option(False, help="Volver a sacar las que ya están.")) -> None:
    """1. Saca las páginas como imágenes ampliadas (paginas/pNNNN.png)."""
    c = _carpeta(pdf, carpeta)
    hechas = extraer_paginas(pdf, c, paginas, rehacer)
    consola.print(f"[green]páginas:[/] {len(hechas)} nuevas, {len(c.lista_paginas())} en {c.paginas}")


@app.command("maquetacion")
def maquetacion_cmd(pdf: Path = PDF, carpeta: Path = CARPETA) -> None:
    """2. Detecta las regiones de cada página con Docling y las clasifica (segmentos.json)."""
    c = _carpeta(pdf, carpeta)
    n = detectar_regiones(c, aviso=consola.print)
    paginas, regiones = segmentar(c)
    consola.print(f"[green]maquetación:[/] {n} páginas nuevas; {regiones} regiones a leer en {paginas} páginas")


@app.command("segmentar")
def segmentar_cmd(pdf: Path = PDF, carpeta: Path = CARPETA) -> None:
    """Vuelve a clasificar las regiones con ajustes.json, sin correr el modelo."""
    paginas, regiones = segmentar(_carpeta(pdf, carpeta))
    consola.print(f"[green]segmentos:[/] {regiones} regiones a leer en {paginas} páginas")


@app.command("ocr")
def ocr_cmd(pdf: Path = PDF, carpeta: Path = CARPETA,
            planear: bool = typer.Option(False, "--planear", help="Solo contar los recortes nuevos, sin leerlos."),
            sin_windows: bool = typer.Option(False, "--sin-windows", help="No correr el OCR de Windows.")) -> None:
    """3 y 4. Lee las regiones con PaddleOCR-VL (GPU) y las páginas con el OCR de Windows."""
    c = _carpeta(pdf, carpeta)
    leer_con_paddle(c, solo_planear=planear, aviso=consola.print)
    if not planear and not sin_windows:
        n = leer_con_windows(c)
        consola.print(f"[green]OCR de Windows:[/] {n} páginas nuevas")


@app.command("borrador")
def borrador_cmd(pdf: Path = PDF, carpeta: Path = CARPETA) -> None:
    """5 y 6. Arma borrador.md y la lista de palabras dudosas (dudas.txt)."""
    c = _carpeta(pdf, carpeta)
    n = armar_borrador(c)
    dudas = listar_dudas(c)
    consola.print(f"[green]borrador:[/] {n} regiones en {c.borrador}")
    consola.print(f"[green]dudas:[/] {dudas} palabras para revisar en {c.dudas}")


@app.command("ver")
def ver_cmd(pdf: Path = PDF, palabras: list[str] = typer.Argument(..., help="Palabras del borrador a revisar."),
            carpeta: Path = CARPETA, salida: Path = typer.Option(None, help="PNG de salida (por defecto ver.png en la carpeta).")) -> None:
    """Junta en una imagen el renglón de la página donde aparece cada palabra, para revisarla."""
    c = _carpeta(pdf, carpeta)
    destino = salida or c.raiz / "ver.png"
    n = hoja_para_ver(c, palabras, destino)
    consola.print(f"{n} de {len(palabras)} palabras en {destino}")


@app.command("todo")
def todo_cmd(pdf: Path = PDF, paginas: str = typer.Option(None, help="Páginas del PDF, p. ej. 15-40,52 (desde 1)."),
             carpeta: Path = CARPETA, sin_windows: bool = typer.Option(False, "--sin-windows")) -> None:
    """Los seis pasos seguidos: páginas, maquetación, PaddleOCR-VL, OCR de Windows, borrador y dudas."""
    paginas_cmd(pdf, paginas, carpeta, False)
    maquetacion_cmd(pdf, carpeta)
    ocr_cmd(pdf, carpeta, False, sin_windows)
    borrador_cmd(pdf, carpeta)


if __name__ == "__main__":
    app()
