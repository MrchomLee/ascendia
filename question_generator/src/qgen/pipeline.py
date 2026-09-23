"""Orquestación de principio a fin (spec §4–§8).

nodos → ventanas pendientes → una llamada por ventana → revisión de cada
pregunta (y verificación de los ejercicios nuevos) → descarte de duplicadas →
guardado. Una corrida se puede cortar y retomar: la siguiente solo procesa las
ventanas que faltan.
"""

from __future__ import annotations

import logging
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

from etl.models.schema import Chunk, Manual, Node
from sqlalchemy import select
from sqlalchemy.orm import Session

from qgen.cost import WindowEstimate, actual_cost_usd, doc_token_estimate, estimate_windows
from qgen.db.persistence import create_run, finalize_run, persist_question, remove_questions_for_windows
from qgen.gemini.cache import build_or_get_cache, delete_cache
from qgen.gemini.client import MODEL_FLASH, resolve_model
from qgen.gemini.generate import generate_window, verify_exercise
from qgen.models.schema import GenerationRun, Question
from qgen.prompts.families import (
    SYSTEM_VERSION,
    build_verification_instruction,
    build_verification_message,
    build_window_instruction,
    build_window_message,
)
from qgen.prompts.schemas import QuestionType, WindowQuestion
from qgen.reference.repository import get_reference_exemplars
from qgen.rules.base import DocumentRules, RulesOverride, merge_rules, rules_to_dict
from qgen.rules.defaults import get_default_rules
from qgen.validation.checks import (
    DuplicateIndex,
    Verdict,
    parse_items,
    review,
    tipo_permitido,
    to_generated,
    verification_motivos,
    verification_options,
)
from qgen.windows import Window, build_windows

logger = logging.getLogger(__name__)


@dataclass
class RunSummary:
    run_id: int
    mode: str
    model: str
    profile: str
    nodes_total: int
    nodes_completed: int
    nodes_failed: int
    cost_estimate_usd: float
    actual_cost_usd: float
    batch_job_id: str | None = None
    cache_name: str | None = None
    windows_total: int = 0
    windows_failed: int = 0
    questions_saved: int = 0


# ---- Ventanas (spec §4) ---------------------------------------------------


@dataclass(frozen=True)
class WindowJob:
    """Una ventana por procesar, con lo que hace falta del nodo (sin objetos ORM: viaja a los hilos)."""

    window: Window
    node_id: int
    node_label: str
    node_title: str
    node_breadcrumb: str


def _nodes_with_text(session: Session, *, manual_id: int, only_node_id: int | None) -> list[Node]:
    stmt = (
        select(Node)
        .where(Node.manual_id == manual_id)
        .where(Node.id.in_(select(Chunk.node_id).where(Chunk.manual_id == manual_id)))
        .where(~Node.title.ilike("%introducci%"))
        .order_by(Node.sort_key)
    )
    if only_node_id is not None:
        stmt = stmt.where(Node.id == only_node_id)
    return list(session.execute(stmt).scalars().all())


def _chunks_for(session: Session, node_id: int) -> list[Chunk]:
    return list(session.execute(select(Chunk).where(Chunk.node_id == node_id).order_by(Chunk.ordinal)).scalars().all())


def _done_window_keys(session: Session, manual_id: int) -> set[str]:
    """Ventanas ya procesadas: `ok` en alguna corrida anterior, o con preguntas guardadas
    (esto último cubre una corrida que murió sin llegar a cerrarse)."""
    done: set[str] = set()
    for meta in session.execute(
        select(GenerationRun.metadata_json).where(GenerationRun.manual_id == manual_id)
    ).scalars():
        done |= {key for key, estado in ((meta or {}).get("ventanas") or {}).items() if estado == "ok"}
    done |= set(
        session.execute(
            select(Question.window_key)
            .where(Question.manual_id == manual_id)
            .where(Question.window_key.is_not(None))
            .distinct()
        ).scalars()
    )
    return done


def plan_windows(
    session: Session,
    *,
    manual_id: int,
    only_node_id: int | None = None,
    regenerate: bool = False,
    limit: int | None = None,
) -> list[WindowJob]:
    """Las ventanas que le tocan a esta corrida, en orden de nodo. `limit` cuenta ventanas."""
    done = set() if regenerate else _done_window_keys(session, manual_id)
    jobs: list[WindowJob] = []
    for node in _nodes_with_text(session, manual_id=manual_id, only_node_id=only_node_id):
        for window in build_windows(node.id, _chunks_for(session, node.id)):
            if window.key in done:
                continue
            jobs.append(WindowJob(
                window=window,
                node_id=node.id,
                node_label=f"{node.level_label} {node.ordinal}".strip(),
                node_title=node.title,
                node_breadcrumb=node.breadcrumb,
            ))
    return jobs[:limit] if limit is not None else jobs


