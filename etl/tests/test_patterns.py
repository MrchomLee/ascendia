from etl.hierarchy.patterns import (
    KIND_ANEXO,
    KIND_ARTICULO,
    KIND_CAPITULO,
    KIND_LIBRO,
    KIND_PARTE,
    KIND_SECCION,
    KIND_SUBSECCION,
    KIND_TITULO,
    classify_heading,
    match_anexo,
    match_articulo,
    match_capitulo,
    match_libro,
    match_parte,
    match_seccion,
    match_subseccion,
    match_titulo,
)


# ----- Manual-style headings (default profile) -----------------------------


def test_parte():
    m = classify_heading("PRIMERA PARTE")
    assert m is not None
    assert m.level == 0
    assert m.level_label == "PARTE"
    assert m.ordinal == "PRIMERA"


def test_capitulo():
    m = classify_heading("Capítulo III")
    assert m is not None
    assert m.level == 1
    assert m.ordinal == "III"


def test_seccion():
    m = classify_heading("Tercera Sección")
    assert m is not None
    assert m.level == 2
    assert m.ordinal == "Tercera"


def test_seccion_unica():
    m = classify_heading("Sección Única")
    assert m is not None
    assert m.level == 2


def test_subseccion():
    m = classify_heading("- Subsección (B)")
    assert m is not None
    assert m.level == 3
    assert m.ordinal == "(B)"


def test_anexo():
    m = classify_heading('Anexo "A" Formato del Estudio Táctico del Terreno')
    assert m is not None
    assert m.is_anexo is True
    assert m.ordinal == "A"


def test_negative_body_text():
    assert classify_heading("Esta es una oración del cuerpo del manual.") is None
    assert classify_heading("") is None
    assert classify_heading("   ") is None


# ----- Profile-agnostic per-kind matchers ----------------------------------


def test_match_libro():
    cand = match_libro("LIBRO PRIMERO")
    assert cand is not None
    assert cand.kind == KIND_LIBRO
    assert cand.ordinal == "PRIMERO"


def test_match_libro_with_accents():
    assert match_libro("Libro Décimo") is not None
    assert match_libro("LIBRO DECIMO") is not None
    assert match_libro("LIBRO PRIMERO") is not None


def test_match_titulo():
    cand = match_titulo("TITULO PRIMERO")
    assert cand is not None
    assert cand.kind == KIND_TITULO
    assert cand.ordinal == "PRIMERO"
    assert match_titulo("Título Segundo") is not None


def test_match_articulo_basic():
    cand = match_articulo("Artículo 1o.- La administración de la justicia militar")
    assert cand is not None
    assert cand.kind == KIND_ARTICULO
    assert cand.ordinal == "1o"


def test_match_articulo_bis():
    cand = match_articulo("Artículo 9o. Bis.- Habrá un Tribunal")
    assert cand is not None
    assert cand.ordinal == "9o Bis"


def test_match_articulo_ter():
    cand = match_articulo("Artículo 9o. Ter.- Para ser Juez")
    assert cand is not None
    assert cand.ordinal == "9o Ter"


def test_match_articulo_no_suffix_marker():
    # Sin "o.-", solo "1.-" o "1.- "
    cand = match_articulo("Articulo 25.- El procedimiento")
    assert cand is not None
    assert cand.ordinal == "25o"


def test_match_articulo_ignores_non_article():
    assert match_articulo("La administración de la justicia militar") is None
    assert match_articulo("Capítulo I") is None


def test_match_capitulo_bis():
    cand = match_capitulo("CAPITULO II BIS")
    assert cand is not None
    assert cand.kind == KIND_CAPITULO
    assert "II" in cand.ordinal


# ----- New cases discovered while ingesting the CJM ------------------------


def test_libro_with_trailing_title():
    cand = match_libro("LIBRO PRIMERO De la organización y competencia")
    assert cand is not None
    assert cand.ordinal == "PRIMERO"
    assert "organización" in cand.title_remainder.lower()


def test_titulo_with_trailing_title():
    cand = match_titulo("TITULO CUARTO De la organización de la Defensoría")
    assert cand is not None
    assert cand.ordinal == "CUARTO"
    assert "Defensoría" in cand.title_remainder


def test_titulo_preliminar():
    cand = match_titulo("TITULO PRELIMINAR")
    assert cand is not None
    assert cand.ordinal == "PRELIMINAR"


def test_titulo_compound_decimoprimero():
    cand = match_titulo("TITULO DECIMOPRIMERO Delitos contra el deber")
    assert cand is not None
    assert "DECIMOPRIMERO" in cand.ordinal
    assert "deber" in cand.title_remainder.lower()


def test_titulo_compound_decimotercero():
    cand = match_titulo("TITULO DECIMOTERCERO Definiciones")
    assert cand is not None
    assert "DECIMOTERCERO" in cand.ordinal


def test_articulo_quater():
    cand = match_articulo("Artículo 9o. Quater.- Para ser Juez")
    assert cand is not None
    assert "Quater" in cand.ordinal or "Quáter" in cand.ordinal


def test_articulo_sexies():
    cand = match_articulo("Artículo 30o. Sexies.- Habrá un Juzgado")
    assert cand is not None
    assert "Sexies" in cand.ordinal


def test_articulo_septimus():
    cand = match_articulo("Artículo 30o. Septimus.- Para ser Juez")
    assert cand is not None
    assert "Septimus" in cand.ordinal


# ----- Sanity that the manual profile ignores legal-code headings ----------


def test_manual_profile_ignores_articulo():
    """Default classify_heading uses 'manual' profile — articles are not
    its concern (they belong to codigo_legal)."""
    assert classify_heading("Artículo 1o.- La administración") is None


def test_manual_profile_ignores_libro():
    assert classify_heading("LIBRO PRIMERO") is None
