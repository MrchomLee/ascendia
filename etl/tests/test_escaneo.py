"""Pruebas del escaneo que no necesitan GPU ni el OCR de Windows."""

import io
import json

import pymupdf
import pytest
from PIL import Image, ImageDraw

from etl.escaneo.borrador import armar_borrador, limpiar, orden_de_lectura, unir_trozos
from etl.escaneo.carpeta import Carpeta, escribir_json, leer_rango, nombre_pagina
from etl.escaneo.dudas import dudosas_de_pagina, en_diccionario, listar_dudas, paginas_del_borrador
from etl.escaneo.maquetacion import segmentar, segmentar_pagina
from etl.escaneo.paginas import extraer_paginas
from etl.escaneo.recortes import clave, partir, recortar


def reg(label, bbox, conf=0.9):
    return {"label": label, "conf": conf, "bbox": bbox}


def el(bbox, kind="text", keep=True, why=""):
    return {"bbox": bbox, "label": "Text", "kind": kind, "keep": keep, "why": why}


# --- rangos de páginas -------------------------------------------------------------------------

def test_rango_con_tramos_y_sueltas():
    assert leer_rango("3-5,9", 20) == [3, 4, 5, 9]


def test_rango_vacio_son_todas():
    assert leer_rango(None, 3) == [1, 2, 3]


@pytest.mark.parametrize("texto", ["5-3", "0", "21", "a-b"])
def test_rango_invalido(texto):
    with pytest.raises(ValueError):
        leer_rango(texto, 20)


def test_nombre_de_pagina():
    assert nombre_pagina(12) == "p0012"


# --- páginas -----------------------------------------------------------------------------------

def _pdf_escaneado(tmp_path):
    img = Image.new("RGB", (400, 600), "white")
    ImageDraw.Draw(img).rectangle([50, 50, 350, 80], fill="black")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    doc = pymupdf.open()
    for _ in range(3):
        page = doc.new_page(width=400, height=600)
        page.insert_image(page.rect, stream=buf.getvalue())
    ruta = tmp_path / "libro.pdf"
    doc.save(ruta)
    return ruta


def test_extraer_paginas_toma_la_imagen_al_doble(tmp_path):
    pdf = _pdf_escaneado(tmp_path)
    c = Carpeta(tmp_path / "trabajo")
    assert extraer_paginas(pdf, c, "2-3") == ["p0002", "p0003"]
    assert Image.open(c.paginas / "p0002.png").size == (800, 1200)
    assert extraer_paginas(pdf, c, "2-3") == []          # ya estaban


def test_pagina_sin_escaneo_se_dibuja(tmp_path):
    doc = pymupdf.open()
    doc.new_page(width=100, height=200).insert_text((10, 50), "Hola")
    pdf = tmp_path / "texto.pdf"
    doc.save(pdf)
    c = Carpeta(tmp_path / "t")
    extraer_paginas(pdf, c)
    assert Image.open(c.paginas / "p0001.png").size == (400, 800)


# --- segmentación ------------------------------------------------------------------------------

def test_segmentar_descarta_rotulos_figuras_y_repetidas():
    elems = segmentar_pagina([
        reg("Page-header", [0, 0, 500, 30]),
        reg("Text", [10, 100, 500, 300], 0.95),
        reg("Text", [12, 102, 498, 298], 0.5),          # la misma región predicha dos veces
        reg("Picture", [10, 400, 500, 800]),
        reg("Text", [50, 500, 200, 520]),                # rótulo dentro de la figura
        reg("Section-header", [10, 50, 300, 80]),
    ])
    assert [(e["label"], e["keep"], e["why"]) for e in elems] == [
        ("Page-header", False, "rotulo"), ("Section-header", True, ""), ("Text", True, ""),
        ("Picture", False, "fig"), ("Text", False, "contexto")]


def test_segmentar_aplica_ajustes(tmp_path):
    c = Carpeta(tmp_path)
    escribir_json(c.maquetacion, {"p0001": [reg("Text", [0, 0, 100, 100])]})
    escribir_json(c.ajustes, {"p0001": {"0": {"keep": False, "why": "a mano"}}})
    assert segmentar(c) == (1, 0)


# --- recortes ----------------------------------------------------------------------------------

def _renglones(alto, cada=40):
    img = Image.new("RGB", (300, alto), "white")
    d = ImageDraw.Draw(img)
    for y in range(10, alto - 20, cada):
        d.rectangle([10, y, 290, y + 18], fill="black")
    return img