# ---- Reglas y costo -------------------------------------------------------


def _resolve_rules(manual: Manual) -> tuple[DocumentRules, str]:
    profile = (manual.metadata_json or {}).get("profile") or "manual"
    default = get_default_rules(profile)
    override_dict = (manual.metadata_json or {}).get("question_rules")
    override = RulesOverride.from_dict(override_dict) if override_dict else None
    return merge_rules(default, override), profile


def _doc_token_estimate_from_chunks(session: Session, manual_id: int) -> int:
    total_chars = session.execute(select(Chunk.char_count).where(Chunk.manual_id == manual_id)).scalars().all()
    return doc_token_estimate(sum(total_chars))


def estimate_only(
    session: Session,
    *,
    manual_id: int,
    model_name: str,
    mode: str,
    limit: int | None,
    only_node_id: int | None,
    regenerate: bool,
) -> tuple[WindowEstimate, int]:
    """Costo aproximado sin llamar a Gemini; el entero son las ventanas por procesar."""
    model_name = resolve_model(model_name)
    manual = session.get(Manual, manual_id)
    if manual is None:
        raise ValueError(f"Manual {manual_id} not found")
    rules, _ = _resolve_rules(manual)
    jobs = plan_windows(session, manual_id=manual_id, only_node_id=only_node_id, regenerate=regenerate, limit=limit)
    # Sin ventanas no se crea cache: no hay nada que cobrar.
    doc_tokens = _doc_token_estimate_from_chunks(session, manual_id) if jobs else 0
    estimate = estimate_windows(
        model=model_name,
        mode=mode,
        windows=len(jobs),
        window_chars=sum(len(job.window.text) for job in jobs),
        with_exercises="ejercicio" in rules.tipos,
        doc_tokens=doc_tokens,
    )
    return estimate, len(jobs)


# ---- Entrada pública ------------------------------------------------------


def run_generation(
    session: Session,
    *,
    manual_id: int,
    model_name: str = MODEL_FLASH,
    mode: str = "immediate",
    limit: int | None = None,
    only_node_id: int | None = None,
    regenerate: bool = False,
    cache_ttl_seconds: int = 3600,
    progress_cb=None,
) -> RunSummary:
    model_name = resolve_model(model_name)
    manual = session.get(Manual, manual_id)
    if manual is None:
        raise ValueError(f"Manual {manual_id} not found")

    rules, profile = _resolve_rules(manual)
    jobs = plan_windows(session, manual_id=manual_id, only_node_id=only_node_id, regenerate=regenerate, limit=limit)
    node_ids = sorted({job.node_id for job in jobs})

    if regenerate and jobs:
        remove_questions_for_windows(
            session, manual_id=manual_id, window_keys=[job.window.key for job in jobs], node_ids=node_ids,
        )

    if not jobs:
        run = create_run(session, manual_id=manual_id, model=model_name, mode=mode, profile_used=profile, rules_snapshot=rules_to_dict(rules), nodes_total=0)
        finalize_run(session, run=run, nodes_completed=0, nodes_failed=0, cost_input_tokens=0, cost_output_tokens=0, cost_cached_tokens=0, cost_estimate_usd=0.0, status="succeeded")
        return RunSummary(run_id=run.id, mode=mode, model=run.model, profile=profile, nodes_total=0, nodes_completed=0, nodes_failed=0, cost_estimate_usd=0.0, actual_cost_usd=0.0)

    manual_title = manual.title or manual.code
    exemplars = get_reference_exemplars(session, profile=profile, manual_code=manual.code, limit=5)
    instruction = build_window_instruction(rules, manual_title=manual_title, exemplars=exemplars or None)

    run = create_run(
        session, manual_id=manual_id, model=model_name, mode=mode, profile_used=profile,
        rules_snapshot=rules_to_dict(rules), nodes_total=len(node_ids), cache_name="none",
        metadata_json={"system_version": SYSTEM_VERSION, "limit": limit, "only_node_id": only_node_id, "regenerate": regenerate},
    )
    return _run_immediate(session, run, manual, jobs, rules, instruction, manual_title, progress_cb)


# ---- Controlador de ejecución inmediata -----------------------------------


@dataclass
class _Accepted:
    question: WindowQuestion
    verdict: Verdict
    verificacion: dict | None


@dataclass
class _WindowResult:
    job: WindowJob
    error: str | None = None
    accepted: list[_Accepted] = field(default_factory=list)
    descartes: list[str] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    latency_s: float = 0.0


