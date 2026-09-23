"""Ventanas de texto (spec §4): grupos de chunks consecutivos de un nodo."""

from dataclasses import dataclass

from qgen.windows import MAXIMO, Window, build_windows, strip_overlap


@dataclass
class C:
    ordinal: int
    text: str
    page_start: int = 1
    page_end: int = 1


def _keys(windows: list[Window]) -> list[str]:
    return [w.key for w in windows]


def test_un_nodo_pequeno_es_una_sola_ventana():
    windows = build_windows(7, [C(0, "Primero.", 3, 3), C(1, "Segundo.", 4, 5)])

    assert _keys(windows) == ["7:0-1"]
    assert windows[0].text == "Primero.\n\nSegundo."
    assert (windows[0].page_start, windows[0].page_end) == (3, 5)


def test_la_ventana_se_cierra_al_llegar_al_objetivo():
    # Contenido distinto por chunk: textos idénticos parecerían solapamiento.
    chunks = [C(i, str(i) * 1500) for i in range(6)]

    assert _keys(build_windows(1, chunks)) == ["1:0-2", "1:3-5"]


def test_nunca_pasa_del_maximo():
    windows = build_windows(1, [C(0, "a" * 3900), C(1, "b" * 2500)])

    assert _keys(windows) == ["1:0-0", "1:1-1"]
    assert all(len(w.text) <= MAXIMO for w in windows)


def test_corta_antes_de_un_ejemplo_pasados_3000_caracteres():
    chunks = [
        C(0, "a" * 1600),
        C(1, "b" * 1600),
        C(2, "EJEMPLO 3 Graficación de puntos\nSolución …"),
        C(3, "c" * 100),
    ]

    assert _keys(build_windows(1, chunks)) == ["1:0-1", "1:2-3"]


def test_no_corta_antes_de_un_ejemplo_si_la_ventana_es_corta():
    chunks = [C(0, "a" * 1000), C(1, "EJEMPLO 1 Distancia entre dos puntos\n…")]

    assert _keys(build_windows(1, chunks)) == ["1:0-1"]


def test_corta_antes_de_una_seccion_numerada():
    chunks = [C(0, "a" * 3100), C(1, "4.3 Ecuaciones de rectas\nUna recta …")]

    assert _keys(build_windows(1, chunks)) == ["1:0-0", "1:1-1"]


def test_un_chunk_mas_grande_que_el_maximo_forma_su_propia_ventana():
    chunks = [C(0, "a" * 500), C(1, "b" * 7000), C(2, "c" * 500)]

    assert _keys(build_windows(1, chunks)) == ["1:0-0", "1:1-1", "1:2-2"]


def test_se_quita_el_solapamiento_que_repite_el_chunker():
    primero = "Párrafo uno, bastante largo. " * 10
    segundo = primero[-120:] + "\n\nPárrafo dos."

    [window] = build_windows(1, [C(0, primero), C(1, segundo)])

    assert window.text == primero.strip() + "\n\nPárrafo dos."


def test_el_encabezado_se_busca_despues_del_solapamiento():
    primero = "a" * 3100
    segundo = primero[-120:] + "\n\nEJEMPLO 2 Tres puntos forman un triángulo"

    assert _keys(build_windows(1, [C(0, primero), C(1, segundo)])) == ["1:0-0", "1:1-1"]


def test_strip_overlap_no_toca_textos_sin_solapamiento():
    assert strip_overlap("fin del anterior.", "Otro texto.") == "Otro texto."
    # Coincidencias cortas (un punto, una palabra) no son solapamiento.
    assert strip_overlap("termina en punto.", ".empieza en punto") == ".empieza en punto"


def test_el_orden_es_por_ordinal_y_siempre_igual():
    chunks = [C(2, "tres"), C(0, "uno"), C(1, "dos")]

    assert build_windows(1, chunks) == build_windows(1, sorted(chunks, key=lambda c: c.ordinal))
    assert build_windows(1, chunks)[0].text == "uno\n\ndos\n\ntres"


def test_chunks_vacios_no_generan_ventanas():
    assert build_windows(1, [C(0, "   "), C(1, "")]) == []
    assert _keys(build_windows(1, [C(0, "  "), C(1, "Texto")])) == ["1:1-1"]
