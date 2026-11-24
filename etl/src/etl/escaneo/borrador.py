"""Paso 5: el borrador en Markdown con el texto de PaddleOCR-VL, en orden de lectura.

Cada página empieza con «[pNNNN]» (página del PDF, no el folio impreso). Los títulos van como «### »,
las tablas entre [TABLA] y [/TABLA] y las fórmulas entre $$. Es un borrador: el ensamble final del
libro (folios impresos, niveles de título, párrafos partidos entre páginas, correcciones revisadas en
la imagen) se hace a mano sobre él.
"""

from __future__ import annotations

import re
from typing import Any

from PIL import Image

from etl.escaneo.carpeta import Carpeta, leer_json

FRACCION_ANCHA = 0.55   # una región más ancha que esto (respecto de la página) va a todo lo ancho


def orden_de_lectura(elems: list[dict[str, Any]], ancho_pagina: int) -> list[int]:
    """Índices de las regiones en orden de lectura para páginas de una o dos columnas.

    Lo que va a todo lo ancho parte la página en franjas; dentro de cada franja se lee primero la
    columna izquierda y luego la derecha."""
    anchas = sorted(e["bbox"][1] for e in elems
                    if e["keep"] and e["bbox"][2] - e["bbox"][0] > FRACCION_ANCHA * ancho_pagina)
    mitad = ancho_pagina / 2

    def llave(i: int) -> tuple[int, int, float]:
        b = elems[i]["bbox"]
        franja = sum(1 for a in anchas if a <= b[1] + 1)
        if b[2] - b[0] > FRACCION_ANCHA * ancho_pagina:
            columna = -1
        else:
            columna = 0 if (b[0] + b[2]) / 2 < mitad else 1
        return (franja, columna, b[1])

    return sorted(range(len(elems)), key=llave)


def unir_trozos(trozos: list[str]) -> str:
    """Une los trozos de una región. PaddleOCR-VL pone punto al final de un trozo aunque la frase siga:
    si el siguiente empieza con minúscula, ese punto se quita."""
    salida = ""
    for t in (x.strip() for x in trozos):
        if not t:
            continue
        if salida and salida.endswith(".") and not salida.endswith("..") and t[0].islower():
            salida = salida[:-1]
        salida = f"{salida} {t}" if salida else t
    return salida


def limpiar(texto: str) -> str:
    """Quita el guion de corte de renglón («neu-\\nrona» → «neurona») y junta los renglones."""
    texto = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", texto)
    return re.sub(r"\s*\n\s*", " ", texto).strip()


def armar_borrador(carpeta: Carpeta) -> int:
    """segmentos + índice + caché del OCR → borrador.md. Devuelve cuántas regiones escribió."""
    segs = leer_json(carpeta.segmentos)
    indice = leer_json(carpeta.ocr_indice)
    cache = leer_json(carpeta.ocr_cache, {})
    partes: list[str] = []
    n = 0
    for p in sorted(segs):
        elems = segs[p]["elems"]
        with Image.open(carpeta.paginas / f"{p}.png") as im:
            ancho = im.width
        partes.append(f"\n[{p}]\n")
        for i in orden_de_lectura(elems, ancho):
            el = elems[i]
            claves = indice.get(p, {}).get(str(i))
            if not el["keep"] or not claves or any(k not in cache for k in claves):
                continue
            n += 1
            if el["kind"] == "table":
                partes.append("[TABLA]\n" + cache[claves[0]].strip() + "\n[/TABLA]")
            elif el["kind"] == "formula":
                partes.append("$$" + " ".join(cache[k].strip() for k in claves) + "$$")
            else:
                texto = unir_trozos([limpiar(cache[k]) for k in claves])
                partes.append(f"### {texto}" if el["kind"] == "title" else texto)
    carpeta.borrador.write_text("\n\n".join(partes).strip() + "\n", encoding="utf-8")
    return n
