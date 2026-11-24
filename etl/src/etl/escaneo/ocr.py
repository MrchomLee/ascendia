"""Pasos 3 y 4: leer las regiones con PaddleOCR-VL-1.5 (GPU) y la página entera con el OCR de Windows.

PaddleOCR-VL es el texto que se usa; el OCR de Windows solo sirve para contrastar, porque PaddleOCR
repite sus errores (pasa palabras al inglés, deja guiones dentro de la palabra, agrega puntos al
final de un recorte, lee mal los romanos en versalitas).
"""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import Any, Callable

from PIL import Image

from etl.escaneo.carpeta import Carpeta, escribir_json, leer_json
from etl.escaneo.recortes import clave, muy_chico, partir, recortar

MODELO = "PaddlePaddle/PaddleOCR-VL-1.5"
PROMPTS = {"ocr": "OCR:", "table": "Table Recognition:", "formula": "Formula Recognition:"}
TAREA = {"table": "table", "formula": "formula"}
WINOCR = Path(__file__).with_name("winocr.ps1")


class PaddleOCRVL:
    """PaddleOCR-VL-1.5 por lotes, en bfloat16 sobre CUDA y con la caché de atención activada
    (sin ella es unas diez veces más lento)."""

    def __init__(self) -> None:
        import torch
        from transformers import AutoModelForImageTextToText, AutoProcessor

        if not torch.cuda.is_available():
            raise RuntimeError("PaddleOCR-VL necesita una GPU NVIDIA con CUDA y no se encontró ninguna")
        self._torch = torch
        self.model = AutoModelForImageTextToText.from_pretrained(
            MODELO, dtype=torch.bfloat16, attn_implementation="sdpa").to("cuda").eval()
        self.proc = AutoProcessor.from_pretrained(MODELO)
        self.proc.tokenizer.padding_side = "left"

    def leer(self, items: list[tuple[Image.Image, str]], max_tokens: int = 2048) -> list[str]:
        with self._torch.inference_mode():
            convs = [[{"role": "user", "content": [{"type": "image", "image": im.convert("RGB")},
                                                   {"type": "text", "text": PROMPTS[t]}]}] for im, t in items]
            entrada = self.proc.apply_chat_template(convs, add_generation_prompt=True, tokenize=True,
                                                    return_dict=True, return_tensors="pt", padding=True).to("cuda")
            salida = self.model.generate(**entrada, max_new_tokens=max_tokens, do_sample=False, use_cache=True)
            n = entrada["input_ids"].shape[-1]
            return [self.proc.decode(o[n:], skip_special_tokens=True) for o in salida]


def planear_recortes(carpeta: Carpeta, cache: dict[str, str]
                     ) -> tuple[dict[str, dict[str, list[str]]], dict[str, tuple[Image.Image, str]]]:
    """Índice {página: {región: [claves]}} y los recortes que todavía no están en la caché."""
    segs = leer_json(carpeta.segmentos)
    indice: dict[str, dict[str, list[str]]] = {}
    nuevos: dict[str, tuple[Image.Image, str]] = {}
    for p, r in sorted(segs.items()):
        img = Image.open(carpeta.paginas / f"{p}.png").convert("RGB")
        indice[p] = {}
        for i, el in enumerate(r["elems"]):
            if not el["keep"] or muy_chico(el["bbox"]):
                continue
            tarea = TAREA.get(el["kind"], "ocr")
            crop = recortar(img, el, r["elems"])
            trozos = [(0, crop)] if tarea == "table" else partir(crop)
            claves = []
            for _, trozo in trozos:
                k = clave(trozo, tarea)
                claves.append(k)
                if k not in cache:
                    nuevos[k] = (trozo, tarea)
            indice[p][str(i)] = claves
    return indice, nuevos


def leer_con_paddle(carpeta: Carpeta, solo_planear: bool = False,
                    aviso: Callable[[str], None] = print) -> int:
    """segmentos.json → ocr_indice.json y ocr_cache.json. Devuelve cuántos recortes nuevos hubo."""
    cache: dict[str, str] = leer_json(carpeta.ocr_cache, {})
    indice, nuevos = planear_recortes(carpeta, cache)
    escribir_json(carpeta.ocr_indice, indice)
    aviso(f"recortes nuevos: {len(nuevos)} (en caché: {len(cache)})")
    if solo_planear or not nuevos:
        return len(nuevos)
    modelo = PaddleOCRVL()
    t0 = time.time()
    trabajos = sorted(nuevos.items(), key=lambda kv: kv[1][0].width * kv[1][0].height)
    tablas = [kv for kv in trabajos if kv[1][1] == "table"]
    texto = [kv for kv in trabajos if kv[1][1] != "table"]
    for grupo, lote, tokens in ((texto, 8, 2048), (tablas, 1, 6144)):
        for n in range(0, len(grupo), lote):
            parte = grupo[n:n + lote]
            for (k, _), t in zip(parte, modelo.leer([v for _, v in parte], max_tokens=tokens)):
                cache[k] = t
            escribir_json(carpeta.ocr_cache, cache)
            tipo = "tablas" if lote == 1 else "texto"
            aviso(f"{tipo} {n + len(parte)}/{len(grupo)}  {time.time() - t0:.0f}s")
    return len(nuevos)


def leer_con_windows(carpeta: Carpeta, idioma: str = "es-MX") -> int:
    """OCR de Windows (Windows.Media.Ocr) de cada página: windows/pNNNN.json con renglones y palabras.
    Solo funciona en Windows con el paquete de idioma instalado."""
    if os.name != "nt":
        raise RuntimeError("el OCR de Windows solo existe en Windows")
    carpeta.windows.mkdir(parents=True, exist_ok=True)
    pendientes = [p for p in carpeta.lista_paginas() if not (carpeta.windows / f"{p}.json").exists()]
    if not pendientes:
        return 0
    entrada = carpeta.raiz / "_windows_entrada"
    entrada.mkdir(exist_ok=True)
    try:
        for p in pendientes:
            destino = entrada / f"{p}.png"
            if not destino.exists():
                os.link(carpeta.paginas / f"{p}.png", destino)
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(WINOCR),
                        "-InDir", str(entrada.resolve()), "-Lang", idioma], check=True)
        for p in pendientes:
            (entrada / f"{p}.json").replace(carpeta.windows / f"{p}.json")
    finally:
        for f in entrada.glob("*"):
            f.unlink()
        entrada.rmdir()
    return len(pendientes)


def palabras_windows(carpeta: Carpeta, pagina: str) -> list[dict[str, Any]]:
    """Renglones del OCR de Windows de una página: [{text, words: [{t, x, y, w, h}]}]."""
    ruta = carpeta.windows / f"{pagina}.json"
    return leer_json(ruta)["lines"] if ruta.exists() else []
