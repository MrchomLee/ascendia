"""Revisiones de cada pregunta de una ventana (spec §7)."""

from qgen.prompts.schemas import MAX_PREGUNTAS_POR_VENTANA
from qgen.prompts.schemas import LETRAS, GeneratedQuestion, OptionRole, VerificationResult, WindowQuestion
from qgen.validation.checks import (
    DuplicateIndex,
    Verdict,
    norm_math,
    norm_text,
    parse_items,
    review,
    tipo_permitido,
    to_generated,
    verification_motivos,
    verification_options,
)

VENTANA = (
    "Para México, la guerra se conceptúa como “un conflicto entre sociedades o grupos "
    "de seres humanos”.\n\nEJEMPLO 1 Derivar f(x) = 𝑥² − 4.\nSolución: f′(x) = 2𝑥."
)


def _item(pregunta="¿Cómo se conceptúa la guerra?", *, tipo="teoria", nivel="conocimiento",
          correcta="un conflicto entre sociedades",
          cita='la guerra se conceptúa como "un conflicto entre sociedades') -> dict:
    return {
        "tipo": tipo,
        "nivel": nivel,
        "pregunta": pregunta,
        "opciones": [
            {"rol": "correct", "texto": correcta},
            {"rol": "confusa", "texto": "confusa"},
            {"rol": "distractor", "texto": "distractor uno"},
            {"rol": "distractor", "texto": "distractor dos"},
        ],
        "cita": cita,
        "justificacion": "…",
    }


def _q(*args, **kwargs) -> WindowQuestion:
    return WindowQuestion.model_validate(_item(*args, **kwargs))


# ─── Normalización ─────────────────────────────────────────────────────────


def test_norm_text_ignora_espacios_mayusculas_y_comillas():
    assert norm_text("  “Hola”   Mundo – x ") == '"hola" mundo - x'


def test_norm_math_iguala_la_notacion_de_los_pdf_de_word():
    assert norm_math("x^2 − 4") == norm_math("x2 - 4") == norm_math("𝑥² − 4")
    assert norm_math("f′(x) = 2𝑥") == norm_math("f'(x)=2x")


# ─── Revisión por tipo ─────────────────────────────────────────────────────


def test_teoria_literal_pasa():
    assert review(_q(), VENTANA) == Verdict("pending", ())


def test_teoria_parafraseada_va_a_revision():
    assert review(_q(correcta="una lucha violenta entre pueblos"), VENTANA).motivos == ("respuesta parafraseada",)


def test_teoria_con_cita_inventada_va_a_revision():
    verdict = review(_q(cita="la guerra es la continuación de la política"), VENTANA)
    assert verdict == Verdict("needs_review", ("cita no encontrada",))


def test_ejercicio_del_libro_con_su_resultado_pasa():
    q = _q("Deriva f(x) = x^2 − 4.", tipo="ejercicio_libro", correcta="f'(x) = 2x",
           cita="Derivar f(x) = 𝑥² − 4.\nSolución: f′(x) = 2𝑥.")
    assert review(q, VENTANA).status == "pending"


def test_ejercicio_del_libro_sin_su_resultado_va_a_revision():
    q = _q("Deriva f(x) = x^2 − 4.", tipo="ejercicio_libro", correcta="f'(x) = x",
           cita="Derivar f(x) = 𝑥² − 4.\nSolución: f′(x) = 2𝑥.")
    assert review(q, VENTANA).motivos == ("el resultado no aparece en el ejemplo citado",)


def test_ejercicio_nuevo_sin_ejemplo_de_referencia_va_a_revision():
    q = _q("Deriva g(x) = x^3.", tipo="ejercicio_nuevo", correcta="3x^2", cita="Derivar g(x) = x³")
    assert review(q, VENTANA).motivos == ("sin ejemplo de referencia",)


def test_ejercicio_nuevo_con_su_ejemplo_pasa_la_revision_de_texto():
    q = _q("Deriva g(x) = x^3.", tipo="ejercicio_nuevo", correcta="3x^2",
           cita="Derivar f(x) = 𝑥² − 4.\nSolución: f′(x) = 2𝑥.")
    assert review(q, VENTANA).status == "pending"


