"""Recortes de las regiones que se leen: con margen, con lo descartado en blanco y partidos en
renglones en blanco cuando son muy altos (PaddleOCR-VL lee mal recortes de más de ~1000 px)."""

from __future__ import annotations

import hashlib
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

MARGEN = 6
ALTO_MAXIMO = 1000
BLANQUEAR = {"fig", "cap", "nota", "rotulo", "contexto"}


def _fraccion_encimada(b: list[float], caja: list[float]) -> float:
    ancho = min(b[2], caja[2]) - max(b[0], caja[0])
    alto = min(b[3], caja[3]) - max(b[1], caja[1])
    if ancho <= 0 or alto <= 0:
        return 0.0
    return ancho * alto / max(1.0, (b[2] - b[0]) * (b[3] - b[1]))


def recortar(img: Image.Image, el: dict[str, Any], elems: list[dict[str, Any]]) -> Image.Image:
    """La región con margen; lo descartado que se le encima (figuras, rótulos…) queda en blanco."""
    x0, y0, x1, y1 = [int(round(v)) for v in el["bbox"]]
    x0, y0 = max(0, x0 - MARGEN), max(0, y0 - MARGEN)
    x1, y1 = min(img.width, x1 + MARGEN), min(img.height, y1 + MARGEN)
    crop = img.crop((x0, y0, x1, y1)).copy()
    d = ImageDraw.Draw(crop)
    for o in elems:
        if o is el or o["keep"] or o["why"] not in BLANQUEAR:
            continue
        b = o["bbox"]
        if _fraccion_encimada(b, [x0, y0, x1, y1]) <= 0.3:
            continue
        ix0, iy0, ix1, iy1 = max(x0, b[0]), max(y0, b[1]), min(x1, b[2]), min(y1, b[3])
        if ix1 > ix0 and iy1 > iy0:
            d.rectangle([ix0 - x0, iy0 - y0, ix1 - x0, iy1 - y0], fill="white")
    return crop


def renglones_en_blanco(crop: Image.Image) -> np.ndarray:
    a = np.asarray(crop.convert("L")).astype(int)
    fondo = np.percentile(a, 90)
    return (a < fondo - 60).sum(1) <= 1


def partir(crop: Image.Image, arriba: int = 0, alto_maximo: int = ALTO_MAXIMO) -> list[tuple[int, Image.Image]]:
    """Parte en renglones en blanco cercanos a la mitad hasta que cada trozo mida <= alto_maximo."""
    h = crop.height
    if h <= alto_maximo:
        return [(arriba, crop)]
    blanco = renglones_en_blanco(crop)
    tramos, y = [], 0
    while y < h:
        if blanco[y]:
            s = y
            while y < h and blanco[y]:
                y += 1
            tramos.append((s, y))
        else:
            y += 1
    cands = [(s, e) for s, e in tramos if 0.25 * h <= (s + e) / 2 <= 0.75 * h and e - s >= 6]
    if not cands:
        cands = [(s, e) for s, e in tramos if 0.1 * h <= (s + e) / 2 <= 0.9 * h and e - s >= 3]
    if cands:
        s, e = max(cands, key=lambda r: (r[1] - r[0]) - 0.02 * abs((r[0] + r[1]) / 2 - h / 2))
        corte = (s + e) // 2
    else:
        corte = h // 2
    a = crop.crop((0, 0, crop.width, corte))
    b = crop.crop((0, corte, crop.width, h))
    return partir(a, arriba, alto_maximo) + partir(b, arriba + corte, alto_maximo)


def clave(im: Image.Image, tarea: str) -> str:
    """Clave de caché por contenido: el mismo recorte con la misma tarea no se vuelve a leer."""
    return tarea + ":" + hashlib.md5(im.tobytes() + str(im.size).encode()).hexdigest()[:16]


def muy_chico(bbox: list[float]) -> bool:
    return bbox[2] - bbox[0] < 40 or bbox[3] - bbox[1] < 20
