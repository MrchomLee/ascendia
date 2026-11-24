"""Paso 2: las regiones de cada página con el modelo de maquetación de Docling, y su clasificación.

`detectar_regiones` corre el modelo (GPU si hay) y guarda las predicciones crudas.
`segmentar` decide qué se lee: quita las predicciones repetidas, conserva texto, listas, títulos y
tablas, y descarta cabezales, folios, figuras, pies de figura, notas al pie y lo que cae dentro de una
figura. Las correcciones a mano van en ajustes.json: {"p0012": {"3": {"keep": false, "why": "fig"}}}.
"""

from __future__ import annotations

import time
from typing import Any, Callable

from PIL import Image

from etl.escaneo.carpeta import Carpeta, escribir_json, leer_json

CONSERVAR = {"Text": "text", "List-item": "text", "Section-header": "title", "Table": "table",
             "Formula": "formula"}
MOTIVO = {"Page-header": "rotulo", "Page-footer": "rotulo", "Picture": "fig", "Caption": "cap",
          "Footnote": "nota", "Document Index": "rotulo", "Form": "fig"}
CONFIANZA_MINIMA = 0.3


def area(b: list[float]) -> float:
    return max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])


def interseccion(a: list[float], b: list[float]) -> float:
    return area([max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])])


def segmentar_pagina(regiones: list[dict[str, Any]], ajustes: dict[str, dict[str, Any]] | None = None
                     ) -> list[dict[str, Any]]:
    """Regiones crudas de una página → [{bbox, label, kind, keep, why}] de arriba abajo."""
    elegidas: list[dict[str, Any]] = []
    for r in sorted(regiones, key=lambda r: -r["conf"]):
        # Una predicción repetida se encima mucho con otra ya elegida; lo que está dentro de una
        # figura no cuenta como repetido de la figura: se marca después como «contexto».
        if any((r["label"] == "Picture") == (e["label"] == "Picture")
               and interseccion(r["bbox"], e["bbox"]) > 0.6 * min(area(r["bbox"]), area(e["bbox"]))
               for e in elegidas):
            continue
        elegidas.append(r)
    figuras = [r["bbox"] for r in elegidas if r["label"] == "Picture"]
    elems = []
    for r in sorted(elegidas, key=lambda r: (r["bbox"][1], r["bbox"][0])):
        b, lab = r["bbox"], r["label"]
        dentro_fig = lab != "Picture" and any(interseccion(b, f) > 0.5 * area(b) for f in figuras)
        keep = lab in CONSERVAR and not dentro_fig and r["conf"] >= CONFIANZA_MINIMA
        why = "contexto" if dentro_fig else MOTIVO.get(lab, "" if keep else "baja")
        elems.append({"bbox": b, "label": lab, "kind": CONSERVAR.get(lab, "otro"), "keep": keep, "why": why})
    for i, cambio in (ajustes or {}).items():
        if int(i) < len(elems):
            elems[int(i)].update(cambio)
    return elems


def segmentar(carpeta: Carpeta) -> tuple[int, int]:
    """maquetacion.json (+ ajustes.json) → segmentos.json. Devuelve (páginas, regiones a leer)."""
    crudas = leer_json(carpeta.maquetacion)
    ajustes = leer_json(carpeta.ajustes, {})
    salida = {p: {"elems": segmentar_pagina(r, ajustes.get(p))} for p, r in sorted(crudas.items())}
    escribir_json(carpeta.segmentos, salida)
    return len(salida), sum(e["keep"] for r in salida.values() for e in r["elems"])


def _predictor() -> Any:
    import torch
    from docling.datamodel.pipeline_options import LayoutOptions
    from docling.models.stages.layout.layout_model import LayoutModel
    from docling_ibm_models.layoutmodel.layout_predictor import LayoutPredictor

    spec = LayoutOptions().model_spec
    ruta = LayoutModel.download_models(layout_model_config=spec) / spec.model_path
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    return LayoutPredictor(artifact_path=str(ruta), device=dispositivo, num_threads=4, base_threshold=0.3)


def detectar_regiones(carpeta: Carpeta, paginas: list[str] | None = None,
                      aviso: Callable[[str], None] = print) -> int:
    """Corre la maquetación de Docling sobre paginas/ y la guarda en maquetacion.json.
    Sin `paginas`, solo las que aún no tienen regiones."""
    hechas = leer_json(carpeta.maquetacion, {})
    todas = carpeta.lista_paginas()
    pendientes = paginas if paginas else [p for p in todas if p not in hechas]
    if not pendientes:
        return 0
    pred = _predictor()
    t0 = time.time()
    for i in range(0, len(pendientes), 8):
        lote = pendientes[i:i + 8]
        imagenes = [Image.open(carpeta.paginas / f"{p}.png").convert("RGB") for p in lote]
        for p, preds in zip(lote, pred.predict_batch(imagenes)):
            hechas[p] = [{"label": x["label"], "conf": round(x["confidence"], 3),
                          "bbox": [round(x["l"]), round(x["t"]), round(x["r"]), round(x["b"])]} for x in preds]
        escribir_json(carpeta.maquetacion, hechas)
        aviso(f"maquetación {i + len(lote)}/{len(pendientes)}  {time.time() - t0:.0f}s")
    return len(pendientes)
