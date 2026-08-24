"""Preguntas generadas — revisión visual, cobertura y corridas.

Es la vista de la fase 2: cada pregunta con su nodo de origen, sus 6 opciones
por rol y su justificación, más lo que falta por generar. Aquí se marca el
`validation_status`, que es lo que decide si la webapp se la sirve a un alumno.
"""

from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

from explorer.components import kpi_row
from explorer.data_access import get_manual, list_manuals
from explorer.navigation import PAGE_NODE, get_int, link_to, set_params
from explorer.questions_access import (
    ROLE_COLOR,
    ROLE_LABEL,
    STATUS_LABEL,
    STATUSES,
    QuestionView,
    get_question_kpis,
    list_questions,
    list_runs,
    nodes_missing_questions,
    questions_available,
    set_validation_status,
)

load_dotenv()
st.set_page_config(page_title="Preguntas", page_icon="❓", layout="wide")

manual_id = get_int("manual_id")
if manual_id is None:
    manuals = list_manuals()
    if not manuals:
        st.error("No hay manuales ingeridos. Vuelve al Home.")
        st.stop()
    selected = st.selectbox(
        "Selecciona un manual",
        options=[m.id for m in manuals],
        format_func=lambda i: next(f"{m.code} — {m.title}" for m in manuals if m.id == i),
    )
    if st.button("Abrir"):
        set_params(manual_id=selected)
        st.rerun()
    st.stop()

manual = get_manual(manual_id)
if manual is None:
    st.error(f"Manual {manual_id} no encontrado.")
    st.stop()

st.title(f"❓ Preguntas — {manual.code}")
st.caption(manual.title)

if not questions_available():
    st.info(
        "Esta base todavía no tiene tablas de preguntas: las crea la fase 2 la "
        "primera vez que corre.\n\n"
        "```powershell\npy -3.14 -m uv run qgen-generate "
        f"{manual.id} --dry-run   # estima el costo\n"
        f"py -3.14 -m uv run qgen-generate {manual.id} --limit 5\n```"
    )
    st.stop()

kpis = get_question_kpis(manual.id)
if kpis.total == 0:
    st.warning(
        f"El manual está ingerido pero no tiene ninguna pregunta. "
        f"Genera una muestra con `qgen-generate {manual.id} --limit 5`."
    )

kpi_row(
    [
        ("Preguntas", f"{kpis.total:,}", "Total generadas para este manual"),
        (
            "Se sirven",
            f"{kpis.served:,}",
            "Solo las que están en `pending` o `valid` llegan a un examen",
        ),
        (
            "Cobertura",
            f"{kpis.coverage_pct:.0f}%",
            f"{kpis.nodes_with_question} de {kpis.nodes_with_text} nodos con texto tienen pregunta",
        ),
        ("Costo", f"${kpis.cost_total_usd:.4f}", "Suma de las corridas del manual"),
    ]
)

if kpis.by_status:
    kpi_row(
        [
            (STATUS_LABEL.get(status, status), kpis.by_status.get(status, 0), None)
            for status in STATUSES
        ]
    )

st.divider()

tab_preguntas, tab_faltantes, tab_corridas = st.tabs(
    ["Preguntas", f"Sin pregunta ({len(nodes_missing_questions(manual.id))})", "Corridas"]
)


def _render_question(question: QuestionView) -> None:
    with st.container(border=True):
        head_left, head_right = st.columns([0.72, 0.28])
        with head_left:
            st.markdown(
                f"[{question.node_label}]({link_to(PAGE_NODE, node_id=question.node_id)}) "
                f"— {question.node_title}  ·  p.{question.node_page_start}"
            )
            st.caption(question.node_breadcrumb)
        with head_right:
            st.markdown(
                f"<div style='text-align:right'>{STATUS_LABEL.get(question.validation_status, question.validation_status)}"
                f"<br><span style='opacity:.6;font-size:.85em'>#{question.id} · corrida {question.run_id}</span></div>",
                unsafe_allow_html=True,
            )

        st.markdown(f"**{question.question_text}**")

        for option in question.options:
            color = ROLE_COLOR.get(option.role, "gray")
            marca = "✔ " if option.is_correct else "&nbsp;&nbsp;&nbsp;"
            st.markdown(
                f"{marca}:{color}[**{ROLE_LABEL.get(option.role, option.role)}**] — {option.text}",
                unsafe_allow_html=True,
            )

        st.caption(f"💡 {question.justification}")

        # Lo único que este explorador escribe. Marcar no borra: una pregunta
        # rechazada sigue ahí y viaja en el bundle, solo que sin llegar a un examen.
        elegido = st.segmented_control(
            "Revisión",
            options=list(STATUSES),
            format_func=lambda s: STATUS_LABEL.get(s, s),
            default=question.validation_status,
            key=f"status_{question.id}",
            label_visibility="collapsed",
        )
        if elegido is not None and elegido != question.validation_status:
            set_validation_status(question.id, elegido)
            st.rerun()


with tab_preguntas:
    runs = list_runs(manual.id)
    filtros = st.columns([0.3, 0.25, 0.45])
    with filtros[0]:
        estados = st.multiselect(
            "Estado",
            options=list(STATUSES),
            default=[],
            format_func=lambda s: STATUS_LABEL.get(s, s),
            placeholder="Todos",
        )
    with filtros[1]:
        run_ids = [r.id for r in runs]
        run_elegida = st.selectbox(
            "Corrida",
            options=[None, *run_ids],
            format_func=lambda i: "Todas" if i is None else f"#{i}",
        )
    with filtros[2]:
        busqueda = st.text_input("Buscar en el enunciado o la justificación", "")

    preguntas = list_questions(
        manual.id,
        statuses=tuple(estados) or None,
        run_id=run_elegida,
        query=busqueda or None,
    )
    st.caption(
        f"{len(preguntas)} pregunta(s)."
        + (" Se muestran como mucho 500." if len(preguntas) >= 500 else "")
    )
    for pregunta in preguntas:
        _render_question(pregunta)

with tab_faltantes:
    faltantes = nodes_missing_questions(manual.id)
    if not faltantes:
        st.success("Todos los nodos con texto tienen al menos una pregunta.")
    else:
        st.caption(
            f"{len(faltantes)} nodo(s) con texto y sin pregunta. Volver a correr "
            "`qgen-generate` sin `--regenerate` genera solo estos."
        )
        st.dataframe(
            [
                {
                    "node_id": n.id,
                    "nivel": f"{n.level_label} {n.ordinal}".strip(),
                    "título": n.title,
                    "página": n.page_start,
                    "chunks": n.chunk_count,
                    "breadcrumb": n.breadcrumb,
                }
                for n in faltantes
            ],
            width="stretch",
            hide_index=True,
        )

with tab_corridas:
    if not runs:
        st.info("Este manual no tiene ninguna corrida de generación.")
    else:
        st.dataframe(
            [
                {
                    "run_id": r.id,
                    "modelo": r.model,
                    "modo": r.mode,
                    "estado": r.status,
                    "perfil": r.profile_used,
                    "preguntas": r.question_count,
                    "nodos ok/total": f"{r.nodes_completed}/{r.nodes_total}",
                    "fallidos": r.nodes_failed,
                    "costo USD": f"{r.cost_estimate_usd:.4f}",
                    "inicio": r.started_at.strftime("%Y-%m-%d %H:%M"),
                }
                for r in runs
            ],
            width="stretch",
            hide_index=True,
        )
        st.caption(
            "Cada invocación de `qgen-generate` abre su propia corrida. Un manual "
            "puede acumular varias: las preguntas que faltaban se llenan en las "
            "siguientes."
        )