def _run_immediate(
    session: Session,
    run: GenerationRun,
    manual: Manual,
    jobs: list[WindowJob],
    rules: DocumentRules,
    instruction: str,
    manual_title: str,
    progress_cb,
) -> RunSummary:
    total_in = total_out = total_cached = 0
    ventanas: dict[str, str] = {}
    failures: list[dict] = []  # por qué falló cada ventana: una corrida `partial` ya se pagó
    descartes: list[dict] = []
    conteo: Counter[str] = Counter()
    saved = 0
    cache = None
    cache_name = "none"
    cache_started = time.monotonic()
    executor: ThreadPoolExecutor | None = None
    node_of = {job.window.key: job.node_id for job in jobs}
    planned = Counter(job.node_id for job in jobs)

    duplicados = DuplicateIndex()
    for node_id, texto, tipo in session.execute(
        select(Question.node_id, Question.question_text, Question.question_type).where(Question.manual_id == manual.id)
    ):
        duplicados.add(node_id, texto, tipo)

    def finalize(status: str) -> float:
        """Cierra la corrida con lo gastado hasta ahora, incluida la creación y el almacenamiento del cache."""
        cache_tokens = cache.token_count if cache else 0
        cache_hours = (time.monotonic() - cache_started) / 3600 if cache else 0.0
        cost = actual_cost_usd(
            model=run.model,
            mode=run.mode,
            input_tokens=total_in,
            output_tokens=total_out,
            cached_tokens=total_cached,
            cache_create_tokens=cache_tokens,
            cache_storage_token_hours=cache_tokens * cache_hours,
        )
        ok = Counter(node_of[key] for key, estado in ventanas.items() if estado == "ok")
        fallidos = {node_of[key] for key, estado in ventanas.items() if estado == "fallida"}
        run.metadata_json = {
            **(run.metadata_json or {}),
            "cache_tokens": cache_tokens,
            "cache_hours": round(cache_hours, 4),
            "ventanas": dict(ventanas),
            "preguntas": dict(conteo),
            "descartes": list(descartes),
            "failures": list(failures),
        }
        finalize_run(
            session, run=run,
            nodes_completed=sum(1 for node_id, total in planned.items() if ok[node_id] == total),
            nodes_failed=len(fallidos),
            cost_input_tokens=total_in, cost_output_tokens=total_out, cost_cached_tokens=total_cached,
            cost_estimate_usd=cost, status=status,
        )
        session.commit()
        return cost

    try:
        # 1. Cache con el PDF (sin system_instruction global); si falla, se sigue sin él.
        pdf_path = Path(manual.source_path)
        if not pdf_path.exists():
            pdf_path = Path(f"data/raw_pdfs/{manual.code}.pdf")
        try:
            cache = build_or_get_cache(
                pdf_path=pdf_path,
                model=run.model,
                system_version=SYSTEM_VERSION,
                display_name=f"Manual_{manual.code}",
            )
            cache_name = cache.name
            cache_started = time.monotonic()
        except Exception as e:
            logger.warning("Error creando cache: %s", e)
        run.cache_name = cache_name
        session.commit()

        run_model = run.model  # string: seguro entre hilos
        verification_instruction = build_verification_instruction()

        def process(job: WindowJob) -> _WindowResult:
            """Hilo de trabajo: llamadas a Gemini y revisiones; no toca la sesión de SQLAlchemy."""
            outcome = generate_window(
                cache=cache,
                model=run_model,
                message=build_window_message(job.window, manual_title=manual_title, breadcrumb=job.node_breadcrumb),
                system_instruction=instruction,
            )
            result = _WindowResult(
                job=job, input_tokens=outcome.input_tokens, output_tokens=outcome.output_tokens,
                cached_tokens=outcome.cached_tokens, latency_s=outcome.latency_s,
            )
            if outcome.error is not None:
                result.error = outcome.error
                return result

            preguntas, result.descartes = parse_items(outcome.items)
            for q in preguntas:
                if not tipo_permitido(q, rules.tipos):
                    result.descartes.append(f"tipo {q.tipo.value} no permitido en {rules.name}")
                    continue
                verdict = review(q, job.window.text)
                verificacion = None
                if q.tipo == QuestionType.EJERCICIO_NUEVO:
                    textos, letra = verification_options(q)
                    check = verify_exercise(
                        model=run_model,
                        message=build_verification_message(q.pregunta, textos, q.cita),
                        system_instruction=verification_instruction,
                    )
                    result.input_tokens += check.input_tokens
                    result.output_tokens += check.output_tokens
                    result.cached_tokens += check.cached_tokens
                    verdict = verdict.with_motivos(verification_motivos(check.result, letra))
                    verificacion = check.result.model_dump() if check.result else {"error": check.error}
                result.accepted.append(_Accepted(question=q, verdict=verdict, verificacion=verificacion))
            return result

        # 2. Ventanas en paralelo. Sin `with`: al salir de un `with` el executor espera
        #    a TODAS las ventanas encoladas, así que un Ctrl-C no cortaría nada.
        executor = ThreadPoolExecutor(max_workers=15 if cache else 2)  # sin cache → plan gratuito
        futures = {executor.submit(process, job): job for job in jobs}
        order = 0

        for idx, future in enumerate(as_completed(futures)):
            result = future.result()
            job = result.job
            key = job.window.key
            total_in += result.input_tokens
            total_out += result.output_tokens
            total_cached += result.cached_tokens

            if result.error is not None:
                ventanas[key] = "fallida"
                failures.append({"window_key": key, "node_id": job.node_id, "error": result.error})
                logger.warning("%s [%s]: %s", job.node_label, key, result.error)
                if progress_cb:
                    progress_cb(idx, len(jobs), job, None, result.error)
                continue

            descartadas = len(result.descartes)
            descartes.extend({"window_key": key, "motivo": motivo} for motivo in result.descartes)
            guardadas = revision = 0
            for accepted in result.accepted:
                q = accepted.question
                if duplicados.is_duplicate(job.node_id, q.pregunta, q.tipo.value):
                    descartes.append({"window_key": key, "motivo": "duplicada"})
                    descartadas += 1
                    continue
                duplicados.add(job.node_id, q.pregunta, q.tipo.value)
                # 3. Persistencia en el hilo principal.
                persist_question(
                    session, run=run, node_id=job.node_id, manual_id=manual.id, generation_order=order,
                    payload=to_generated(q),
                    raw_response={"ventana": key, "item": q.model_dump(mode="json")},
                    metadata={
                        "provider": "gemini",
                        "paginas": [job.window.page_start, job.window.page_end],
                        "motivos": list(accepted.verdict.motivos),
                        "verificacion": accepted.verificacion,
                        "ventana_tokens": {"input": result.input_tokens, "output": result.output_tokens},
                        "latencia_ventana_s": round(result.latency_s, 2),
                    },
                    validation_status=accepted.verdict.status,
                    question_type=q.tipo.value,
                    source_quote=q.cita,
                    window_key=key,
                )
                order += 1
                saved += 1
                guardadas += 1
                revision += accepted.verdict.status == "needs_review"
                conteo[f"{q.tipo.value}/{accepted.verdict.status}"] += 1
            ventanas[key] = "ok"
            # Se guarda antes del callback: si el callback falla o se corta la corrida,
            # lo generado ya quedó.
            session.commit()
            if progress_cb:
                progress_cb(idx, len(jobs), job, {"guardadas": guardadas, "revision": revision, "descartes": descartadas}, None)

        computed_cost = finalize("succeeded" if not failures else "partial")
    except BaseException as exc:
        # Una corrida no puede quedarse en `running`: el exportador no entrega
        # corridas a medias. Lo ya guardado se conserva y se retoma después.
        session.rollback()
        finalize("cancelled" if isinstance(exc, KeyboardInterrupt) else "failed")
        raise
    finally:
        if executor is not None:
            executor.shutdown(wait=False, cancel_futures=True)
        if cache:
            delete_cache(cache)

    return RunSummary(
        run_id=run.id, mode=run.mode, model=run.model, profile=run.profile_used,
        nodes_total=run.nodes_total, nodes_completed=run.nodes_completed, nodes_failed=run.nodes_failed,
        cost_estimate_usd=0.0, actual_cost_usd=computed_cost, cache_name=cache_name,
        windows_total=len(jobs), windows_failed=len(failures), questions_saved=saved,
    )


# ---- Batch desactivado ----
def _run_batch_submit(*args, **kwargs): raise NotImplementedError("No compatible con Ollama local.")
def finalize_batch_run(*args, **kwargs): raise NotImplementedError("No compatible con Ollama local.")


def _run_summary_from_db(run: GenerationRun) -> RunSummary:
    """Construye un RunSummary a partir de una corrida persistida en la base de datos."""
    return RunSummary(
        run_id=run.id,
        mode=run.mode,
        model=run.model,
        profile=run.profile_used,
        nodes_total=run.nodes_total,
        nodes_completed=run.nodes_completed,
        nodes_failed=run.nodes_failed,
        cost_estimate_usd=run.cost_estimate_usd,
        actual_cost_usd=run.cost_estimate_usd,
        batch_job_id=run.batch_job_id,
        cache_name=run.cache_name,
    )
