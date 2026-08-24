from etl.models.schema import Chunk, Node

from qgen.prompts.render import build_variable_prompt
from qgen.prompts.system import build_system_instruction
from qgen.rules.defaults import get_default_rules


def _node():
    return Node(
        id=42, manual_id=1, parent_id=None,
        level=3, level_label="Artículo", ordinal="9o Bis",
        title="Habrá un Tribunal Militar",
        breadcrumb="LIBRO PRIMERO › TÍTULO PRIMERO › Capítulo II › Artículo 9o Bis",
        page_start=3, page_end=3, sort_key="01.01.02.03", is_anexo=False,
        metadata_json={},
    )


def _chunk(text: str, ordinal: int = 0):
    return Chunk(
        id=ordinal + 1, node_id=42, manual_id=1, ordinal=ordinal,
        text=text, char_count=len(text), page_start=3, page_end=3,
        has_table=False, has_image_ref=False, metadata_json={},
    )


def test_system_instruction_contains_rules():
    rules = get_default_rules("codigo_legal")
    instr = build_system_instruction(rules, target_question="dummy question")
    assert "codigo_legal" in instr
    assert "exactamente 4 opciones" in instr
    assert "tipos de delitos y faltas militares" in instr  # preferred_topics
    assert "años de condena" in instr  # forbidden_topics


def test_variable_prompt_includes_breadcrumb_and_body():
    node = _node()
    chunks = [_chunk("Texto del artículo 9o Bis sobre tribunales.")]
    prompt = build_variable_prompt(node, chunks)
    assert "Artículo" in prompt
    assert "9o Bis" in prompt
    assert "LIBRO PRIMERO › TÍTULO PRIMERO" in prompt
    assert "Texto del artículo 9o Bis sobre tribunales." in prompt


def test_variable_prompt_handles_empty_chunks():
    prompt = build_variable_prompt(_node(), [])
    assert "(bloque sin texto extra" in prompt


def test_variable_prompt_concatenates_multiple_chunks_in_order():
    chunks = [_chunk("Segundo párrafo.", ordinal=1), _chunk("Primer párrafo.", ordinal=0)]
    prompt = build_variable_prompt(_node(), chunks)
    # ordinals sorted: primero, segundo
    assert prompt.index("Primer párrafo.") < prompt.index("Segundo párrafo.")
