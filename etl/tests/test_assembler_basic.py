from etl.extraction.types import ElementKind, RawElement
from etl.hierarchy.assembler import HierarchyAssembler
from etl.hierarchy.profile import get_profile


def _t(text: str, page: int, kind: ElementKind = ElementKind.TITLE) -> RawElement:
    return RawElement(page_number=page, physical_page_index=page - 1, kind=kind, text=text)


def test_assemble_from_body_simple_manual():
    """Manual profile builds PARTE → Capítulo → Sección hierarchy from body."""
    elements = [
        _t("PRIMERA PARTE", 1),
        _t("LA GUERRA", 1, ElementKind.NARRATIVE),
        _t("Capítulo I", 1),
        _t("Teoría de la Guerra", 1, ElementKind.NARRATIVE),
        _t("Primera Sección", 1),
        _t("Generalidades", 1, ElementKind.NARRATIVE),
        _t("Cuerpo del párrafo de generalidades.", 2, ElementKind.NARRATIVE),
        _t("Capítulo II", 5),
        _t("Principios de la Guerra", 5, ElementKind.NARRATIVE),
    ]
    tree = HierarchyAssembler(get_profile("manual")).assemble(elements, toc=None)
    assert len(tree.nodes) >= 4
    assert tree.profile_name == "manual"

    levels = {n.level_label for n in tree.nodes}
    assert "PARTE" in levels
    assert "Capítulo" in levels
    assert "Sección" in levels

    parents = {n.local_id: n.parent_local_id for n in tree.nodes}
    cap_i = next(n for n in tree.nodes if n.level_label == "Capítulo" and n.ordinal == "I")
    parte = next(n for n in tree.nodes if n.level_label == "PARTE")
    assert parents[cap_i.local_id] == parte.local_id


def test_assemble_codigo_legal_basic():
    """Legal-code profile builds Libro → Título → Capítulo → Artículo."""
    elements = [
        _t("LIBRO PRIMERO", 1),
        _t("De la organización y competencia", 1, ElementKind.NARRATIVE),
        _t("TITULO PRIMERO", 1),
        _t("De la organización de los tribunales militares", 1, ElementKind.NARRATIVE),
        _t("CAPITULO I", 1),
        _t("Disposiciones preliminares", 1, ElementKind.NARRATIVE),
        _t("Artículo 1o.- La administración de la justicia militar", 1, ElementKind.NARRATIVE),
        _t("corresponde al Tribunal Superior Militar.", 1, ElementKind.NARRATIVE),
        _t("Artículo 2o.- Son auxiliares de la administración", 2, ElementKind.NARRATIVE),
    ]
    tree = HierarchyAssembler(get_profile("codigo_legal")).assemble(elements, toc=None)
    assert tree.profile_name == "codigo_legal"

    labels = {n.level_label for n in tree.nodes}
    assert "LIBRO" in labels
    assert "TÍTULO" in labels
    assert "Capítulo" in labels
    assert "Artículo" in labels

    art1 = next(n for n in tree.nodes if n.level_label == "Artículo" and n.ordinal == "1o")
    cap1 = next(n for n in tree.nodes if n.level_label == "Capítulo")
    assert art1.parent_local_id == cap1.local_id


def test_assemble_codigo_legal_drops_page_headers():
    """Drop filters silence Cámara/DOF noise without losing real content."""
    elements = [
        _t("CÁMARA DE DIPUTADOS DEL H. CONGRESO DE LA UNIÓN", 1, ElementKind.NARRATIVE),
        _t("Última Reforma DOF 21-06-2018", 1, ElementKind.NARRATIVE),
        _t("LIBRO PRIMERO", 1),
        _t("CAPITULO I", 1),
        _t("Artículo 1o.- La administración de la justicia militar", 1, ElementKind.NARRATIVE),
        _t("1 de 141", 1, ElementKind.NARRATIVE),
    ]
    tree = HierarchyAssembler(get_profile("codigo_legal")).assemble(elements, toc=None)
    assert tree.dropped_element_count == 3  # Cámara + DOF banner + footer "1 de 141"
    labels = {n.level_label for n in tree.nodes}
    assert "LIBRO" in labels
    assert "Artículo" in labels


def test_assemble_codigo_legal_captures_reform_metadata():
    """Reform annotations get attached as metadata on the relevant node."""
    elements = [
        _t("LIBRO PRIMERO", 1),
        _t("CAPITULO I", 1),
        _t("Artículo 1o.- La administración", 1, ElementKind.NARRATIVE),
        _t("Artículo reformado DOF 13-06-2014", 1, ElementKind.NARRATIVE),
    ]
    tree = HierarchyAssembler(get_profile("codigo_legal")).assemble(elements, toc=None)
    art = next(n for n in tree.nodes if n.level_label == "Artículo")
    annotations = art.metadata.get("annotations") or []
    assert any(a.get("reforma_dof") == "13-06-2014" for a in annotations)
