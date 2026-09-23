"""Formato del bundle de contenido (v1 y v2).

La especificación en prosa vive en los dos repos: `CONTRATO-BUNDLE.md` en el de
contenido, `docs/06-contrato-bundle-de-contenido.md` en el de la webapp.

Este módulo es la **única implementación** del contrato: lo importan tanto el
exportador (`qgen-export`, lado contenido) como el importador
(`etl/scripts/import_bundle.py`, lado webapp). Los dos validan con el mismo
código, así que un bundle que el exportador acepta es un bundle que el
importador acepta.

Solo stdlib, a propósito: el importador tiene que poder correr sin las
dependencias pesadas del pipeline (docling, torch, pydantic…).
"""

from __future__ import annotations

import gzip
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

BUNDLE_VERSION = 2
SUPPORTED_VERSIONS = frozenset({1, 2})

# Por encima de esto el bundle se escribe como `.json.gz`.
GZIP_THRESHOLD_BYTES = 25 * 1024 * 1024

VALIDATION_STATUSES = frozenset({"pending", "valid", "needs_review", "rejected"})
#: Solo estos dos se sirven a los alumnos; ver `questions.validation_status`.
SERVED_STATUSES = frozenset({"pending", "valid"})

#: Tipos de pregunta (v2).
QUESTION_TYPES = frozenset({"teoria", "ejercicio_libro", "ejercicio_nuevo"})

RUN_MODES = frozenset({"immediate", "batch"})
#: `running` queda fuera: una corrida a medias no se entrega.
RUN_STATUSES = frozenset({"succeeded", "failed", "partial", "cancelled"})

ROLE_COUNTS: dict[str, int] = {
    "correct": 1,
    "confusa": 1,
    "distractor": 2,
}
OPTIONS_PER_QUESTION = sum(ROLE_COUNTS.values())

# Lo que aguanta cada columna del otro lado.
MAX_LEN: dict[str, int] = {
    "manual_code": 64,
    "manual_edition": 64,
    "manual_title": 512,
    "manual_branch": 64,
    "node_level_label": 32,
    "node_ordinal": 64,
    "node_title": 1024,
    "node_ref": 64,
    "question_text": 1000,
    "justification": 2000,
    "source_quote": 2000,
    "option_text": 500,
    "run_model": 64,
    "run_profile": 32,
}

_ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")
_SLUG_RE = re.compile(r"[^a-z0-9._-]+")
_FILENAME_RE = re.compile(r"^(?P<code>[a-z0-9._-]+)--(?P<date>\d{8})--v(?P<version>\d+)\.json(\.gz)?$")

