"""Orquestación de principio a fin: seleccionar nodos → generar → persistir."""

from __future__ import annotations

import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from etl.models.schema import Chunk, Manual, Node
from sqlalchemy import select
from sqlalchemy.orm import Session

from qgen.cost import CostEstimate, actual_cost_usd, doc_token_estimate
from qgen.db.persistence import (
    create_run,
    finalize_run,
    persist_question,
    remove_existing_questions_for_nodes,
)
from qgen.gemini.cache import build_or_get_cache, delete_cache
from qgen.gemini.generate import generate_one, generate_draft_questions
from qgen.models.schema import GenerationRun, Question
from qgen.prompts.creator import build_creator_instruction
from qgen.prompts.render import build_variable_prompt
from qgen.prompts.system import SYSTEM_VERSION, build_system_instruction
from qgen.rules.base import DocumentRules, RulesOverride, merge_rules, rules_to_dict
from qgen.rules.defaults import get_default_rules

# Módulo de logging en lugar de print() directo
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


# ---- Selección ------------------------------------------------------------

def _select_nodes(session: Session, *, manual_id: int, regenerate: bool, limit: int | None, only_node_id: int | None) -> list[Node]:
    stmt = (
        select(Node)
        .where(Node.manual_id == manual_id)
        .where(Node.id.in_(select(Chunk.node_id).where(Chunk.manual_id == manual_id)))
        .where(~Node.title.ilike('%introducci%'))
        .order_by(Node.sort_key)
    )
    if only_node_id is not None:
        stmt = stmt.where(Node.id == only_node_id)
    if not regenerate:
        existing = select(Question.node_id).where(Question.manual_id == manual_id)
        stmt = stmt.where(~Node.id.in_(existing))
    nodes = session.execute(stmt).scalars().all()
    if limit is not None:
        nodes = nodes[:limit]
    return list(nodes)

def _chunks_for(session: Session, node_id: int) -> list[Chunk]:
    return list(session.execute(select(Chunk).where(Chunk.node_id == node_id).order_by(Chunk.ordinal)).scalars().all())

def _resolve_rules(manual: Manual) -> tuple[DocumentRules, str]:
    profile = (manual.metadata_json or {}).get("profile") or "manual"
    default = get_default_rules(profile)
    override_dict = (manual.metadata_json or {}).get("question_rules")
    override = RulesOverride.from_dict(override_dict) if override_dict else None
    return merge_rules(default, override), profile

def _doc_token_estimate_from_chunks(session: Session, manual_id: int) -> int:
    total_chars = session.execute(select(Chunk.char_count).where(Chunk.manual_id == manual_id)).scalars().all()
    return doc_token_estimate(sum(total_chars))


# ---- Entrada Pública ------------------------------------------------

def estimate_only(session: Session, *, manual_id: int, model_name: str, mode: str, limit: int | None, only_node_id: int | None, regenerate: bool) -> tuple[CostEstimate, int]:
    nodes = _select_nodes(session, manual_id=manual_id, regenerate=regenerate, limit=limit, only_node_id=only_node_id)
    estimate = CostEstimate(
        model=model_name,
        mode=mode,
        n_questions=len(nodes),
        cache_tokens=0,
        input_tokens_per_q=0,
        output_tokens_per_q=0,
        cache_create_usd=0.0,
        cache_storage_usd=0.0,
        per_question_usd=0.0,
        total_usd=0.0,
    )
    return estimate, len(nodes)

def run_generation(session: Session, *, manual_id: int, model_name: str = "deepseek-r1:8b", mode: str = "immediate", limit: int | None = None, only_node_id: int | None = None, regenerate: bool = False, cache_ttl_seconds: int = 3600, progress_cb=None) -> RunSummary:
    manual = session.get(Manual, manual_id)
    if manual is None: raise ValueError(f"Manual {manual_id} not found")

    rules, profile = _resolve_rules(manual)
    nodes = _select_nodes(session, manual_id=manual_id, regenerate=regenerate, limit=limit, only_node_id=only_node_id)

    if regenerate and nodes:
        remove_existing_questions_for_nodes(session, manual_id=manual_id, node_ids=[n.id for n in nodes])

    if not nodes:
        run = create_run(session, manual_id=manual_id, model=model_name, mode=mode, profile_used=profile, rules_snapshot=rules_to_dict(rules), nodes_total=0)
        finalize_run(session, run=run, nodes_completed=0, nodes_failed=0, cost_input_tokens=0, cost_output_tokens=0, cost_cached_tokens=0, cost_estimate_usd=0.0, status="succeeded")
        return RunSummary(run_id=run.id, mode=mode, model=run.model, profile=profile, nodes_total=0, nodes_completed=0, nodes_failed=0, cost_estimate_usd=0.0, actual_cost_usd=0.0)

    creator_instruction = build_creator_instruction(rules)

    run = create_run(session, manual_id=manual_id, model=model_name, mode=mode, profile_used=profile, rules_snapshot=rules_to_dict(rules), nodes_total=len(nodes), cache_name="none", metadata_json={"system_version": SYSTEM_VERSION, "limit": limit, "only_node_id": only_node_id, "regenerate": regenerate})

    return _run_immediate(session, run, manual, nodes, rules, creator_instruction, progress_cb)


# ---- Controlador de Ejecución Inmediata -----------------------------------

