"""Render the per-node variable prompt that goes alongside the cached context."""

from __future__ import annotations

from etl.models.schema import Chunk, Node


def _node_text(node: Node, chunks: list[Chunk]) -> str:
    """Concatenate the node's chunks in order; empty string if none."""
    if not chunks:
        return ""
    ordered = sorted(chunks, key=lambda c: c.ordinal)
    return "\n\n".join(c.text for c in ordered if c.text and c.text.strip())


def build_variable_prompt(node: Node, chunks: list[Chunk]) -> str:
    """Build the user message for a single node.

    The cached context already gave Gemini the whole document plus the system
    instructions and rules. Here we only point to the specific block we want
    a question about, plus the literal text of that block (so the LLM knows
    the exact passage to use as the ground truth for the correct answer).
    """
    body = _node_text(node, chunks)
    page_range = (
        f"p. {node.page_start}"
        if node.page_end in (None, node.page_start)
        else f"pp. {node.page_start}-{node.page_end}"
    )

    return f"""\
Genera UNA pregunta de examen para el siguiente bloque del documento.

Bloque:
- Tipo: {node.level_label}
- Ordinal: {node.ordinal}
- Título: {node.title}
- Ubicación: {page_range}
- Ruta jerárquica: {node.breadcrumb}

Texto literal del bloque (usa esto como verdad para la respuesta correcta;
NO inventes datos fuera de este texto y del documento cacheado):

\"\"\"
{body or "(bloque sin texto extraíble; usa el contexto del documento cacheado)"}
\"\"\"

Genera el JSON con la pregunta, las 4 opciones (1 correct + 1 confusa + 2 distractor) y la justificación, siguiendo todas las reglas del system prompt."""