# Cosas que no tienen por qué viajar en un bundle. Se buscan en los bloques
# libres (`metadata`, `rules_snapshot`), que es donde podría colarse algo.
_SECRET_VALUE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("clave de Google AI", re.compile(r"AIza[0-9A-Za-z_\-]{20,}")),
    ("clave estilo OpenAI", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("cadena de conexión con contraseña", re.compile(r"\b[a-z][a-z0-9+.\-]*://[^\s:/@]+:[^\s@]+@")),
    ("clave privada PEM", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]
# El nombre completo del campo, no una subcadena: si no, `cost_input_tokens`
# saltaría como si fuera un token de autenticación.
_SECRET_KEY_RE = re.compile(
    r"^(api[_-]?keys?|secrets?|passwords?|passwd|tokens?|credentials?|authorizations?)$",
    re.IGNORECASE,
)
_SECRET_MIN_LEN = 12


# ─── Serialización ─────────────────────────────────────────────────────────


def iso(value: datetime | None) -> str | None:
    """Fecha en el formato del contrato: ISO 8601 UTC con `Z`.

    SQLite devuelve los `DateTime(timezone=True)` sin `tzinfo`. Lo que guarda el
    pipeline siempre es UTC (`datetime.now(timezone.utc)`), así que un valor
    ingenuo se interpreta como UTC en vez de como hora local.
    """
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_ref(model: str, mode: str, started_at: datetime) -> str:
    """Clave estable de una corrida: `{model}--{mode}--{inicio compacto UTC}`."""
    stamp = iso(started_at) or ""
    return f"{model}--{mode}--{stamp.replace('-', '').replace(':', '')}"


def dumps(bundle: dict[str, Any]) -> str:
    """Serialización canónica: UTF-8, indentado a 2, sin escapar acentos."""
    return json.dumps(bundle, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def slug(value: str) -> str:
    return _SLUG_RE.sub("-", value.strip().lower()).strip("-.") or "manual"


def bundle_filename(code: str, day: date, version: int) -> str:
    return f"{slug(code)}--{day.strftime('%Y%m%d')}--v{version}.json"


def next_version(out_dir: Path, code: str) -> int:
    """Siguiente `v{n}` libre para este manual en `out_dir`.

    Se cuenta por manual y no por fecha: `v3` es la tercera entrega de ese
    manual, se haya hecho el mismo día que la segunda o tres semanas después.
    """
    prefix = slug(code)
    highest = 0
    if out_dir.is_dir():
        for path in out_dir.iterdir():
            match = _FILENAME_RE.match(path.name)
            if match and match.group("code") == prefix:
                highest = max(highest, int(match.group("version")))
    return highest + 1


def write_bundle(path: Path, bundle: dict[str, Any]) -> tuple[Path, str]:
    """Escribe el bundle (comprimiendo si es grande) y su `.sha256`.

    Devuelve `(ruta final, checksum)`. La ruta final lleva `.gz` si el JSON
    superaba el umbral, así que hay que usar la que devuelve, no la que entró.
    """
    payload = dumps(bundle).encode("utf-8")
    if len(payload) > GZIP_THRESHOLD_BYTES:
        path = path.with_suffix(path.suffix + ".gz")
        # mtime=0: el mismo contenido produce el mismo fichero byte a byte.
        payload = gzip.compress(payload, mtime=0)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)

    checksum = hashlib.sha256(payload).hexdigest()
    path.with_name(path.name + ".sha256").write_text(
        f"{checksum}  {path.name}\n", encoding="utf-8"
    )
    return path, checksum


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_checksum(path: Path) -> None:
    """Comprueba el `.sha256` que acompaña al bundle. Lanza si no cuadra."""
    sidecar = path.with_name(path.name + ".sha256")
    if not sidecar.exists():
        raise FileNotFoundError(
            f"Falta el checksum {sidecar.name}. Sin él no se puede saber si el "
            f"bundle llegó entero; pide que te lo reenvíen o salta la "
            f"comprobación a sabiendas con --skip-checksum."
        )
    expected = sidecar.read_text(encoding="utf-8").split()[0].strip().lower()
    actual = sha256_of(path)
    if expected != actual:
        raise ValueError(
            f"El checksum de {path.name} no cuadra: el fichero se corrompió o "
            f"cambió después de exportarse.\n  esperado: {expected}\n  real:     {actual}"
        )


def read_bundle(path: Path) -> dict[str, Any]:
    """Lee un bundle `.json` o `.json.gz`. No valida: para eso está `validate`."""
    raw = gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: la raíz del bundle debe ser un objeto JSON.")
    return data


# ─── Validación ────────────────────────────────────────────────────────────


@dataclass
class Report:
    """Resultado de validar un bundle.

    `errors` bloquea (no se exporta, no se importa). `warnings` no bloquea pero
    conviene mirarlo antes de dar una entrega por buena.
    """

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def _is_iso(value: Any) -> bool:
    return isinstance(value, str) and bool(_ISO_RE.match(value))


def _text(report: Report, obj: Any, key: str, where: str, *, limit_key: str | None = None,
          required: bool = True, allow_empty: bool = False) -> str | None:
    value = obj.get(key) if isinstance(obj, dict) else None
    if value is None:
        if required:
            report.error(f"{where}: falta `{key}`.")
        return None
    if not isinstance(value, str):
        report.error(f"{where}: `{key}` debe ser texto, llegó {type(value).__name__}.")
        return None
    if not allow_empty and not value.strip():
        report.error(f"{where}: `{key}` viene vacío.")
        return None
    if limit_key:
        limit = MAX_LEN[limit_key]
        if len(value) > limit:
            report.error(f"{where}: `{key}` mide {len(value)} caracteres, el máximo es {limit}.")
    return value


def _int(report: Report, obj: Any, key: str, where: str, *, required: bool = True,
         minimum: int | None = None) -> int | None:
    value = obj.get(key) if isinstance(obj, dict) else None
    if value is None:
        if required:
            report.error(f"{where}: falta `{key}`.")
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        report.error(f"{where}: `{key}` debe ser entero, llegó {type(value).__name__}.")
        return None
    if minimum is not None and value < minimum:
        report.error(f"{where}: `{key}` = {value}, no puede ser menor que {minimum}.")
    return value


def _bool(report: Report, obj: Any, key: str, where: str) -> None:
    if not isinstance(obj.get(key), bool):
        report.error(f"{where}: `{key}` debe ser booleano.")


def _dict(report: Report, obj: Any, key: str, where: str) -> None:
    value = obj.get(key)
    if value is not None and not isinstance(value, dict):
        report.error(f"{where}: `{key}` debe ser un objeto JSON.")


def _stamp(report: Report, obj: Any, key: str, where: str, *, required: bool = True) -> None:
    value = obj.get(key) if isinstance(obj, dict) else None
    if value is None:
        if required:
            report.error(f"{where}: falta `{key}`.")
        return
    if not _is_iso(value):
        report.error(f"{where}: `{key}` debe ser ISO 8601 UTC con Z (`2026-08-17T10:15:00Z`), llegó {value!r}.")


def find_secrets(bundle: dict[str, Any]) -> list[str]:
    """Rutas dentro del bundle que parecen contener un secreto.

    Un bundle es un fichero que viaja por correo, chat o un repo: que arrastre
    una API key es más fácil de lo que parece, porque `metadata` y
    `rules_snapshot` son objetos libres que el pipeline llena sin mirar.
    """
    hits: list[str] = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                here = f"{path}.{key}"
                if (
                    _SECRET_KEY_RE.match(key)
                    and isinstance(value, str)
                    and len(value.strip()) >= _SECRET_MIN_LEN
                ):
                    hits.append(f"{here} (el nombre del campo delata un secreto)")
                    continue
                walk(value, here)
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, f"{path}[{i}]")
        elif isinstance(node, str):
            for label, pattern in _SECRET_VALUE_PATTERNS:
                if pattern.search(node):
                    hits.append(f"{path} ({label})")
                    break

    walk(bundle, "$")
    return hits


