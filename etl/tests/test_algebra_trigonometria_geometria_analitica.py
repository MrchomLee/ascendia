"""Perfil `algebra_trigonometria_geometria_analitica`: los cuatro capítulos de la imagen.

`Algebra_trigonometria_geometria_analitica_Caps_4_8_9_12.pdf` (Zill y Dewar,
McGraw-Hill, 3a. ed. 2012). La secuencia imita la extracción real de Docling:
portada, capítulos en mayúsculas **sin número** (el número sale del temario) y
secciones que repiten el título de su capítulo pero llevan número delante
("8.2 Trigonometría del triángulo rectángulo"), que no abren un capítulo.
"""

from etl.extraction.types import ElementKind, RawElement
from etl.hierarchy.assembler import HierarchyAssembler
from etl.hierarchy.profile import get_profile

H, N = ElementKind.HEADING, ElementKind.NARRATIVE

ELEMENTS = [
    (1, H, "Álgebra, trigonometría y geometría analítica"),                        # 0  portada
    (1, N, "Capítulos 4, 8, 9 y 12 -transcripción literal"),                       # 1  portada
    (2, H, "SISTEMA DE COORDENADAS RECTANGULARES Y GRÁFICAS"),                     # 2
    (2, H, "En este capítulo"),                                                    # 3
    (2, H, "4.1 El sistema de coordenadas rectangulares"),                         # 4
    (4, H, "Teorema 4.1.1 Fórmula de la distancia"),                               # 5
    (4, N, "La distancia entre P1(x1, y1) y P2(x2, y2) es d(P1, P2) = √((x2 − x1)² + (y2 − y1)²)."),  # 6
    (18, H, "TRIGONOMETRÍA DEL TRIÁNGULO RECTÁNGULO"),                             # 7
    (18, H, "8.1 Ángulos y sus medidas"),                                          # 8
    (23, H, "8.2 Trigonometría del triángulo rectángulo"),                         # 9  no es el capítulo
    (23, N, "En un triángulo rectángulo, sen θ = cat. op./hip."),                  # 10
    (37, H, "TRIGONOMETRÍA DEL CÍRCULO UNITARIO"),                                 # 11
    (38, H, "9.1 Las funciones circulares"),                                       # 12
    (69, H, "COORDENADAS POLARES"),                                                # 13
    (70, H, "12.1 Coordenadas polares"),                                           # 14 no es el capítulo
    (70, H, "EJEMPLO 1 Gráfica de puntos en coordenadas polares"),                 # 15
    (87, H, "12.5 Producto punto"),                                                # 16
    (87, N, "El producto punto de u = ⟨a1, b1⟩ y v = ⟨a2, b2⟩ es u · v = a1a2 + b1b2."),  # 17
]


def _tree():
    elements = [
        RawElement(page_number=p, physical_page_index=p - 1, kind=k, text=t) for p, k, t in ELEMENTS
    ]
    return HierarchyAssembler(
        get_profile("algebra_trigonometria_geometria_analitica"), prefer_toc=False
    ).assemble(elements, toc=None)


def test_el_arbol_son_los_cuatro_capitulos_de_la_imagen():
    nodes = _tree().nodes

    assert [(n.level_label, n.ordinal, n.title) for n in nodes] == [
        ("Capítulo", "4", "Sistema de Coordenadas Rectangulares y Gráficas"),
        ("Capítulo", "8", "Trigonometría del Triángulo Rectángulo"),
        ("Capítulo", "9", "Trigonometría del Círculo Unitario"),
        ("Capítulo", "12", "Coordenadas Polares"),
    ]
    assert [n.parent_local_id for n in nodes] == [None] * 4
    assert [n.page_start for n in nodes] == [2, 18, 37, 69]


def test_secciones_ejemplos_y_teoremas_quedan_en_el_cuerpo_de_su_capitulo():
    assert [n.body_element_indices for n in _tree().nodes] == [
        [3, 4, 5, 6],
        [8, 9, 10],
        [12],
        [14, 15, 16, 17],
    ]


def test_la_portada_queda_fuera():
    tree = _tree()

    assert tree.unattached_element_indices == []
    assert tree.dropped_element_count == 2