def test_partir_corta_en_renglones_en_blanco():
    trozos = partir(_renglones(2500), alto_maximo=1000)
    assert len(trozos) >= 3
    assert all(t.height <= 1000 for _, t in trozos)
    assert sum(t.height for _, t in trozos) == 2500
    tops = [top for top, _ in trozos]
    assert tops == sorted(tops) and tops[0] == 0


def test_recortar_blanquea_lo_descartado():
    img = Image.new("RGB", (200, 200), "black")
    texto = el([0, 0, 200, 200])
    figura = el([0, 0, 100, 100], kind="otro", keep=False, why="fig")
    crop = recortar(img, texto, [texto, figura])
    assert crop.getpixel((50, 50)) == (255, 255, 255)
    assert crop.getpixel((150, 150)) == (0, 0, 0)


def test_clave_depende_del_contenido_y_la_tarea():
    a, b = Image.new("RGB", (10, 10), "white"), Image.new("RGB", (10, 10), "black")
    assert clave(a, "ocr") == clave(a.copy(), "ocr")
    assert clave(a, "ocr") != clave(b, "ocr") != clave(b, "table")


# --- borrador ----------------------------------------------------------------------------------

def test_orden_de_lectura_dos_columnas_con_titulo_ancho():
    elems = [el([520, 200, 980, 400]), el([20, 200, 480, 400]), el([20, 50, 980, 100], kind="title"),
             el([20, 500, 480, 600])]
    assert orden_de_lectura(elems, 1000) == [2, 1, 3, 0]


def test_unir_trozos_quita_el_punto_falso():
    assert unir_trozos(["las células.", "que forman el tejido."]) == "las células que forman el tejido."
    assert unir_trozos(["Fin del párrafo.", "Otro párrafo."]) == "Fin del párrafo. Otro párrafo."


def test_limpiar_quita_guion_de_corte():
    assert limpiar("la neu-\nrona y\nel axón") == "la neurona y el axón"


def test_armar_borrador(tmp_path):
    c = Carpeta(tmp_path)
    c.paginas.mkdir()
    Image.new("RGB", (1000, 1400), "white").save(c.paginas / "p0003.png")
    escribir_json(c.segmentos, {"p0003": {"elems": [el([20, 50, 980, 100], kind="title"),
                                                    el([20, 200, 980, 400])]}})
    escribir_json(c.ocr_indice, {"p0003": {"0": ["k1"], "1": ["k2", "k3"]}})
    escribir_json(c.ocr_cache, {"k1": "Capítulo 2", "k2": "La célula.", "k3": "es la unidad."})
    assert armar_borrador(c) == 2
    assert c.borrador.read_text(encoding="utf-8") == "[p0003]\n\n\n### Capítulo 2\n\nLa célula es la unidad.\n"


# --- dudas -------------------------------------------------------------------------------------

def _renglon(texto):
    return {"text": texto, "words": [{"t": w, "x": 0, "y": 0, "w": 1, "h": 1} for w in texto.split()]}


def test_dudosas_son_las_que_windows_no_leyo():
    renglones = [_renglon("La hemoglobina transporta oxígeno")]
    assert dudosas_de_pagina("La hemoglobin transporta oxígeno.", renglones) == ["hemoglobin"]


class _Dicc:
    def __contains__(self, w):
        return w in {"transporta", "sangre"}


def test_dudosas_descarta_las_del_diccionario():
    assert dudosas_de_pagina("transporta sangre", [_renglon("otra cosa")], _Dicc()) == []


class _Base:
    def __contains__(self, w):
        return w in {"valor", "considerar", "crear", "vinculado"}


@pytest.mark.parametrize("w", ["valores", "considera", "crearse", "considerarán", "vinculadas"])
def test_formas_que_se_reconocen_por_su_base(w):
    assert en_diccionario(w, _Base())


def test_palabra_mal_leida_no_se_reconoce():
    assert not en_diccionario("obrenga", _Base())


def test_dudosas_descarta_lo_que_windows_leyo_en_otra_pagina():
    assert dudosas_de_pagina("los valores", [_renglon("los valotes")], vocabulario={"valores"}) == []


def test_listar_dudas(tmp_path):
    c = Carpeta(tmp_path)
    c.borrador.write_text("[p0001]\n\nLa hemoglobin.\n\n[p0002]\n\nTexto.\n", encoding="utf-8")
    c.windows.mkdir()
    (c.windows / "p0001.json").write_text(json.dumps({"lines": [_renglon("La hemoglobina.")]}), encoding="utf-8")
    assert paginas_del_borrador(c.borrador.read_text(encoding="utf-8"))[0][0] == "p0001"
    listar_dudas(c)
    texto = c.dudas.read_text(encoding="utf-8")
    assert "p0001  hemoglobin |" in texto
    assert "p0002  (sin OCR de Windows" in texto
