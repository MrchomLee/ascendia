"""Perfil `taller_lectura_redaccion`: solo el temario pedido, como Bloque › Parte.

`Proceso_comunicativo_y_escritura.pdf` (recorte del Taller de Lectura y
Redacción 1, Zarzar). Entran Bloque 1 (1.1, 1.2) y Bloque 3 (3.1, 3.2, 3.3);
el índice, la introducción del Bloque 3 y los temas 3.4 y 3.5 quedan fuera.
La secuencia imita la extracción real de Docling: en el Bloque 3 se pierde la
línea "BLOQUE 3" y solo llega el título.
"""

from etl.extraction.types import ElementKind, RawElement
from etl.hierarchy.assembler import HierarchyAssembler
from etl.hierarchy.profile import get_profile

H, N = ElementKind.HEADING, ElementKind.NARRATIVE

ELEMENTS = [
    (1, H, "Contenido"),                                                           # 0
    (2, N, "3.5  Conectores discursivos  ........................................ 25"),  # 1
    (3, H, "BLOQUE 1"),                                                            # 2
    (3, H, "Proceso comunicativo"),                                                # 3
    (3, H, "1.1  Los elementos del proceso comunicativo"),                         # 4
    (3, N, "El lenguaje oral es más completo que el lenguaje mímico."),            # 5
    (7, H, "1.2  Funciones del lenguaje"),                                         # 6
    (8, N, "La función poética se centra en el mensaje."),                         # 7
    (12, H, "Proceso de escritura"),                                               # 8
    (12, H, "Introducción"),                                                       # 9
    (12, N, "Leer un texto es mucho más sencillo que escribir un texto."),         # 10
    (12, H, "3.1  Principios básicos de la sintaxis"),                             # 11
    (12, N, "La palabra sintaxis proviene del griego."),                           # 12
    (13, H, "3.2  Reglas de acentuación"),                                         # 13
    (14, N, "Las palabras agudas llevan tilde si terminan en n, s o vocal."),      # 14
    (18, H, "3.3  Reglas de puntuación"),                                          # 15
    (19, N, "El punto y aparte separa párrafos."),                                 # 16
    (20, H, "3.4  Propiedades de la redacción (coherencia, cohesión y adecuación)"),  # 17
    (21, N, "La primera característica de un texto es la unidad."),                # 18
    (24, H, "3.5  Conectores discursivos"),                                        # 19
    (25, N, "Los conectores enlazan las ideas de un texto."),                      # 20
]


def _tree():
    elements = [
        RawElement(page_number=p, physical_page_index=p - 1, kind=k, text=t) for p, k, t in ELEMENTS
    ]
    return HierarchyAssembler(get_profile("taller_lectura_redaccion"), prefer_toc=False).assemble(
        elements, toc=None
    )


def test_solo_quedan_los_bloques_y_partes_de_la_imagen():
    assert [(n.level_label, n.ordinal, n.title) for n in _tree().nodes] == [
        ("Bloque", "1", "Proceso comunicativo"),
        ("Parte", "1.1", "Los elementos del proceso comunicativo"),
        ("Parte", "1.2", "Funciones del lenguaje"),
        ("Bloque", "3", "Proceso de escritura"),
        ("Parte", "3.1", "Principios básicos de la sintaxis"),
        ("Parte", "3.2", "Reglas de acentuación"),
        ("Parte", "3.3", "Reglas de puntuación"),
    ]


def test_cada_parte_cuelga_de_su_bloque():
    by_ordinal = {n.ordinal: n for n in _tree().nodes}

    for parte, bloque in [("1.1", "1"), ("1.2", "1"), ("3.1", "3"), ("3.2", "3"), ("3.3", "3")]:
        assert by_ordinal[parte].parent_local_id == by_ordinal[bloque].local_id
    assert by_ordinal["1"].parent_local_id is None and by_ordinal["3"].parent_local_id is None


def test_cada_parte_lleva_solo_su_texto():
    by_ordinal = {n.ordinal: n for n in _tree().nodes}

    assert {o: by_ordinal[o].body_element_indices for o in ("1.1", "1.2", "3.1", "3.2", "3.3")} == {
        "1.1": [5], "1.2": [7], "3.1": [12], "3.2": [14], "3.3": [16],  # 3.3 sin el texto de 3.4 ni 3.5
    }
    assert by_ordinal["3"].body_element_indices == []  # sin la introducción del bloque
    assert by_ordinal["3"].page_start == 12


def test_lo_que_no_esta_en_la_imagen_no_queda_en_ningun_nodo():
    tree = _tree()

    assert tree.unattached_element_indices == []
    # índice (0, 1), "BLOQUE 1" (2), introducción (9, 10), 3.4 (17, 18) y 3.5 (19, 20)
    assert tree.dropped_element_count == 9