def validate(bundle: Any) -> Report:
    """Las diez comprobaciones del §5 del contrato, en orden.

    No lanza: devuelve un `Report` con todo lo que encontró, para poder arreglar
    varias cosas de una pasada en vez de una por corrida.
    """
    report = Report()
    if not isinstance(bundle, dict):
        report.error("La raíz del bundle debe ser un objeto JSON.")
        return report

    # (2) versión
    version = bundle.get("bundle_version")
    if version not in SUPPORTED_VERSIONS:
        report.error(
            f"`bundle_version` = {version!r}; este importador entiende "
            f"{sorted(SUPPORTED_VERSIONS)}. Hay que actualizar el importador."
        )
        return report  # sin versión conocida, el resto de checks no significan nada

    # (3) cabecera
    _stamp(report, bundle, "generated_at", "raíz")
    generator = bundle.get("generator")
    if not isinstance(generator, dict):
        report.error("raíz: falta `generator` (o no es un objeto).")
    else:
        _text(report, generator, "tool", "generator")
        _text(report, generator, "version", "generator")

    manual = bundle.get("manual")
    if not isinstance(manual, dict):
        report.error("raíz: falta `manual` (o no es un objeto).")
        return report

    _text(report, manual, "code", "manual", limit_key="manual_code")
    _text(report, manual, "title", "manual", limit_key="manual_title")
    _text(report, manual, "source_path", "manual")
    _text(report, manual, "extractor_used", "manual")
    _int(report, manual, "page_count", "manual", minimum=0)
    _stamp(report, manual, "ingested_at", "manual")
    _dict(report, manual, "metadata", "manual")
    for optional, limit in (("edition", "manual_edition"), ("branch", "manual_branch")):
        if manual.get(optional) is not None:
            _text(report, manual, optional, "manual", limit_key=limit)

    hint = bundle.get("catalog_hint")
    if hint is not None:
        if not isinstance(hint, dict):
            report.error("raíz: `catalog_hint` debe ser un objeto o `null`.")
        else:
            for key in ("grado_code", "materia_code"):
                if hint.get(key) is not None:
                    _text(report, hint, key, "catalog_hint")

    for key in ("nodes", "runs", "questions"):
        if not isinstance(bundle.get(key), list):
            report.error(f"raíz: `{key}` debe ser una lista.")
    if report.errors:
        return report

    nodes: list[Any] = bundle["nodes"]
    runs: list[Any] = bundle["runs"]
    questions: list[Any] = bundle["questions"]

    # (4) árbol
    node_refs: set[str] = set()
    parents: dict[str, str | None] = {}
    n_chunks = 0
    for i, node in enumerate(nodes):
        where = f"nodes[{i}]"
        if not isinstance(node, dict):
            report.error(f"{where}: debe ser un objeto.")
            continue
        ref = _text(report, node, "ref", where, limit_key="node_ref")
        if ref is not None:
            if ref in node_refs:
                report.error(
                    f"{where}: `ref` {ref!r} repetido. El `ref` sale del `sort_key` "
                    f"del ensamblador y debe ser único dentro del manual."
                )
            node_refs.add(ref)
            parents[ref] = node.get("parent_ref")
        else:
            ref = f"<{where}>"

        parent_ref = node.get("parent_ref")
        if parent_ref is not None and not isinstance(parent_ref, str):
            report.error(f"{where}: `parent_ref` debe ser texto o `null`.")

        _int(report, node, "level", where, minimum=0)
        _text(report, node, "level_label", where, limit_key="node_level_label")
        _text(report, node, "ordinal", where, limit_key="node_ordinal", allow_empty=True)
        _text(report, node, "title", where, limit_key="node_title")
        _text(report, node, "breadcrumb", where, allow_empty=True)
        _int(report, node, "page_start", where, minimum=0)
        _int(report, node, "page_end", where, required=False, minimum=0)
        _bool(report, node, "is_anexo", where)
        _dict(report, node, "metadata", where)

        chunks = node.get("chunks")
        if not isinstance(chunks, list):
            report.error(f"{where}: `chunks` debe ser una lista (vacía si el nodo no tiene texto).")
            continue
        seen_ordinals: set[int] = set()
        for j, chunk in enumerate(chunks):
            cwhere = f"{where}.chunks[{j}]"
            if not isinstance(chunk, dict):
                report.error(f"{cwhere}: debe ser un objeto.")
                continue
            ordinal = _int(report, chunk, "ordinal", cwhere, minimum=0)
            if ordinal is not None:
                if ordinal in seen_ordinals:
                    report.error(f"{cwhere}: `ordinal` {ordinal} repetido dentro del nodo {ref}.")
                seen_ordinals.add(ordinal)
            _text(report, chunk, "text", cwhere)
            _int(report, chunk, "char_count", cwhere, minimum=0)
            _int(report, chunk, "page_start", cwhere, minimum=0)
            _int(report, chunk, "page_end", cwhere, minimum=0)
            _bool(report, chunk, "has_table", cwhere)
            _bool(report, chunk, "has_image_ref", cwhere)
            _dict(report, chunk, "metadata", cwhere)
            n_chunks += 1

    for ref, parent_ref in parents.items():
        if parent_ref is not None and parent_ref not in node_refs:
            report.error(f"nodo {ref}: su `parent_ref` {parent_ref!r} no está en el bundle.")

    if node_refs and not any(p is None for p in parents.values()):
        report.error("El árbol no tiene raíz: todos los nodos declaran un padre.")

    for ref in parents:
        seen: set[str] = set()
        cursor: str | None = ref
        while cursor is not None and cursor in parents and cursor not in seen:
            seen.add(cursor)
            cursor = parents[cursor]
        if cursor is not None and cursor in seen:
            report.error(f"nodo {ref}: la cadena de `parent_ref` forma un ciclo.")
            break

    # (6) corridas
    run_refs: set[str] = set()
    for i, run in enumerate(runs):
        where = f"runs[{i}]"
        if not isinstance(run, dict):
            report.error(f"{where}: debe ser un objeto.")
            continue
        ref = _text(report, run, "ref", where)
        if ref is not None:
            if ref in run_refs:
                report.error(f"{where}: `ref` {ref!r} repetido.")
            run_refs.add(ref)

        _text(report, run, "model", where, limit_key="run_model")
        _text(report, run, "profile_used", where, limit_key="run_profile")
        mode = run.get("mode")
        if mode not in RUN_MODES:
            report.error(f"{where}: `mode` = {mode!r}; debe ser uno de {sorted(RUN_MODES)}.")
        status = run.get("status")
        if status == "running":
            report.error(
                f"{where}: la corrida sigue en `running`. Una generación a medias no se "
                f"entrega: espera a que termine (o márcala como `partial`)."
            )
        elif status not in RUN_STATUSES:
            report.error(f"{where}: `status` = {status!r}; debe ser uno de {sorted(RUN_STATUSES)}.")

        _stamp(report, run, "started_at", where)
        _stamp(report, run, "completed_at", where, required=False)
        for key in ("nodes_total", "nodes_completed", "nodes_failed",
                    "cost_input_tokens", "cost_output_tokens", "cost_cached_tokens"):
            _int(report, run, key, where, minimum=0)
        cost = run.get("cost_estimate_usd")
        if not isinstance(cost, (int, float)) or isinstance(cost, bool) or cost < 0:
            report.error(f"{where}: `cost_estimate_usd` debe ser un número no negativo.")
        _dict(report, run, "rules_snapshot", where)
        _dict(report, run, "metadata", where)

        if isinstance(run.get("nodes_failed"), int) and run["nodes_failed"] > 0:
            report.warn(f"{where}: la corrida dejó {run['nodes_failed']} nodo(s) sin pregunta.")

    # (5, 7, 8, 9, 10) preguntas
    seen_questions: set[tuple[str, Any]] = set()
    by_status: dict[str, int] = {}
    for i, question in enumerate(questions):
        where = f"questions[{i}]"
        if not isinstance(question, dict):
            report.error(f"{where}: debe ser un objeto.")
            continue

        q_run = _text(report, question, "run_ref", where)
        q_node = _text(report, question, "node_ref", where)
        if q_run is not None and q_run not in run_refs:
            report.error(f"{where}: `run_ref` {q_run!r} no está en `runs`.")
        if q_node is not None and q_node not in node_refs:
            report.error(f"{where}: `node_ref` {q_node!r} no está en `nodes`.")
        q_order = _int(report, question, "generation_order", where, minimum=0)
        # Identidad de la pregunta: (corrida, nodo) en v1; (corrida, orden) desde v2,
        # que admite varias preguntas por nodo.
        if version == 1 and q_run is not None and q_node is not None:
            key: tuple[str, Any] = (q_run, q_node)
            if key in seen_questions:
                report.error(
                    f"{where}: ya hay otra pregunta para la corrida {q_run} y el nodo "
                    f"{q_node}. Ese par es la identidad de la pregunta y el índice "
                    f"único de Postgres lo rechazaría."
                )
            seen_questions.add(key)
        elif version >= 2 and q_run is not None and q_order is not None:
            key = (q_run, q_order)
            if key in seen_questions:
                report.error(
                    f"{where}: ya hay otra pregunta con `generation_order` {q_order} en la "
                    f"corrida {q_run}. Ese par es la identidad de la pregunta (v2) y el "
                    f"índice único de Postgres lo rechazaría."
                )
            seen_questions.add(key)

        _text(report, question, "question_text", where, limit_key="question_text")
        _text(report, question, "justification", where, limit_key="justification")
        if version >= 2:
            q_type = question.get("question_type")
            if q_type not in QUESTION_TYPES:
                report.error(
                    f"{where}: `question_type` = {q_type!r}; debe ser uno de {sorted(QUESTION_TYPES)}."
                )
            _text(report, question, "source_quote", where, limit_key="source_quote")
        _stamp(report, question, "created_at", where)
        _stamp(report, question, "validated_at", where, required=False)
        _dict(report, question, "metadata", where)

        status = question.get("validation_status")
        if status not in VALIDATION_STATUSES:
            report.error(
                f"{where}: `validation_status` = {status!r}; debe ser uno de "
                f"{sorted(VALIDATION_STATUSES)}."
            )
        else:
            by_status[status] = by_status.get(status, 0) + 1

        options = question.get("options")
        if not isinstance(options, list):
            report.error(f"{where}: `options` debe ser una lista.")
            continue
        if len(options) != OPTIONS_PER_QUESTION:
            report.error(f"{where}: tiene {len(options)} opciones, deben ser {OPTIONS_PER_QUESTION}.")

        roles: dict[str, int] = {}
        orders: list[Any] = []
        texts: list[str] = []
        correct_refs: list[str] = []
        for j, option in enumerate(options):
            owhere = f"{where}.options[{j}]"
            if not isinstance(option, dict):
                report.error(f"{owhere}: debe ser un objeto.")
                continue
            role = option.get("role")
            if role not in ROLE_COUNTS:
                report.error(f"{owhere}: `role` = {role!r}; debe ser uno de {sorted(ROLE_COUNTS)}.")
            else:
                roles[role] = roles.get(role, 0) + 1
            _int(report, option, "order_in_question", owhere, minimum=0)
            orders.append(option.get("order_in_question"))
            text = _text(report, option, "text", owhere, limit_key="option_text")
            if text is not None:
                texts.append(" ".join(text.split()).lower())
            _dict(report, option, "metadata", owhere)
            if not isinstance(option.get("is_correct"), bool):
                report.error(f"{owhere}: `is_correct` debe ser booleano.")
            elif option["is_correct"]:
                correct_refs.append(f"{owhere} (rol {role!r})")

        for role, expected in ROLE_COUNTS.items():
            actual = roles.get(role, 0)
            if actual != expected:
                report.error(f"{where}: {actual} opción(es) con rol {role!r}, deben ser {expected}.")

        if len(correct_refs) != 1:
            report.error(
                f"{where}: {len(correct_refs)} opciones marcadas `is_correct`, debe haber "
                f"exactamente 1. {'; '.join(correct_refs)}"
            )
        elif "rol 'correct'" not in correct_refs[0]:
            report.error(
                f"{where}: la opción marcada `is_correct` no es la de rol `correct` "
                f"— {correct_refs[0]}."
            )

        if len(set(texts)) != len(texts):
            report.error(f"{where}: hay opciones con el mismo texto.")

        clean_orders = [o for o in orders if isinstance(o, int) and not isinstance(o, bool)]
        if len(set(clean_orders)) != len(clean_orders):
            report.error(f"{where}: `order_in_question` repetido entre sus opciones.")

    # Secretos: se comprueba al final, sobre el bundle entero.
    for hit in find_secrets(bundle):
        report.error(f"Posible secreto en {hit}. Un bundle no debe llevar credenciales.")

    served = sum(by_status.get(s, 0) for s in SERVED_STATUSES)
    if not questions:
        report.warn("El bundle no trae preguntas: el examen se creará vacío y sin publicar.")
    elif served == 0:
        report.warn(
            "Ninguna pregunta está en `pending` ni `valid`: se importarán todas, "
            "pero no se le servirá ninguna a los alumnos."
        )
    for status in ("needs_review", "rejected"):
        if by_status.get(status):
            report.warn(f"{by_status[status]} pregunta(s) en `{status}`: no se sirven a los alumnos.")

    covered = {q.get("node_ref") for q in questions if isinstance(q, dict)}
    with_text = {
        n["ref"] for n in nodes
        if isinstance(n, dict) and isinstance(n.get("ref"), str) and n.get("chunks")
    }
    uncovered = len(with_text - covered)
    if uncovered:
        report.warn(f"{uncovered} nodo(s) con texto se quedaron sin pregunta.")

    report.counts = {
        "nodes": len(nodes),
        "chunks": n_chunks,
        "runs": len(runs),
        "questions": len(questions),
        "questions_served": served,
        **{f"status_{k}": v for k, v in sorted(by_status.items())},
    }
    return report
