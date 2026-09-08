"""Pruebas unitarias para los patrones y jerarquía de Álgebra de Baldor."""

from etl.hierarchy.patterns import (
    KIND_BALDOR_TEMA,
    KIND_CAPITULO,
    KIND_SECCION,
    KIND_SUBSECCION,
    match_baldor_capitulo,
    match_baldor_caso,
    match_baldor_subseccion_romana,
    match_baldor_tema_mayusculas,
    match_baldor_inciso,
)
from etl.hierarchy.profile import get_profile


def test_match_baldor_capitulo_romanos():
    """Verifica que los capítulos con numeración romana se reconocen con su ordinal y título."""
    casos = [
        ("I. Suma", "I", "Suma"),
        ("II. Resta", "II", "Resta"),
        ("III. Signos de agrupación", "III", "Signos de agrupación"),
        ("IV. Multiplicación", "IV", "Multiplicación"),
        ("V. División", "V", "División"),
        ("VI. Productos y cocientes notables", "VI", "Productos y cocientes notables"),
        ("VIII. Ecuaciones enteras de primer grado con una incógnita", "VIII", "Ecuaciones enteras de primer grado con una incógnita"),
        ("X. Descomposición factorial", "X", "Descomposición factorial"),
        ("XI. Máximo común divisor", "XI", "Máximo común divisor"),
        ("XII. Mínimo común múltiplo", "XII", "Mínimo común múltiplo"),
        ("XIII. Fracciones algebraicas. Reducción de fracciones", "XIII", "Fracciones algebraicas. Reducción de fracciones"),
        ("XVIII. Fórmulas", "XVIII", "Fórmulas"),
        ("XX. Funciones", "XX", "Funciones"),
        ("XXI. Representación gráfica de funciones y relaciones", "XXI", "Representación gráfica de funciones y relaciones"),
        ("XXIV. Ecuaciones simultáneas de primer grado con dos incógnitas", "XXIV", "Ecuaciones simultáneas de primer grado con dos incógnitas"),
        ("XXXII. Números complejos", "XXXII", "Números complejos"),
    ]
    for texto, ord_esperado, tit_esperado in casos:
        cand = match_baldor_capitulo(texto)
        assert cand is not None, f"Fallo al detectar capítulo: {texto}"
        assert cand.kind == KIND_CAPITULO
        assert cand.ordinal == ord_esperado
        assert cand.title_remainder == tit_esperado


def test_match_baldor_subseccion_romana():
    """Verifica las subsecciones con números romanos en mayúsculas."""
    casos = [
        ("I. SUMA DE MONOMIOS", "I", "SUMA DE MONOMIOS"),
        ("II. SUMA DE POLINOMIOS", "II", "SUMA DE POLINOMIOS"),
        ("I. RESTA DE MONOMIOS", "I", "RESTA DE MONOMIOS"),
        ("I. ELIMINACIÓN POR IGUALACIÓN", "I", "ELIMINACIÓN POR IGUALACIÓN"),
        ("II. ELIMINACIÓN POR SUSTITUCIÓN", "II", "ELIMINACIÓN POR SUSTITUCIÓN"),
        ("III. MÉTODO DE REDUCCIÓN", "III", "MÉTODO DE REDUCCIÓN"),
    ]
    for texto, ord_esperado, tit_esperado in casos:
        cand = match_baldor_subseccion_romana(texto)
        assert cand is not None, f"Fallo en subsección romana: {texto}"
        assert cand.kind == KIND_SECCION
        assert cand.ordinal == ord_esperado
        assert cand.title_remainder == tit_esperado


def test_match_baldor_casos():
    """Verifica el reconocimiento de los casos clásicos de factorización."""
    casos = [
        (
            "CASO I: CUANDO TODOS LOS TÉRMINOS DE UN POLINOMIO TIENEN UN FACTOR COMÚN",
            "I",
            "CUANDO TODOS LOS TÉRMINOS DE UN POLINOMIO TIENEN UN FACTOR COMÚN",
        ),
        ("CASO III: TRINOMIO CUADRADO PERFECTO", "III", "TRINOMIO CUADRADO PERFECTO"),
        ("CASO IV: DIFERENCIA DE CUADRADOS PERFECTOS", "IV", "DIFERENCIA DE CUADRADOS PERFECTOS"),
        (
            "CASO ESPECIAL: FACTORIZAR UNA SUMA DE DOS CUADRADOS",
            "ESPECIAL",
            "FACTORIZAR UNA SUMA DE DOS CUADRADOS",
        ),
    ]
    for texto, ord_esperado, tit_esperado in casos:
        cand = match_baldor_caso(texto)
        assert cand is not None, f"Fallo en caso: {texto}"
        assert cand.kind == KIND_SECCION
        assert cand.ordinal == ord_esperado
        assert cand.title_remainder == tit_esperado


def test_match_baldor_temas_mayusculas():
    """Verifica encabezados conceptuales y reglas generales en mayúsculas sostenidas."""
    temas = [
        "LA SUMA O ADICIÓN",
        "CARÁCTER GENERAL DE LA SUMA ALGEBRAICA",
        "REGLA GENERAL PARA SUMAR",
        "PRUEBA DE LA SUMA POR EL VALOR NUMÉRICO",
        "LA RESTA O SUSTRACCIÓN",
        "LEY DE LOS SIGNOS",
        "LEY DE LOS EXPONENTES",
        "LEY DE LOS COEFICIENTES",
        "PRODUCTO CONTINUADO",
        "CANTIDADES IMAGINARIAS",
        "CANTIDADES COMPLEJAS",
    ]
    for texto in temas:
        cand = match_baldor_tema_mayusculas(texto)
        assert cand is not None, f"Fallo en tema mayúsculas: {texto}"
        assert cand.kind == KIND_BALDOR_TEMA
        assert cand.title_remainder == texto


def test_match_baldor_incisos():
    """Verifica subcasos con letras tipo a) o b)."""
    cand_a = match_baldor_inciso("a) Factor común monomio.")
    assert cand_a is not None
    assert cand_a.kind == KIND_SUBSECCION
    assert cand_a.ordinal == "a"
    assert "Factor común monomio" in cand_a.title_remainder


def test_perfil_algebra_baldor_clasificacion():
    """Verifica que el perfil 'algebra_baldor' solo clasifica capítulos a nivel 0 y no subdivide en más nodos."""
    profile = get_profile("algebra_baldor")

    # Capítulo -> Nivel 0 (únicos nodos en el árbol)
    hm_cap = profile.classify("IV. Multiplicación")
    assert hm_cap is not None
    assert hm_cap.level == 0
    assert hm_cap.ordinal == "IV"
    assert hm_cap.title_remainder == "Multiplicación"

    hm_cap1 = profile.classify("I. Suma")
    assert hm_cap1 is not None
    assert hm_cap1.level == 0
    assert hm_cap1.ordinal == "I"

    # Subsecciones temáticas en mayúsculas no generan nodo (se conservan en el cuerpo)
    assert profile.classify("I. SUMA DE MONOMIOS") is None
    assert profile.classify("II. SUMA DE POLINOMIOS") is None

    # Casos, temas e incisos no generan nodos separados
    assert profile.classify("CASO III: TRINOMIO CUADRADO PERFECTO") is None
    assert profile.classify("LA SUMA O ADICIÓN") is None
    assert profile.classify("REGLA GENERAL PARA SUMAR") is None
    assert profile.classify("a) Factor común monomio.") is None

