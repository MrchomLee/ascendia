"""Paso 1: las páginas del PDF como imágenes, ampliadas para que lean mejor la maquetación y los OCR.

Si la página es un escaneo (una imagen que la cubre), se toma la imagen original tal cual, se gira si
la página está girada y se amplía al doble. Si no, se dibuja la página a ~288 ppp.
"""

from __future__ import annotations

import io
from pathlib import Path

import pymupdf
from PIL import Image

from etl.escaneo.carpeta import Carpeta, leer_rango, nombre_pagina

ZOOM_DIBUJO = 4.0          # 72 ppp × 4 ≈ 288 ppp cuando no hay imagen de escaneo
COBERTURA_ESCANEO = 0.6    # la imagen más grande cubre al menos esta fracción de la página


def imagen_de_pagina(page: pymupdf.Page) -> Image.Image:
    """La imagen de escaneo de la página al doble; si no la hay, la página dibujada."""
    doc = page.parent
    imagenes = page.get_images(full=True)
    if imagenes:
        xref = max(imagenes, key=lambda im: im[2] * im[3])[0]
        cajas = page.get_image_rects(xref)
        area_pag = page.rect.width * page.rect.height
        if cajas and max(c.width * c.height for c in cajas) >= COBERTURA_ESCANEO * area_pag:
            im = Image.open(io.BytesIO(doc.extract_image(xref)["image"])).convert("RGB")
            if page.rotation:
                im = im.rotate(-page.rotation, expand=True)
            return im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(ZOOM_DIBUJO, ZOOM_DIBUJO))
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def extraer_paginas(pdf: Path, carpeta: Carpeta, rango: str | None = None, rehacer: bool = False) -> list[str]:
    """Escribe paginas/pNNNN.png para cada página del rango. Devuelve los nombres escritos."""
    carpeta.paginas.mkdir(parents=True, exist_ok=True)
    escritas = []
    with pymupdf.open(pdf) as doc:
        for n in leer_rango(rango, doc.page_count):
            destino = carpeta.paginas / f"{nombre_pagina(n)}.png"
            if destino.exists() and not rehacer:
                continue
            imagen_de_pagina(doc[n - 1]).save(destino)
            escritas.append(destino.stem)
    return escritas