# ─── Estructura ────────────────────────────────────────────────────────────


def test_parse_items_descarta_solo_lo_malo():
    preguntas, descartes = parse_items([_item(), {"tipo": "teoria"}])
    assert len(preguntas) == 1
    assert len(descartes) == 1 and descartes[0].startswith("pregunta 2: estructura inválida")


def test_parse_items_corta_en_el_tope_por_ventana():
    tope = MAX_PREGUNTAS_POR_VENTANA
    preguntas, descartes = parse_items([_item(f"¿Pregunta {i}?") for i in range(tope + 1)])
    assert len(preguntas) == tope
    assert descartes == [f"pregunta {tope + 1}: pasa de las {tope} preguntas por ventana"]


def test_tipo_permitido():
    teoria, ejercicio = _q(), _q("Deriva.", tipo="ejercicio_libro")
    assert tipo_permitido(teoria, ("teoria",))
    assert not tipo_permitido(ejercicio, ("teoria",))
    assert tipo_permitido(ejercicio, ("teoria", "ejercicio"))


# ─── Opciones barajadas ────────────────────────────────────────────────────


def test_to_generated_baraja_de_forma_reproducible():
    g = to_generated(_q())
    assert isinstance(g, GeneratedQuestion)
    assert [o.text for o in g.options] == [o.text for o in to_generated(_q()).options]
    assert sorted(o.role.value for o in g.options) == ["confusa", "correct", "distractor", "distractor"]


def test_la_correcta_no_queda_siempre_primera():
    posiciones = [
        next(i for i, o in enumerate(to_generated(_q(f"¿Pregunta {n}?")).options) if o.role == OptionRole.CORRECT)
        for n in range(8)
    ]
    assert any(p != 0 for p in posiciones)


def test_verification_options_devuelve_la_letra_de_la_clave():
    textos, letra = verification_options(_q())
    assert textos[LETRAS.index(letra)] == "un conflicto entre sociedades"
    assert sorted(textos) == sorted(["un conflicto entre sociedades", "confusa", "distractor uno", "distractor dos"])


# ─── Verificación ──────────────────────────────────────────────────────────


def _verif(opcion: str, dificultad: str = "igual") -> VerificationResult:
    return VerificationResult(razonamiento="…", opcion=opcion, dificultad=dificultad)


def test_verification_motivos():
    # Las letras de la verificación no son las del explorador: el motivo nombra las opciones.
    textos = ["3x^2", "x^2", "3x", "x^3/3"]
    assert verification_motivos(None, "A", textos) == ["verificación fallida"]
    assert verification_motivos(_verif("A"), "A", textos) == []
    assert verification_motivos(_verif("B"), "A", textos) == ["la verificación eligió «x^2»; la clave es «3x^2»"]
    assert verification_motivos(_verif("ninguna"), "A", textos) == ["la verificación respondió «ninguna»"]
    assert verification_motivos(_verif("A", "mayor"), "A", textos) == ["supera la dificultad del PDF"]


def test_verdict_with_motivos_recalcula_el_estado():
    assert Verdict.from_motivos([]).with_motivos(["x"]) == Verdict("needs_review", ("x",))


# ─── Duplicadas ────────────────────────────────────────────────────────────


def test_duplicadas_de_teoria_por_similitud_dentro_del_mismo_nodo():
    index = DuplicateIndex()
    index.add(1, "¿Cómo se conceptúa la guerra para México?", "teoria", "un conflicto entre sociedades")
    assert index.is_duplicate(1, "¿Cómo se conceptúa la guerra, para México?", "teoria", "Un conflicto entre sociedades")
    assert not index.is_duplicate(2, "¿Cómo se conceptúa la guerra, para México?", "teoria", "un conflicto entre sociedades")


def test_ejercicios_solo_se_descartan_si_son_identicos():
    index = DuplicateIndex()
    index.add(1, "Deriva f(x) = 3x^2.", "ejercicio_nuevo", "6x")
    assert not index.is_duplicate(1, "Deriva f(x) = 5x^2.", "ejercicio_nuevo", "10x")
    assert index.is_duplicate(1, "Deriva  f(x) = 3x^2.", "ejercicio_nuevo", "6x")


