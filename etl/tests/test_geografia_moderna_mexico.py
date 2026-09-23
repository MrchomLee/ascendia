"""Perfil `geografia_moderna_mexico`: el temario de la imagen, como Capítulo › Tema.

`Geografia_Moderna_de_Mexico_extraccion.pdf` (Tamayo, Trillas, 15a. ed. 2021):
Cap. 1 con cuatro temas, Cap. 3 con uno, y Caps. 4 y 5 completos. La secuencia
imita la extracción real de Docling: el título del libro antes del Cap. 1, los
encabezados en mayúsculas, el Cap. 3 pegado a su tema en un solo encabezado y
un subtítulo "GENERALIDADES" dentro de Litorales que no es el Cap. 1.
"""

from etl.extraction.types import ElementKind, RawElement
from etl.hierarchy.assembler import HierarchyAssembler
from etl.hierarchy.profile import get_profile

H, N, L, T = ElementKind.HEADING, ElementKind.NARRATIVE, ElementKind.LIST_ITEM, ElementKind.TABLE

ELEMENTS = [
    (1, H, "Geografía Moderna de México"),                                         # 0  título del libro
    (1, H, "CAP. 1. GENERALIDADES"),                                               # 1
    (1, H, "SITUACIÓN GEOGRÁFICA"),                                                # 2
    (1, N, "México se localiza en el hemisferio norte."),                          # 3
    (1, H, "Frontera norte"),                                                      # 4
    (2, L, "1. A partir de la desembocadura del río Bravo en el Golfo."),          # 5
    (3, H, "EXTENSIÓN"),                                                           # 6
    (3, N, "La superficie del territorio nacional es de 1 967 183 km²."),          # 7
    (4, H, "DIVISIÓN POLÍTICA"),                                                   # 8
    (5, T, "| Estado | Capital |\n|---|---|\n| Aguascalientes | Aguascalientes |"),  # 9
    (5, H, "REPRESENTACIÓN CARTOGRÁFICA"),                                         # 10
    (5, N, "Las proyecciones representan la superficie terrestre en un plano."),   # 11
    (6, H, "CAP. 2. HIDROGRAFÍA"),                                                 # 12 no está en la imagen
    (6, N, "Los ríos de México se agrupan en tres vertientes."),                   # 13
    (6, H, "CAP. 3. GEOMORFOLOGÍA DE LA REPÚBLICA MEXICANA UNIDADES OROGÉNICAS"),  # 14
    (6, H, "Sierra Madre Occidental"),                                             # 15
    (6, N, "Es el sistema montañoso más extenso del país."),                       # 16
    (12, H, "CAP. 4. LITORALES"),                                                  # 17
    (12, H, "GENERALIDADES"),                                                      # 18
    (12, N, "México tiene litorales en el Pacífico y en el Atlántico."),           # 19
    (12, H, "Costas del océano Pacífico"),                                         # 20
    (16, H, "CAP. 5. ISLAS"),                                                      # 21
    (16, H, "ISLAS DEL GOLFO DE CALIFORNIA"),                                      # 22
    (17, N, "Tiburón es la isla más grande de México."),                           # 23
]


def _tree():
    elements = [
        RawElement(page_number=p, physical_page_index=p - 1, kind=k, text=t) for p, k, t in ELEMENTS
    ]
    return HierarchyAssembler(get_profile("geografia_moderna_mexico"), prefer_toc=False).assemble(
        elements, toc=None
    )


def test_el_arbol_es_el_de_la_imagen():
    assert [(n.level_label, n.ordinal, n.title) for n in _tree().nodes] == [
        ("Capítulo", "1", "Generalidades"),
        ("Tema", "1", "Situación Geográfica"),
        ("Tema", "2", "Extensión"),
        ("Tema", "3", "División Política"),
        ("Tema", "4", "Representación Cartográfica"),
        ("Capítulo", "3", "Geomorfología de la República Mexicana"),
        ("Tema", "1", "Unidades Orogénicas"),
        ("Capítulo", "4", "Litorales"),
        ("Capítulo", "5", "Islas"),
    ]


def test_cada_tema_cuelga_de_su_capitulo():
    nodes = _tree().nodes
    cap1, cap3, cap4, cap5 = nodes[0], nodes[5], nodes[7], nodes[8]

    assert [n.parent_local_id for n in nodes[1:5]] == [cap1.local_id] * 4
    assert nodes[6].parent_local_id == cap3.local_id
    assert [c.parent_local_id for c in (cap1, cap3, cap4, cap5)] == [None] * 4
    assert nodes[6].breadcrumb == (
        "Capítulo 3 — Geomorfología de la República Mexicana › Tema 1 — Unidades Orogénicas"
    )


def test_los_subtitulos_y_los_capitulos_completos_quedan_como_texto():
    assert [n.body_element_indices for n in _tree().nodes] == [
        [],                # Cap. 1
        [3, 4, 5],         # Situación Geográfica, con "Frontera norte"
        [7],               # Extensión
        [9],               # División Política, con su tabla
        [11],              # Representación Cartográfica
        [],                # Cap. 3
        [15, 16],          # Unidades Orogénicas
        [18, 19, 20],      # Litorales completo, con su "GENERALIDADES"
        [22, 23],          # Islas completo
    ]


def test_lo_que_no_esta_en_la_imagen_queda_fuera():
    tree = _tree()

    assert tree.unattached_element_indices == []
    # título del libro (0) y el Cap. 2 con su texto (12, 13)
    assert tree.dropped_element_count == 3
