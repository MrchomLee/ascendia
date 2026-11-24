"""Paso 6: las palabras del borrador que conviene mirar en la imagen, y la hoja para mirarlas.

Una palabra es dudosa si el OCR de Windows no la leyó en esa misma página y, cuando está instalado
`pyspellchecker`, tampoco está en el diccionario de español. El vocabulario para decidir no sale de
PaddleOCR, porque repite sus propios errores.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from PIL import Image, ImageDraw

from etl.escaneo.carpeta import Carpeta, leer_json
from etl.escaneo.ocr import palabras_windows

PALABRA = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ\-]+")
PAGINA = re.compile(r"^\[(p\d{4})\]$", re.M)


def normal(w: str) -> str:
    return unicodedata.normalize("NFC", w).lower().strip(".,;:()«»\"'¿?¡!-")


def diccionario() -> Any | None:
    try:
        from spellchecker import SpellChecker
    except ImportError:
        return None
    return SpellChecker(language="es")


# El diccionario de pyspellchecker trae formas base: se prueba también sin plural, sin pronombre
# enclítico y con la terminación verbal más común cambiada por el infinitivo.
TERMINACIONES = [("es", ""), ("s", ""), ("as", "o"), ("os", "o"), ("a", "o"), ("se", ""), ("rse", "r"),
                 ("aron", "ar"), ("ieron", "er"), ("ieron", "ir"), ("án", ""), ("arán", "ar"), ("erán", "er"),
                 ("irán", "ir"), ("a", "ar"), ("e", "er"), ("e", "ir"), ("an", "ar"), ("en", "er"), ("en", "ir"),
                 ("ando", "ar"), ("iendo", "er"), ("iendo", "ir"), ("ado", "ar"), ("ido", "er"), ("ido", "ir"),
                 ("ada", "ar"), ("adas", "ar"), ("ados", "ar")]


def en_diccionario(w: str, dicc: Any) -> bool:
    if w in dicc:
        return True
    return any(w.endswith(fin) and len(w) - len(fin) >= 3 and w[: len(w) - len(fin)] + base in dicc
               for fin, base in TERMINACIONES)


def paginas_del_borrador(md: str) -> list[tuple[str, str]]:
    trozos = PAGINA.split(md)[1:]
    return list(zip(trozos[::2], trozos[1::2]))


def vocabulario_windows(carpeta: Carpeta) -> set[str]:
    """Todas las palabras que el OCR de Windows leyó en el libro."""
    return {normal(x["t"]) for f in carpeta.windows.glob("p*.json")
            for r in leer_json(f)["lines"] for x in r["words"]}


def dudosas_de_pagina(texto: str, renglones: list[dict[str, Any]], dicc: Any | None = None,
                      vocabulario: set[str] | None = None) -> list[str]:
    """Palabras del texto (≥ 3 letras) que Windows no leyó en la página.

    Se perdonan las que están en el diccionario y, si además se da el vocabulario de todo el libro,
    las que Windows sí leyó en otra página (el diccionario de español no trae plurales ni
    conjugaciones, y Windows también se equivoca: «valotes» por «valores»)."""
    vistas = {normal(x["t"]) for r in renglones for x in r["words"]}
    corrido = normal(" ".join(r["text"] for r in renglones))
    salida = []
    for pal in PALABRA.findall(texto):
        w = normal(pal)
        if len(w) < 3 or w in vistas or re.search(rf"(?<!\w){re.escape(w)}(?!\w)", corrido):
            continue
        if vocabulario and w in vocabulario:
            continue
        if dicc is not None and all(en_diccionario(parte, dicc) for parte in w.split("-") if parte):
            continue
        salida.append(pal)
    return salida


def listar_dudas(carpeta: Carpeta) -> int:
    """borrador.md + windows/ → dudas.txt («pNNNN  palabra | contexto»). Devuelve cuántas hay."""
    md = carpeta.borrador.read_text(encoding="utf-8")
    dicc = diccionario()
    lineas = []
    if dicc is None:
        lineas.append("# sin diccionario: instala el extra «escaneo» para descartar las palabras correctas")
    total = 0
    vocabulario = vocabulario_windows(carpeta) if carpeta.windows.exists() else set()
    for p, texto in paginas_del_borrador(md):
        renglones = palabras_windows(carpeta, p)
        if not renglones:
            lineas.append(f"{p}  (sin OCR de Windows: no se puede contrastar)")
            continue
        for pal, veces in Counter(dudosas_de_pagina(texto, renglones, dicc, vocabulario)).items():
            i = texto.find(pal)
            contexto = texto[max(0, i - 40):i + len(pal) + 40].replace("\n", " ")
            lineas.append(f"{p}  {pal}{f' ×{veces}' if veces > 1 else ''} | {contexto}")
            total += 1
    carpeta.dudas.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return total


def hoja_para_ver(carpeta: Carpeta, palabras: Iterable[str], salida: Path) -> int:
    """Junta en una imagen el renglón de la página donde aparece cada palabra (lo ubica con las
    cajas del OCR de Windows; si Windows no la leyó, aproxima la altura dentro de la región)."""
    segs = leer_json(carpeta.segmentos)
    indice = leer_json(carpeta.ocr_indice)
    cache = leer_json(carpeta.ocr_cache, {})
    tiras: list[tuple[str, Image.Image]] = []
    for pal in palabras:
        hallada = _ubicar(carpeta, segs, indice, cache, pal)
        if hallada:
            tiras.append(hallada)
    if not tiras:
        return 0
    ancho = max(t.width for _, t in tiras)
    hoja = Image.new("RGB", (ancho, sum(t.height + 24 for _, t in tiras)), "white")
    d = ImageDraw.Draw(hoja)
    y = 0
    for nombre, tira in tiras:
        d.text((4, y + 4), nombre, fill="red")
        hoja.paste(tira, (0, y + 24))
        y += tira.height + 24
    salida.parent.mkdir(parents=True, exist_ok=True)
    hoja.save(salida)
    return len(tiras)


def _ubicar(carpeta: Carpeta, segs: dict, indice: dict, cache: dict, pal: str
            ) -> tuple[str, Image.Image] | None:
    for p in sorted(indice):
        for i, claves in indice[p].items():
            texto = " ".join(cache.get(k, "") for k in claves)
            if pal not in texto:
                continue
            b = segs[p]["elems"][int(i)]["bbox"]
            img = Image.open(carpeta.paginas / f"{p}.png").convert("RGB")
            y = None
            for r in palabras_windows(carpeta, p):
                for w in r["words"]:
                    if normal(w["t"]) == normal(pal) and b[1] - 10 <= w["y"] <= b[3] + 10:
                        y = w["y"] + w["h"] / 2
                        break
                if y is not None:
                    break
            if y is None:
                y = b[1] + texto.find(pal) / max(1, len(texto)) * (b[3] - b[1])
            caja = (max(0, int(b[0]) - 10), max(0, int(y) - 70), min(img.width, int(b[2]) + 10), int(y) + 70)
            return f"{p}  {pal}", img.crop(caja)
    return None