# ─── Arreglos de la revisión final ─────────────────────────────────────────

PREFIJO = (
    "Conforme al Manual de Logística Militar, PARTE I — Generalidades › Capítulo II — "
    "Organización › Sección Primera — Conceptos, "
)


def test_preguntas_militares_distintas_con_el_mismo_prefijo_no_son_duplicadas():
    index = DuplicateIndex()
    index.add(1, PREFIJO + "¿qué es la logística?", "teoria", "el conjunto de actividades de apoyo")
    assert not index.is_duplicate(1, PREFIJO + "¿qué es la táctica?", "teoria", "el empleo de las unidades en combate")


def test_preguntas_parecidas_con_distinta_respuesta_no_son_duplicadas():
    index = DuplicateIndex()
    index.add(1, "¿En qué año se fundó la ONU?", "teoria", "1945")
    assert not index.is_duplicate(1, "¿En qué año se fundó la OEA?", "teoria", "1948")


def test_la_similitud_no_depende_del_orden():
    a, b = "¿Cuál es la capital de Sonora?", "¿Cuál es la capital de Sinaloa?"
    uno, otro = DuplicateIndex(), DuplicateIndex()
    uno.add(1, a, "teoria", "Hermosillo")
    otro.add(1, b, "teoria", "Hermosillo")
    assert uno.is_duplicate(1, b, "teoria", "Hermosillo") == otro.is_duplicate(1, a, "teoria", "Hermosillo")


def test_teoria_de_matematicas_no_va_a_revision_por_la_notacion():
    ventana = "La derivada de 𝑥2 es 2𝑥, y la de x2 − 4 también."
    q = _q("¿Cuál es la derivada de x²?", correcta="2x", cita="La derivada de x² es 2x")
    assert review(q, ventana).status == "pending"


def test_norm_math_ignora_el_signo_por():
    assert norm_math("2 × 3 = 6") == norm_math("2*3=6")


COSTA = (
    "La costa avanza hacia el norte por efecto de depósitos aluviales formados por "
    "los ríos Grijalva y Usumacinta, unidos."
)


def _nivel(nivel, pregunta="¿Cómo avanza la costa?", correcta="por la acumulación de sedimentos de dos ríos",
           cita=COSTA):
    return _q(pregunta, nivel=nivel, correcta=correcta, cita=cita)


def test_en_conocimiento_la_clave_debe_ser_literal():
    assert review(_nivel("conocimiento", correcta="hacia el norte"), COSTA).motivos == ()
    assert review(_nivel("conocimiento"), COSTA).motivos == ("respuesta parafraseada",)


def test_en_comprension_una_clave_literal_larga_delata_conocimiento():
    literal = "por efecto de depósitos aluviales formados por los ríos Grijalva y Usumacinta"
    assert review(_nivel("comprension", correcta=literal), COSTA).motivos == (
        "la clave es literal: por su forma es conocimiento",
    )
    assert review(_nivel("comprension"), COSTA).motivos == ()  # paráfrasis


def test_una_clave_literal_corta_no_delata_nada():
    assert review(_nivel("analisis", correcta="hacia el norte"), COSTA).motivos == ()


def test_en_aplicacion_el_caso_debe_ser_inventado():
    copiado = "La costa avanza hacia el norte por efecto de depósitos aluviales. ¿Qué ocurre?"
    inventado = "Un equipo de geógrafos mide la línea costera de Tabasco durante diez años. ¿Qué cambio registrará?"
    assert review(_nivel("aplicacion", pregunta=copiado), COSTA).motivos == ("el caso no es inventado",)
    assert review(_nivel("aplicacion", pregunta=inventado), COSTA).motivos == ()


def test_la_cita_debe_ser_literal_en_todos_los_niveles():
    for nivel in ("conocimiento", "comprension", "analisis", "aplicacion"):
        motivos = review(_nivel(nivel, correcta="hacia el norte", cita="una cita inventada"), COSTA).motivos
        assert "cita no encontrada" in motivos