def _run_immediate(session: Session, run: GenerationRun, manual: Manual, nodes: list[Node], rules: DocumentRules, creator_instruction: str, progress_cb) -> RunSummary:
    completed = 0
    failed = 0
    total_in = 0
    total_out = 0
    total_cached = 0

    # 1. Crear caché con el PDF (sin system_instruction global)
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
    except Exception as e:
        logger.warning("Error creando cache: %s", e)
        cache = None
        cache_name = "none"

    run.cache_name = cache_name
    session.commit()
    
    # 2. Pre-fetch: extraer datos puros (no ORM objects) para thread safety.
    #    Los hilos solo reciben strings y enteros, nunca objetos SQLAlchemy.
    node_jobs = []
    for node in nodes:
        chunks = _chunks_for(session, node.id)
        prompt = build_variable_prompt(node, chunks)
        text_chunk = "\n\n".join(c.text for c in chunks)
        node_jobs.append({
            "id": node.id,
            "prompt": prompt,
            "text_chunk": text_chunk,
            # Datos serializados del nodo para el callback (sin objeto ORM)
            "node_title": node.title,
            "node_breadcrumb": node.breadcrumb,
        })
    
    # Referencia local al modelo para los hilos (string, thread-safe)
    run_model = run.model

    def process_node(node_idx, job):
        """Función ejecutada en hilo worker. No toca la sesión de SQLAlchemy."""
        node_completed = 0
        node_failed = 0
        node_in = 0
        node_out = 0
        node_cached = 0
        
        prompt = job["prompt"]
        text_chunk = job["text_chunk"]
        
        preguntas_sugeridas = generate_draft_questions(
            cache=cache,
            model=run_model,
            variable_prompt=prompt, 
            system_instruction=creator_instruction
        )
            
        if not preguntas_sugeridas:
            node_failed += 1
            return (node_completed, node_failed, node_in, node_out, node_cached, [])

        results = []
        for pregunta in preguntas_sugeridas:
            pregunta_limpia = re.split(r'\b[A-D][\.\\)]\s', pregunta, maxsplit=1, flags=re.IGNORECASE)[0].strip()
            system_instruction = build_system_instruction(rules, target_question=pregunta_limpia)
            
            outcome = generate_one(
                cache=cache,
                model=run_model,
                variable_prompt=prompt, 
                system_instruction=system_instruction
            )

            if outcome.question is None:
                node_failed += 1
                continue

            # Validación Algorítmica (Python)
            validation_status = "pending"
            reviewer_notes = "Sin notas."
            
            correct_opt = next((o for o in outcome.question.options if o.role.value == "correct"), None)
            if correct_opt:
                txt_chunk_norm = re.sub(r'\s+', ' ', text_chunk).strip()
                opt_norm = re.sub(r'\s+', ' ', correct_opt.text).strip()
                if opt_norm not in txt_chunk_norm:
                    validation_status = "needs_review"
                    reviewer_notes = "Revisión automática: La respuesta correcta no es una cita literal (el modelo parafraseó)."
            
            metadata = {
                "provider": "gemini", 
                "input_tokens": outcome.input_tokens, 
                "output_tokens": outcome.output_tokens, 
                "cached_tokens": outcome.cached_tokens, 
                "latency_s": outcome.latency_s,
                "reviewer_notes": reviewer_notes,
                "reviewer_raw": json.dumps(outcome.raw_response)
            }
            
            results.append({
                "node_id": job["id"],
                "payload": outcome.question,
                "raw_response": outcome.raw_response,
                "metadata": metadata,
                "validation_status": validation_status
            })
            
            node_completed += 1
            node_in += outcome.input_tokens
            node_out += outcome.output_tokens
            node_cached += outcome.cached_tokens
            
        return (node_completed, node_failed, node_in, node_out, node_cached, results)

    # 3. Ejecutar peticiones concurrentemente
    max_workers = 15 if cache else 2  # Sin cache → Free Tier / límite restrictivo
    order = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_node, idx, job): (idx, job) for idx, job in enumerate(node_jobs)}
        
        for future in as_completed(futures):
            idx, job = futures[future]
            c, f, i, o, ca, res = future.result()
            completed += c
            failed += f
            total_in += i
            total_out += o
            total_cached += ca

            # Callback de progreso con datos serializados (hilo principal)
            if progress_cb:
                for r in res:
                    progress_cb(idx, len(nodes), job, r["payload"], None)
                if f > 0 and not res:
                    progress_cb(idx, len(nodes), job, None, "Error extrayendo preguntas")
            
            # Persistencia en el hilo principal (thread-safe)
            for r in res:
                persist_question(
                    session, run=run, node_id=r["node_id"], manual_id=manual.id, generation_order=order, payload=r["payload"], raw_response=r["raw_response"],
                    metadata=r["metadata"], validation_status=r["validation_status"]
                )
                order += 1
            
            # Commit periódico para no perder progreso
            session.commit()

    if cache:
        delete_cache(cache)

    # Cálculo del costo real usando los tokens observados
    computed_cost = actual_cost_usd(
        model=run.model,
        mode=run.mode,
        input_tokens=total_in,
        output_tokens=total_out,
        cached_tokens=total_cached,
    )
    finalize_run(session, run=run, nodes_completed=completed, nodes_failed=failed, cost_input_tokens=total_in, cost_output_tokens=total_out, cost_cached_tokens=total_cached, cost_estimate_usd=computed_cost, status="succeeded" if failed == 0 else "partial")
    session.commit()

    return RunSummary(run_id=run.id, mode=run.mode, model=run.model, profile=run.profile_used, nodes_total=len(nodes), nodes_completed=completed, nodes_failed=failed, cost_estimate_usd=0.0, actual_cost_usd=computed_cost, cache_name=cache_name)

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