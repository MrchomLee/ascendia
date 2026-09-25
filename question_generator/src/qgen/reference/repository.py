"""Repositorio para consultar preguntas de referencia (exemplars).

Recupera preguntas oro de la base de datos por perfil o código de manual
para ser inyectadas en los prompts durante la generación.
"""

from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session, joinedload
from qgen.models.reference_schema import ReferenceQuestion
from qgen.prompts.niveles import ORDEN


def get_reference_exemplars(
    session: Session,
    profile: str = "global",
    manual_code: str | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Consulta y retorna preguntas de referencia formateadas como diccionarios.

    Prioriza preguntas específicas del manual_code si coinciden; de lo contrario
    recupera preguntas del perfil o globales.

    Args:
        session: Sesión activa de SQLAlchemy.
        profile: Perfil del documento (ej. algebra_baldor, ley_organica).
        manual_code: Código del manual específico (ej. BALDOR-01).
        limit: Número máximo de ejemplos a retornar.

    Returns:
        Lista de diccionarios estructurados con las preguntas y sus opciones.
    """
    query = session.query(ReferenceQuestion).options(joinedload(ReferenceQuestion.options))

    # 1. Intentar buscar por manual_code si se proporciona
    exemplars = []
    if manual_code:
        exemplars = (
            query.filter(ReferenceQuestion.manual_code == manual_code)
            .limit(limit)
            .all()
        )

    # 2. Si no hay suficientes, buscar por perfil
    if len(exemplars) < limit:
        needed = limit - len(exemplars)
        existing_ids = {q.id for q in exemplars}
        profile_exemplars = (
            query.filter(
                ReferenceQuestion.profile == profile,
                ReferenceQuestion.id.notin_(existing_ids) if existing_ids else True,
            )
            .limit(needed)
            .all()
        )
        exemplars.extend(profile_exemplars)

    # 3. Si aún faltan, buscar por global
    if len(exemplars) < limit:
        needed = limit - len(exemplars)
        existing_ids = {q.id for q in exemplars}
        global_exemplars = (
            query.filter(
                ReferenceQuestion.profile == "global",
                ReferenceQuestion.id.notin_(existing_ids) if existing_ids else True,
            )
            .limit(needed)
            .all()
        )
        exemplars.extend(global_exemplars)

    return [_as_dict(q) for q in exemplars]


def _as_dict(q: ReferenceQuestion) -> dict[str, Any]:
    return {
        "id": q.id,
        "question_text": q.question_text,
        "profile": q.profile,
        "manual_code": q.manual_code,
        "justification": q.justification,
        "nivel": q.cognitive_level,
        "options": [{"role": o.role, "text": o.text, "is_correct": o.is_correct} for o in q.options],
    }


def get_level_exemplars(session: Session, *, profile: str, manual_code: str | None) -> list[dict[str, Any]]:
    """Un ejemplo por nivel, en el orden de los niveles: del manual; si no hay, del
    perfil; si no, global. El de menor id, para que el prompt sea determinista."""
    filtros = [ReferenceQuestion.profile == profile, ReferenceQuestion.profile == "global"]
    if manual_code:
        filtros.insert(0, ReferenceQuestion.manual_code == manual_code)
    ejemplos: list[dict[str, Any]] = []
    for nivel in ORDEN:
        for filtro in filtros:
            q = (
                session.query(ReferenceQuestion)
                .options(joinedload(ReferenceQuestion.options))
                .filter(ReferenceQuestion.cognitive_level == nivel.value, filtro)
                .order_by(ReferenceQuestion.id)
                .first()
            )
            if q is not None:
                ejemplos.append(_as_dict(q))
                break
    return ejemplos
