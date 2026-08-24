import pytest

from qgen.rules.base import DocumentRules, RulesOverride, merge_rules
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
