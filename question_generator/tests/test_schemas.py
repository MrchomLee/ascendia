import pytest
from pydantic import ValidationError

from qgen.prompts.schemas import GeneratedOption, GeneratedQuestion, OptionRole


def _make_options(role_counts=(1, 1, 2)):
    """Build a list of options matching the canonical 1+1+2 distribution."""
    out = []
    counter = 0
    role_buckets = [
        (OptionRole.CORRECT, role_counts[0]),
        (OptionRole.CONFUSA, role_counts[1]),
        (OptionRole.DISTRACTOR, role_counts[2]),
    ]
    for role, n in role_buckets:
        for _ in range(n):
            counter += 1
            out.append(GeneratedOption(role=role, text=f"option text {counter}"))
    return out


def test_valid_question_passes():
    q = GeneratedQuestion(
        question="¿Cuál es el principio fundamental?",
        options=_make_options(),
        justification="Porque sí.",
    )
    assert len(q.options) == 4
    assert sum(1 for o in q.options if o.role == OptionRole.CORRECT) == 1


def test_too_few_options_rejected():
    with pytest.raises(ValidationError):
        GeneratedQuestion(
            question="Q",
            options=_make_options()[:3],
            justification="J",
        )


def test_two_correct_options_rejected():
    opts = _make_options(role_counts=(2, 1, 1))  # still 4 total, but 2 correct
    with pytest.raises(ValidationError):
        GeneratedQuestion(question="Q", options=opts, justification="J")


def test_zero_distractor_rejected():
    opts = _make_options(role_counts=(1, 1, 0))
    with pytest.raises(ValidationError):
        GeneratedQuestion(question="Q", options=opts, justification="J")


def test_duplicate_option_text_rejected():
    opts = _make_options()
    opts[1] = GeneratedOption(role=OptionRole.CONFUSA, text=opts[0].text)
    with pytest.raises(ValidationError):
        GeneratedQuestion(question="Q", options=opts, justification="J")


def test_empty_question_rejected():
    with pytest.raises(ValidationError):
        GeneratedQuestion(question="", options=_make_options(), justification="J")
