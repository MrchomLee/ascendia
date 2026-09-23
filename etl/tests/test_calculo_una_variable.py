"""Perfil `calculo_una_variable`: los tres capítulos completos de la imagen.

`Calculo_Una_Variable_Caps_1_2_3.pdf` (Thomas y Weir, Pearson, 13a. ed. 2015).
La secuencia imita la extracción real de Docling: la portada antes del primer
capítulo y los capítulos como encabezados en mayúsculas **sin número**
("FUNCIONES"), así que se reconocen por su título y el número sale del temario.
Secciones ("1.1 …"), subtítulos y bloques "DEFINICIÓN" quedan en el cuerpo.
"""

from etl.extraction.types import ElementKind, RawElement
from etl.hierarchy.assembler import HierarchyAssembler
from etl.hierarchy.profile import get_profile

H, N, L = ElementKind.HEADING, ElementKind.NARRATIVE, ElementKind.LIST_ITEM

ELEMENTS = [
    (1, H, "Cálculo, una variable"),                                                 # 0  portada
    (1, N, "Capítulos 1, 2 y 3 -transcripción literal"),                             # 1  portada
    (2, H, "FUNCIONES"),                                                             # 2
    (2, N, "INTRODUCCIÓN Las funciones son fundamentales en el estudio del cálculo."),  # 3
    (2, H, "1.1 Las funciones y sus gráficas"),                                      # 4
    (2, H, "DEFINICIÓN"),                                                            # 5
    (2, N, "Una función f de un conjunto D a un conjunto Y asigna un único f(x)."),  # 6
    (14, H, "LÍMITES Y CONTINUIDAD"),                                                # 7
    (16, H, "2.2 Límite de una función y leyes de los límites"),                     # 8
    (17, L, "1. Regla de la suma: lím 𝑥→𝑐 (ƒ( x ) + g ( x )) = L + M"),              # 9
    (23, H, "Funciones continuas"),                                                  # 10
    (29, H, "DERIVADAS"),                                                            # 11
    (38, H, "Derivadas en economía"),                                                # 12
    (40, H, "3.6 La regla de la cadena"),                                            # 13
    (40, N, "La derivada de una composición es el producto de las derivadas."),      # 14
]


def _tree():
    elements = [
        RawElement(page_number=p, physical_page_index=p - 1, kind=k, text=t) for p, k, t in ELEMENTS
    ]
    return HierarchyAssembler(get_profile("calculo_una_variable"), prefer_toc=False).assemble(
        elements, toc=None
    )


def test_el_arbol_son_los_tres_capitulos_de_la_imagen():
    nodes = _tree().nodes

    assert [(n.level_label, n.ordinal, n.title) for n in nodes] == [
        ("Capítulo", "1", "Funciones"),
        ("Capítulo", "2", "Límites y continuidad"),
        ("Capítulo", "3", "Derivadas"),
    ]
    assert [n.parent_local_id for n in nodes] == [None] * 3
    assert [n.page_start for n in nodes] == [2, 14, 29]


def test_secciones_y_subtitulos_quedan_en_el_cuerpo_de_su_capitulo():
    assert [n.body_element_indices for n in _tree().nodes] == [
        [3, 4, 5, 6],
        [8, 9, 10],
        [12, 13, 14],
    ]


def test_la_portada_queda_fuera():
    tree = _tree()

    assert tree.unattached_element_indices == []
    assert tree.dropped_element_count == 2
