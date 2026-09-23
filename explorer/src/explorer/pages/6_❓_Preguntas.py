"""Preguntas generadas — revisión visual, cobertura y corridas.

Es la vista de la fase 2: cada pregunta con su nodo de origen, sus 6 opciones
por rol y su justificación, más lo que falta por generar. Aquí se marca el
`validation_status`, que es lo que decide si la webapp se la sirve a un alumno.
"""

from __future__ import annotations

from datetime import datetime, timezone
import streamlit as st
from dotenv import load_dotenv

from etl.db.session import session_scope
from explorer.components import kpi_row
from explorer.data_access import get_manual, list_manuals
from explorer.navigation import PAGE_NODE, get_int, link_to, set_params
from explorer.questions_access import (
    ROLE_COLOR,
    ROLE_LABEL,
    STATUS_LABEL,
    STATUSES,
    TYPE_LABEL,
    QuestionView,
    get_question_kpis,
    list_questions,
    list_runs,
    nodes_missing_questions,
    questions_available,
    set_validation_status,
)
from qgen.bundle.build import build_bundle, source_digest
from qgen.bundle.spec import bundle_filename, dumps, validate

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

# Barra visual de progreso y auditoría de cobertura
cobertura_val = min(max(kpis.coverage_pct / 100.0, 0.0), 1.0)
st.progress(
    cobertura_val,
    text=f"Cobertura global: {kpis.coverage_pct:.1f}% ({kpis.nodes_with_question} de {kpis.nodes_with_text} nodos con texto cubiertos)",
)

runs = list_runs(manual.id)
tab_preguntas, tab_faltantes, tab_corridas, tab_exportar = st.tabs(
    [
        "Preguntas",
        f"Sin pregunta ({len(nodes_missing_questions(manual.id))})",
        "Corridas",
        "📦 Exportar Bundle",
    ]
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
        st.caption(TYPE_LABEL.get(question.question_type, question.question_type))
        if question.motivos:
            st.warning("A revisar: " + "; ".join(question.motivos))

        for option in question.options:
            color = ROLE_COLOR.get(option.role, "gray")
            marca = "✔ " if option.is_correct else "&nbsp;&nbsp;&nbsp;"
            st.markdown(
                f"{marca}:{color}[**{ROLE_LABEL.get(option.role, option.role)}**] — {option.text}",
                unsafe_allow_html=True,
            )

        st.caption(f"💡 {question.justification}")
        if question.source_quote:
            with st.expander("Cita del texto"):
                # Texto plano: en markdown, `*`, `_` o `$` de una fórmula se interpretarían.
                st.text(question.source_quote)

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

with tab_exportar:
    st.subheader("📦 Exportación del Bundle de Contenido (v1)")
    st.caption(
        "Genera el paquete canónico JSON listo para entregar o importar en la webapp de exámenes, "
        "conforme a la especificación oficial de `CONTRATO-BUNDLE.md`."
    )

    col_cfg, col_preview = st.columns([0.48, 0.52])
    with col_cfg:
        st.markdown("#### Configuración de entrega")
        filtro_corrida = st.selectbox(
            "Corridas a incluir",
            options=[None] + [r.id for r in runs],
            format_func=lambda r: "Todas las corridas"
            if r is None
            else f"Corrida #{r} ({next(x.status for x in runs if x.id == r)})",
            help="Permite empaquetar una corrida específica o todas las preguntas acumuladas.",
        )

        include_raw = st.checkbox(
            "Incluir respuesta cruda del LLM (raw_response_json)",
            value=False,
            help="Incluye los metadatos completos y tokens crudos devueltos por Gemini (aumenta el tamaño del archivo).",
        )

        version_entrega = st.number_input(
            "Número de versión de entrega",
            min_value=1,
            value=1,
            step=1,
            help="Sufijo de versión para el nombre del archivo (ej. v1, v2).",
        )

        # Construir y validar bundle en memoria
        try:
            with session_scope() as session:
                bundle_data = build_bundle(
                    session,
                    manual_id=manual.id,
                    run_ids=[filtro_corrida] if filtro_corrida else None,
                    include_raw=include_raw,
                )
                source_path = bundle_data["manual"]["source_path"]
                bundle_data["manual"]["source_sha256"] = source_digest(source_path)
                reporte_val = validate(bundle_data)
                json_str = dumps(bundle_data)

            filename = bundle_filename(
                manual.code, datetime.now(timezone.utc).date(), int(version_entrega)
            )
            file_bytes = json_str.encode("utf-8")

            if reporte_val.ok:
                st.success("✅ Bundle validado con éxito contra el contrato v1.")
                st.download_button(
                    label=f"📥 Descargar {filename} ({len(file_bytes) / 1024:.1f} KB)",
                    data=file_bytes,
                    file_name=filename,
                    mime="application/json",
                    use_container_width=True,
                )
            else:
                # Igual que `qgen-export`: los errores bloquean la entrega; el
                # importador de la webapp rechazaría el fichero.
                st.error(
                    f"El bundle no cumple el contrato ({len(reporte_val.errors)} error(es)); "
                    "no se puede entregar:"
                )
                for err in reporte_val.errors:
                    st.error(err)
        except Exception as exc:
            st.error(f"Error al generar bundle: {exc}")
            json_str = "{}"
            reporte_val = None

    with col_preview:
        st.markdown("#### Resumen del contenido a empaquetar")
        if reporte_val:
            counts = reporte_val.counts
            c1, c2 = st.columns(2)
            c1.metric("Preguntas en bundle", counts.get("questions", 0))
            c2.metric("Preguntas servibles", counts.get("questions_served", 0))
            c3, c4 = st.columns(2)
            c3.metric("Nodos del manual", counts.get("nodes", 0))
            c4.metric("Chunks de texto", counts.get("chunks", 0))

            if reporte_val.warnings:
                with st.expander("Observaciones del contrato"):
                    for w in reporte_val.warnings:
                        st.info(f"ℹ {w}")

        with st.expander("Ver estructura preliminar (primeros 2 KB)"):
            st.code(json_str[:2000] + ("..." if len(json_str) > 2000 else ""), language="json")
