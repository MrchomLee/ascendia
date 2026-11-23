"""Perfil `historia_universal`: el temario de la imagen, como Capítulo › Tema.

`Historia_Universal_Extracto.pdf` (Rodríguez Arvizu, Limusa, 3a. ed. 2017) es
solo el Capítulo 6. El Mundo Contemporáneo. Docling marca los ~60 subtítulos
como encabezados del mismo nivel, así que los cuatro temas se reconocen por su
título (el PDF no los numera ni respeta las mayúsculas del temario) y el resto
de subtítulos queda en el cuerpo de su tema.
"""

from etl.extraction.types import ElementKind, RawElement
from etl.hierarchy.assembler import HierarchyAssembler
from etl.hierarchy.profile import get_profile

H, N, L = ElementKind.HEADING, ElementKind.NARRATIVE, ElementKind.LIST_ITEM

ELEMENTS = [
    (1, H, "Capítulo 6. El Mundo Contemporáneo"),                                           # 0
    (1, H, "La Guerra Fría"),                                                               # 1
    (1, H, "Características del enfrentamiento entre Estados Unidos y la Unión Soviética"),  # 2
    (1, N, "Al término de la segunda conflagración mundial se configuró un nuevo orden."),  # 3
    (3, H, "La Guerra de Corea"),                                                           # 4
    (3, N, "El sudeste asiático representó una zona estratégica para los bloques."),        # 5
    (6, H, "Las grandes organizaciones internacionales"),                                   # 6
    (6, H, "La Organización de las Naciones Unidas"),                                       # 7
    (6, N, "La ONU se creó al término de la Segunda Guerra Mundial."),                      # 8
    (8, H, "Principales acontecimientos de nuestros días"),                                 # 9
    (8, H, "El conflicto del Golfo Pérsico (agosto de 1990-febrero de 1991)"),              # 10
    (9, H, "Kuwait"),                                                                       # 11
    (9, N, "Kuwait fue protectorado británico hasta 1961."),                                # 12
    (21, H, "La llegada del siglo XXI"),                                                    # 13
    (22, H, "Antecedentes"),                                                                # 14
    (22, N, "La Unión Europea surgió de la integración económica de posguerra."),           # 15
    (24, H, "China"),                                                                       # 16
    (24, L, "Reformas económicas a partir de 1978."),                                       # 17
]


def _tree():
    elements = [
        RawElement(page_number=p, physical_page_index=p - 1, kind=k, text=t) for p, k, t in ELEMENTS
    ]
    return HierarchyAssembler(get_profile("historia_universal"), prefer_toc=False).assemble(
        elements, toc=None
    )


def test_el_arbol_es_el_capitulo_y_sus_cuatro_temas():
    assert [(n.level_label, n.ordinal, n.title) for n in _tree().nodes] == [
        ("Capítulo", "6", "El Mundo Contemporáneo"),
        ("Tema", "1", "La Guerra Fría"),
        ("Tema", "2", "Las Grandes Organizaciones Internacionales"),
        ("Tema", "3", "Principales acontecimientos de nuestros días"),
        ("Tema", "4", "La llegada del Siglo XXI"),
    ]


def test_cada_tema_cuelga_del_capitulo():
    capitulo, *temas = _tree().nodes

    assert capitulo.parent_local_id is None and capitulo.level == 0
    assert [(t.parent_local_id, t.level) for t in temas] == [(capitulo.local_id, 1)] * 4
    assert temas[0].breadcrumb == "Capítulo 6 — El Mundo Contemporáneo › Tema 1 — La Guerra Fría"


def test_los_subtitulos_quedan_en_el_cuerpo_de_su_tema():
    tree = _tree()
    capitulo, *temas = tree.nodes

    assert [t.body_element_indices for t in temas] == [
        [2, 3, 4, 5],
        [7, 8],
        [10, 11, 12],
        [14, 15, 16, 17],
    ]
    assert capitulo.body_element_indices == []
    assert [t.page_start for t in temas] == [1, 6, 8, 21]
    assert tree.unattached_element_indices == []
    assert tree.dropped_element_count == 0
