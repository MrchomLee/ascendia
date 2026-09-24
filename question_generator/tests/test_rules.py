import pytest

from qgen.rules.base import DocumentRules, RulesOverride, merge_rules, rules_from_dict, rules_to_dict
from qgen.rules.defaults import PROFILE_RULES, get_default_rules


def test_profile_registry_has_keys():
    assert {"manual", "codigo_legal", "ley_organica"}.issubset(PROFILE_RULES)


def test_get_default_rules_known():
    r = get_default_rules("codigo_legal")
    assert r.name == "codigo_legal"
    assert "tipos de delitos y faltas militares" in r.preferred_topics


def test_get_default_rules_unknown_raises():
    with pytest.raises(ValueError):
        get_default_rules("not_a_profile")


def test_merge_with_none_override_returns_default():
    d = get_default_rules("manual")
    assert merge_rules(d, None) is d


def test_override_replaces_only_provided_fields():
    d = get_default_rules("manual")
    ov = RulesOverride(
        forbidden_topics=("custom forbidden",),
        extra_instructions="custom extra",
    )
    merged = merge_rules(d, ov)
    assert merged.forbidden_topics == ("custom forbidden",)
    assert merged.extra_instructions == "custom extra"
    # Untouched fields preserved
    assert merged.preferred_topics == d.preferred_topics
    assert merged.style_guide == d.style_guide


def test_rules_serialize_roundtrip():
    d = get_default_rules("codigo_legal")
    payload = d.to_dict()
    rebuilt = DocumentRules.from_dict(payload)
    assert rebuilt == d


def test_rules_override_from_empty_dict():
    ov = RulesOverride.from_dict({})
    d = get_default_rules("manual")
    assert merge_rules(d, ov) == d


def test_taller_lectura_redaccion_tiene_reglas_de_generacion():
    # Sin reglas, qgen-generate se cae con ValueError al primer uso del perfil.
    rules = get_default_rules("taller_lectura_redaccion")
    assert rules.name == "taller_lectura_redaccion"
    assert rules.preferred_topics


def test_historia_universal_tiene_reglas_de_generacion():
    rules = get_default_rules("historia_universal")
    assert rules.name == "historia_universal"
    assert rules.preferred_topics


def test_geografia_moderna_mexico_tiene_reglas_de_generacion():
    rules = get_default_rules("geografia_moderna_mexico")
    assert rules.name == "geografia_moderna_mexico"
    assert rules.preferred_topics


def test_calculo_una_variable_tiene_reglas_de_generacion():
    rules = get_default_rules("calculo_una_variable")
    assert rules.name == "calculo_una_variable"
    assert rules.preferred_topics


def test_algebra_trigonometria_geometria_analitica_tiene_reglas_de_generacion():
    rules = get_default_rules("algebra_trigonometria_geometria_analitica")
    assert rules.name == "algebra_trigonometria_geometria_analitica"
    assert rules.preferred_topics


@pytest.mark.parametrize("perfil, familia, tipos", [
    ("manual", "militar", ("teoria",)),
    ("codigo_legal", "militar", ("teoria",)),
    ("ley_organica", "militar", ("teoria",)),
    ("historia_universal", "civil", ("teoria",)),
    ("geografia_moderna_mexico", "civil", ("teoria",)),
    ("algebra_baldor", "civil", ("teoria", "ejercicio")),
    ("calculo_una_variable", "civil", ("teoria", "ejercicio")),
    ("algebra_trigonometria_geometria_analitica", "civil", ("teoria", "ejercicio")),
    ("taller_lectura_redaccion", "civil", ("teoria",)),
])
def test_cada_perfil_tiene_su_familia_y_sus_tipos(perfil, familia, tipos):
    rules = get_default_rules(perfil)
    assert (rules.familia, rules.tipos) == (familia, tipos)


def test_solo_los_libros_de_matematicas_tienen_ejercicios():
    con_ejercicios = {name for name, r in PROFILE_RULES.items() if "ejercicio" in r.tipos}
    matematicos = {name for name, r in PROFILE_RULES.items() if r.matematicas}
    assert con_ejercicios == matematicos == {
        "algebra_baldor", "calculo_una_variable", "algebra_trigonometria_geometria_analitica",
    }


def test_un_libro_que_no_es_de_matematicas_no_admite_ejercicios():
    with pytest.raises(ValueError, match="matemáticas"):
        DocumentRules(name="x", familia="civil", tipos=("teoria", "ejercicio"))
    DocumentRules(name="x", familia="civil", tipos=("teoria", "ejercicio"), matematicas=True)


def test_una_foto_antigua_con_ejercicios_se_lee_como_de_matematicas():
    rules = rules_from_dict({"name": "algebra_baldor", "familia": "civil", "tipos": ["teoria", "ejercicio"]})
    assert rules.matematicas


def test_familia_y_tipos_viajan_en_la_foto_de_la_corrida():
    rules = get_default_rules("calculo_una_variable")
    assert rules_from_dict(rules_to_dict(rules)) == rules


def test_una_foto_antigua_sin_familia_se_lee_como_militar_de_teoria():
    rules = rules_from_dict({"name": "manual"})
    assert (rules.familia, rules.tipos) == ("militar", ("teoria",))


def test_el_override_no_cambia_familia_ni_tipos():
    merged = merge_rules(get_default_rules("calculo_una_variable"), RulesOverride(style_guide="otro"))
    assert (merged.familia, merged.tipos, merged.matematicas) == ("civil", ("teoria", "ejercicio"), True)


def test_familia_o_tipo_desconocido_se_rechaza():
    with pytest.raises(ValueError):
        DocumentRules(name="x", familia="naval")
    with pytest.raises(ValueError):
        DocumentRules(name="x", tipos=("examen",))
    with pytest.raises(ValueError):
        DocumentRules(name="x", tipos=())
