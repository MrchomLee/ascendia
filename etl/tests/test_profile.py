from etl.extraction.types import ElementKind, RawElement
from etl.hierarchy.profile import (
    PROFILES,
    auto_detect_profile,
    get_profile,
)


def _el(text: str) -> RawElement:
    return RawElement(page_number=1, physical_page_index=0, kind=ElementKind.NARRATIVE, text=text)


def test_profile_registry_has_all_expected():
    assert "manual" in PROFILES
    assert "codigo_legal" in PROFILES
    assert "ley_organica" in PROFILES


def test_get_profile_unknown_raises():
    import pytest

    with pytest.raises(ValueError):
        get_profile("nonexistent_profile")


def test_manual_profile_classifies_parte_and_capitulo():
    p = get_profile("manual")
    assert p.classify("PRIMERA PARTE") is not None
    assert p.classify("Capítulo I") is not None
    assert p.classify("Tercera Sección") is not None
    assert p.classify("Subsección (A)") is not None


def test_manual_profile_does_not_classify_articulo():
    p = get_profile("manual")
    assert p.classify("Artículo 1o.- La administración") is None
    assert p.classify("LIBRO PRIMERO") is None


def test_codigo_legal_profile_classifies_legal_levels():
    p = get_profile("codigo_legal")

    libro = p.classify("LIBRO PRIMERO")
    assert libro is not None and libro.level == 0 and libro.level_label == "LIBRO"

    titulo = p.classify("TITULO PRIMERO")
    assert titulo is not None and titulo.level == 1 and titulo.level_label == "TÍTULO"

    capitulo = p.classify("CAPITULO I")
    assert capitulo is not None and capitulo.level == 2

    art = p.classify("Artículo 9o. Bis.- Habrá un Tribunal")
    assert art is not None and art.level == 3
    assert art.ordinal == "9o Bis"


def test_codigo_legal_profile_does_not_classify_parte():
    p = get_profile("codigo_legal")
    assert p.classify("PRIMERA PARTE") is None
    assert p.classify("Subsección (A)") is None


def test_codigo_legal_drop_filters():
    p = get_profile("codigo_legal")
    assert p.is_dropped_text("CÁMARA DE DIPUTADOS DEL H. CONGRESO DE LA UNIÓN")
    assert p.is_dropped_text("Secretaría de Servicios Parlamentarios")
    assert p.is_dropped_text("1 de 141")
    assert p.is_dropped_text("Última Reforma DOF 21-06-2018")
    assert not p.is_dropped_text("Artículo 1o.- La administración de la justicia militar")


def test_codigo_legal_metadata_extractor_captures_dof():
    p = get_profile("codigo_legal")
    captured = p.extract_metadata("Artículo reformado DOF 16-05-2016")
    assert captured.get("reforma_dof") == "16-05-2016"

    captured2 = p.extract_metadata("Fracción adicionada DOF 16-05-2016")
    assert captured2.get("reforma_dof") == "16-05-2016"


def test_codigo_legal_metadata_no_match_returns_empty():
    p = get_profile("codigo_legal")
    assert p.extract_metadata("La administración de la justicia militar") == {}


# ----- Auto-detection ------------------------------------------------------


def test_autodetect_codigo_legal():
    elements = [
        _el("CÓDIGO DE JUSTICIA MILITAR"),
        _el("LIBRO PRIMERO"),
        _el("De la organización y competencia"),
        _el("TITULO PRIMERO"),
        _el("CAPITULO I"),
        _el("Artículo 1o.- La administración de la justicia militar..."),
    ]
    assert auto_detect_profile(elements) == "codigo_legal"


def test_autodetect_manual():
    elements = [
        _el("MANUAL DE OPERACIONES MILITARES"),
        _el("PRIMERA PARTE"),
        _el("LA GUERRA"),
        _el("Capítulo I"),
        _el("Teoría de la Guerra"),
    ]
    assert auto_detect_profile(elements) == "manual"


def test_autodetect_falls_back_to_manual_for_empty():
    assert auto_detect_profile([]) == "manual"
