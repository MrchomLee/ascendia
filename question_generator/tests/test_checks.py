"""Revisiones de cada pregunta de una ventana (spec §7)."""

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


def _item(pregunta="¿Cómo se conceptúa la guerra?", *, tipo="teoria",
          correcta="un conflicto entre sociedades",
          cita='la guerra se conceptúa como "un conflicto entre sociedades') -> dict:
    return {
        "tipo": tipo,
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


def test_parse_items_corta_en_30():
    preguntas, descartes = parse_items([_item(f"¿Pregunta {i}?") for i in range(31)])
    assert len(preguntas) == 30
    assert descartes == ["pregunta 31: pasa de las 30 preguntas por ventana"]


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
    assert verification_motivos(None, "A") == ["verificación fallida"]
    assert verification_motivos(_verif("A"), "A") == []
    assert verification_motivos(_verif("B"), "A") == ["la verificación eligió B; la clave es A"]
    assert verification_motivos(_verif("ninguna"), "A") == ["la verificación respondió «ninguna»"]
    assert verification_motivos(_verif("A", "mayor"), "A") == ["supera la dificultad del PDF"]


def test_verdict_with_motivos_recalcula_el_estado():
    assert Verdict.from_motivos([]).with_motivos(["x"]) == Verdict("needs_review", ("x",))


# ─── Duplicadas ────────────────────────────────────────────────────────────


def test_duplicadas_de_teoria_por_similitud_dentro_del_mismo_nodo():
    index = DuplicateIndex()
    index.add(1, "¿Cómo se conceptúa la guerra para México?", "teoria")
    assert index.is_duplicate(1, "¿Cómo se conceptúa la guerra, para México?", "teoria")
    assert not index.is_duplicate(2, "¿Cómo se conceptúa la guerra, para México?", "teoria")


def test_ejercicios_solo_se_descartan_si_son_identicos():
    index = DuplicateIndex()
    index.add(1, "Deriva f(x) = 3x^2.", "ejercicio_nuevo")
    assert not index.is_duplicate(1, "Deriva f(x) = 5x^2.", "ejercicio_nuevo")
    assert index.is_duplicate(1, "Deriva  f(x) = 3x^2.", "ejercicio_nuevo")
