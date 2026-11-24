"""La carpeta de trabajo de un escaneo y los nombres de sus archivos."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

RAIZ_ESCANEOS = Path("data/processed/escaneo")


def nombre_pagina(numero: int) -> str:
    """Página del PDF (1 = la primera, como la cuenta el visor) → «p0012»."""
    return f"p{numero:04d}"


def numero_pagina(nombre: str) -> int:
    return int(nombre[1:])


def leer_rango(texto: str | None, total: int) -> list[int]:
    """«3-10,15» → [3, …, 10, 15] (páginas del PDF, desde 1). Sin rango, todas."""
    if not texto:
        return list(range(1, total + 1))
    paginas: set[int] = set()
    for parte in texto.split(","):
        parte = parte.strip()
        if not parte:
            continue
        m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", parte)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a > b:
                raise ValueError(f"rango al revés: {parte}")
            paginas.update(range(a, b + 1))
        elif parte.isdigit():
            paginas.add(int(parte))
        else:
            raise ValueError(f"no entiendo el rango «{parte}»; usa por ejemplo 3-10,15")
    fuera = [p for p in paginas if p < 1 or p > total]
    if fuera:
        raise ValueError(f"el PDF tiene {total} páginas; fuera de rango: {sorted(fuera)[:5]}")
    return sorted(paginas)


@dataclass(frozen=True)
class Carpeta:
    """Rutas de un escaneo. Todo es JSON o PNG dentro de `raiz`."""

    raiz: Path

    @classmethod
    def para_pdf(cls, pdf: Path, carpeta: Path | None = None) -> Carpeta:
        return cls(Path(carpeta) if carpeta else RAIZ_ESCANEOS / pdf.stem)

    @property
    def paginas(self) -> Path:          # imágenes de página ya ampliadas: pNNNN.png
        return self.raiz / "paginas"

    @property
    def windows(self) -> Path:          # OCR de Windows: pNNNN.json
        return self.raiz / "windows"

    @property
    def maquetacion(self) -> Path:      # regiones crudas de Docling
        return self.raiz / "maquetacion.json"

    @property
    def segmentos(self) -> Path:        # regiones clasificadas, en orden de lectura
        return self.raiz / "segmentos.json"

    @property
    def ajustes(self) -> Path:          # correcciones a mano de la segmentación (opcional)
        return self.raiz / "ajustes.json"

    @property
    def ocr_indice(self) -> Path:       # {página: {región: [claves de caché]}}
        return self.raiz / "ocr_indice.json"

    @property
    def ocr_cache(self) -> Path:        # {clave: texto de PaddleOCR-VL}
        return self.raiz / "ocr_cache.json"

    @property
    def borrador(self) -> Path:
        return self.raiz / "borrador.md"

    @property
    def dudas(self) -> Path:
        return self.raiz / "dudas.txt"

    def lista_paginas(self) -> list[str]:
        return sorted(p.stem for p in self.paginas.glob("p*.png"))


def leer_json(ruta: Path, defecto: Any = None) -> Any:
    if not ruta.exists():
        if defecto is not None:
            return defecto
        raise FileNotFoundError(f"falta {ruta}: corre antes el paso que lo genera")
    return json.loads(ruta.read_text(encoding="utf-8-sig"))


def escribir_json(ruta: Path, datos: Any) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = ruta.with_suffix(ruta.suffix + ".tmp")
    tmp.write_text(json.dumps(datos, ensure_ascii=False, indent=0), encoding="utf-8")
    tmp.replace(ruta)
