"""Niveles cognitivos: valores, proporción y definiciones compartidas."""

from qgen.prompts.niveles import DEFINICIONES, NIVEL_LABEL, ORDEN, PROPORCION, Nivel, falta_algun_nivel


def test_cuatro_niveles_en_el_orden_del_usuario():
    assert [n.value for n in ORDEN] == ["conocimiento", "comprension", "aplicacion", "analisis"]
    assert NIVEL_LABEL["comprension"] == "Comprensión" and NIVEL_LABEL["analisis"] == "Análisis"


def test_la_proporcion_es_55_15_15_15():
    assert PROPORCION == {Nivel.CONOCIMIENTO: 55, Nivel.COMPRENSION: 15, Nivel.ANALISIS: 15, Nivel.APLICACION: 15}


def test_una_ventana_con_3_de_conocimiento_debe_traer_los_otros_niveles():
    completo = {"conocimiento": 3, "comprension": 1, "analisis": 1, "aplicacion": 1}
    assert not falta_algun_nivel(completo)
    assert falta_algun_nivel({**completo, "analisis": 0})
    assert falta_algun_nivel({"conocimiento": 5})
    assert not falta_algun_nivel({"conocimiento": 2})  # con menos de 3 son opcionales


def test_las_definiciones_traen_clave_confusa_y_filtro_de_cada_nivel():
    for marca in ("copia LITERAL", "PARÁFRASIS", "CASO INVENTADO", "CONCLUSIÓN INFERIDA", "Filtro anti-falsos positivos"):
        assert marca in DEFINICIONES
    assert "¿Cómo se describe el proceso de" in DEFINICIONES
    assert "¿Cómo describe el texto" not in DEFINICIONES
