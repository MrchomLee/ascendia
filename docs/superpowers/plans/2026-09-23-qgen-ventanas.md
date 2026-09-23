# Generación de preguntas por ventanas (qgen v2) — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que `qgen-generate` genere todas las preguntas posibles recorriendo el texto por ventanas de ~4 000 caracteres, con una sola llamada por ventana, prompts por familia (militar/civil), teoría literal y ejercicios basados en el PDF verificados, y exporte con un contrato v2 que admite varias preguntas por nodo.

**Architecture:** Un módulo puro parte los chunks de cada nodo en ventanas (`qgen/windows.py`). Por cada ventana pendiente, una llamada a Gemini devuelve la lista completa de preguntas tipadas; cada pregunta se valida por separado (`qgen/validation/checks.py`), los ejercicios nuevos se verifican con una segunda llamada, se descartan duplicadas y se guardan con su tipo, cita y ventana. La reanudación se basa en el estado de cada ventana guardado en la corrida y en `Question.window_key`.

**Tech Stack:** Python 3.14 (uv workspace), SQLAlchemy 2 sobre SQLite, pydantic v2, google-genai, typer + rich, Streamlit, pytest.

**Spec:** `docs/superpowers/specs/2026-09-23-qgen-ventanas-design.md` (léela antes de empezar).

## Global Constraints

- Windows + Git Bash. Tests desde la raíz del repo: `.venv/Scripts/python.exe -m pytest <ruta> -q`. Nunca `py -3.14 -m uv`.
- Rama `feat/qgen-ventanas`. Un commit por tarea; cada mensaje termina con la línea `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **No tocar `etl/src/`** (ni el ETL ni los árboles de nodos).
- Docstrings, comentarios y textos para el usuario en español, como el código de alrededor.
- Ventanas: `OBJETIVO = 4000`, `MINIMO_CORTE = 3000`, `MAXIMO = 6000` caracteres.
- Máximo 30 preguntas por ventana; similitud de duplicado 0.90 (solo teoría; ejercicios solo si son idénticos).
- Temperatura 0.3 en la llamada por ventana y 0 en la verificación. Modelo por defecto `MODEL_FLASH` (`gemini-3.6-flash`).
- Límites: `pregunta` ≤ 1000, `texto` de opción ≤ 500, `cita` ≤ 2000, `justificacion` ≤ 2000 caracteres.
- Opciones: siempre 1 `correct`, 1 `confusa`, 2 `distractor`.
- Familias: `militar` = manual, codigo_legal, ley_organica (tipos: teoria). `civil` = historia_universal, geografia_moderna_mexico (teoria); algebra_baldor, calculo_una_variable, algebra_trigonometria_geometria_analitica, taller_lectura_redaccion (teoria, ejercicio).
- Los tests nunca llaman a Gemini de verdad: siempre un Gemini falso.
- Al terminar (Task 12): `PYTHONHASHSEED=0 graphify update .` (ver `CLAUDE.md`).

## Review Focus

1. **Una corrida que muere sin cerrarse** (proceso matado): la siguiente no debe repetir ventanas que ya tienen preguntas guardadas → `_done_window_keys` también lee `Question.window_key` (test en Task 8).
2. **Respuestas de Gemini con forma inesperada** (`preguntas` ausente o que no es lista, más de 30 preguntas, una pregunta mal formada): se reintenta la ventana o se descarta solo lo malo (tests en Tasks 4 y 6).
3. **Chunks vacíos o solo espacios, y un chunk más grande que `MAXIMO`**: ninguna ventana vacía; el chunk gigante forma su propia ventana (tests en Task 2).
4. **Notación distinta entre el PDF y la respuesta** (x² / x^2 / x2, 𝑥, − frente a -, ′ frente a ', comillas tipográficas): no debe mandar una pregunta a revisión (tests en Task 4).
5. **`--regenerate --limit N`**: solo se borran las preguntas de las ventanas que se van a rehacer, no las del resto del nodo (tests en Tasks 7 y 8).

---

### Task 1: Familia y tipos en las reglas

**Files:**
- Modify: `question_generator/src/qgen/rules/base.py`
- Modify: `question_generator/src/qgen/rules/defaults.py`
- Test: `question_generator/tests/test_rules.py`

**Interfaces:**
- Produces: `DocumentRules.familia: str` (`"militar"` | `"civil"`, por defecto `"militar"`), `DocumentRules.tipos: tuple[str, ...]` (subconjunto de `("teoria", "ejercicio")`, por defecto `("teoria",)`), constantes `FAMILIAS` y `TIPOS` en `qgen.rules.base`. `to_dict`/`from_dict` las incluyen; `merge_rules` las conserva del perfil.

- [ ] **Step 1: Write the failing tests** — añade al final de `question_generator/tests/test_rules.py` (y `import pytest` arriba si no está):

```python
from qgen.rules.base import DocumentRules, RulesOverride, merge_rules, rules_from_dict, rules_to_dict


@pytest.mark.parametrize("perfil, familia, tipos", [
    ("manual", "militar", ("teoria",)),
    ("codigo_legal", "militar", ("teoria",)),
    ("ley_organica", "militar", ("teoria",)),
    ("historia_universal", "civil", ("teoria",)),
    ("geografia_moderna_mexico", "civil", ("teoria",)),
    ("algebra_baldor", "civil", ("teoria", "ejercicio")),
    ("calculo_una_variable", "civil", ("teoria", "ejercicio")),
    ("algebra_trigonometria_geometria_analitica", "civil", ("teoria", "ejercicio")),
    ("taller_lectura_redaccion", "civil", ("teoria", "ejercicio")),
])
def test_cada_perfil_tiene_su_familia_y_sus_tipos(perfil, familia, tipos):
    rules = get_default_rules(perfil)
    assert (rules.familia, rules.tipos) == (familia, tipos)


def test_familia_y_tipos_viajan_en_la_foto_de_la_corrida():
    rules = get_default_rules("calculo_una_variable")
    assert rules_from_dict(rules_to_dict(rules)) == rules


def test_una_foto_antigua_sin_familia_se_lee_como_militar_de_teoria():
    rules = rules_from_dict({"name": "manual"})
    assert (rules.familia, rules.tipos) == ("militar", ("teoria",))


def test_el_override_no_cambia_familia_ni_tipos():
    merged = merge_rules(get_default_rules("calculo_una_variable"), RulesOverride(style_guide="otro"))
    assert (merged.familia, merged.tipos) == ("civil", ("teoria", "ejercicio"))


def test_familia_o_tipo_desconocido_se_rechaza():
    with pytest.raises(ValueError):
        DocumentRules(name="x", familia="naval")
    with pytest.raises(ValueError):
        DocumentRules(name="x", tipos=("examen",))
    with pytest.raises(ValueError):
        DocumentRules(name="x", tipos=())
```

- [ ] **Step 2: Run to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_rules.py -q`
Expected: FAIL (`AttributeError: 'DocumentRules' object has no attribute 'familia'` y `TypeError` por argumento inesperado).

- [ ] **Step 3: Implement** — en `rules/base.py`, justo después de `from typing import Any`, añade:

```python
#: Familias de generación (spec §5): cambian el rol y el formato del prompt.
FAMILIAS = ("militar", "civil")
#: Tipos que un perfil puede permitir; "ejercicio" habilita ejercicio_libro y ejercicio_nuevo.
TIPOS = ("teoria", "ejercicio")
```

Sustituye la clase `DocumentRules` entera por:

```python
@dataclass(frozen=True)
class DocumentRules:
    """Knobs that shape question generation for a class of documents."""

    name: str
    forbidden_topics: tuple[str, ...] = field(default_factory=tuple)
    preferred_topics: tuple[str, ...] = field(default_factory=tuple)
    style_guide: str = ""
    extra_instructions: str = ""
    familia: str = "militar"
    tipos: tuple[str, ...] = ("teoria",)

    def __post_init__(self) -> None:
        if self.familia not in FAMILIAS:
            raise ValueError(f"familia {self.familia!r} desconocida; debe ser una de {FAMILIAS}")
        if not self.tipos or any(t not in TIPOS for t in self.tipos):
            raise ValueError(f"tipos {self.tipos!r} inválidos; cada uno debe ser uno de {TIPOS}")

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "DocumentRules":
        return cls(
            name=d["name"],
            forbidden_topics=tuple(d.get("forbidden_topics") or ()),
            preferred_topics=tuple(d.get("preferred_topics") or ()),
            style_guide=d.get("style_guide", "") or "",
            extra_instructions=d.get("extra_instructions", "") or "",
            familia=d.get("familia") or "militar",
            tipos=tuple(d.get("tipos") or ("teoria",)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "forbidden_topics": list(self.forbidden_topics),
            "preferred_topics": list(self.preferred_topics),
            "style_guide": self.style_guide,
            "extra_instructions": self.extra_instructions,
            "familia": self.familia,
            "tipos": list(self.tipos),
        }
```

En `merge_rules`, en el `return DocumentRules(...)`, añade al final de los argumentos:

```python
        familia=default.familia,
        tipos=default.tipos,
```

En `rules/defaults.py` añade estas dos líneas justo después de `name="…",` en cada una de estas constantes (las militares se quedan con el valor por defecto):

- `_BALDOR_RULES`, `_TALLER_LECTURA_REDACCION_RULES`, `_CALCULO_UNA_VARIABLE_RULES`, `_ALGEBRA_TRIGONOMETRIA_GEOMETRIA_ANALITICA_RULES`:

```python
    familia="civil",
    tipos=("teoria", "ejercicio"),
```

- `_HISTORIA_UNIVERSAL_RULES`, `_GEOGRAFIA_MODERNA_MEXICO_RULES`:

```python
    familia="civil",
    tipos=("teoria",),
```

- [ ] **Step 4: Run to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests -q`
Expected: todo en verde.

- [ ] **Step 5: Commit**

```bash
git add question_generator/src/qgen/rules question_generator/tests/test_rules.py
git commit -m "feat(qgen): familia y tipos de pregunta en las reglas de cada perfil

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Ventanas

**Files:**
- Create: `question_generator/src/qgen/windows.py`
- Test: `question_generator/tests/test_windows.py`

**Interfaces:**
- Produces: `Window(node_id: int, ordinal_desde: int, ordinal_hasta: int, text: str, page_start: int, page_end: int)` (dataclass congelada) con la propiedad `key -> str` (`"<node_id>:<desde>-<hasta>"`); `build_windows(node_id: int, chunks: Sequence[ChunkLike]) -> list[Window]`; `strip_overlap(prev: str, text: str) -> str`; constantes `OBJETIVO`, `MINIMO_CORTE`, `MAXIMO`. `ChunkLike` es cualquier objeto con `ordinal`, `text`, `page_start`, `page_end` (el `Chunk` del ORM sirve).

- [ ] **Step 1: Write the failing tests** — crea `question_generator/tests/test_windows.py`:

```python
"""Ventanas de texto (spec §4): grupos de chunks consecutivos de un nodo."""

from dataclasses import dataclass

from qgen.windows import MAXIMO, Window, build_windows, strip_overlap


@dataclass
class C:
    ordinal: int
    text: str
    page_start: int = 1
    page_end: int = 1


def _keys(windows: list[Window]) -> list[str]:
    return [w.key for w in windows]


def test_un_nodo_pequeno_es_una_sola_ventana():
    windows = build_windows(7, [C(0, "Primero.", 3, 3), C(1, "Segundo.", 4, 5)])

    assert _keys(windows) == ["7:0-1"]
    assert windows[0].text == "Primero.\n\nSegundo."
    assert (windows[0].page_start, windows[0].page_end) == (3, 5)


def test_la_ventana_se_cierra_al_llegar_al_objetivo():
    # Contenido distinto por chunk: textos idénticos parecerían solapamiento.
    chunks = [C(i, str(i) * 1500) for i in range(6)]

    assert _keys(build_windows(1, chunks)) == ["1:0-2", "1:3-5"]


def test_nunca_pasa_del_maximo():
    windows = build_windows(1, [C(0, "a" * 3900), C(1, "b" * 2500)])

    assert _keys(windows) == ["1:0-0", "1:1-1"]
    assert all(len(w.text) <= MAXIMO for w in windows)


def test_corta_antes_de_un_ejemplo_pasados_3000_caracteres():
    chunks = [
        C(0, "a" * 1600),
        C(1, "b" * 1600),
        C(2, "EJEMPLO 3 Graficación de puntos\nSolución …"),
        C(3, "c" * 100),
    ]

    assert _keys(build_windows(1, chunks)) == ["1:0-1", "1:2-3"]


def test_no_corta_antes_de_un_ejemplo_si_la_ventana_es_corta():
    chunks = [C(0, "a" * 1000), C(1, "EJEMPLO 1 Distancia entre dos puntos\n…")]

    assert _keys(build_windows(1, chunks)) == ["1:0-1"]


def test_corta_antes_de_una_seccion_numerada():
    chunks = [C(0, "a" * 3100), C(1, "4.3 Ecuaciones de rectas\nUna recta …")]

    assert _keys(build_windows(1, chunks)) == ["1:0-0", "1:1-1"]


def test_un_chunk_mas_grande_que_el_maximo_forma_su_propia_ventana():
    chunks = [C(0, "a" * 500), C(1, "b" * 7000), C(2, "c" * 500)]

    assert _keys(build_windows(1, chunks)) == ["1:0-0", "1:1-1", "1:2-2"]


def test_se_quita_el_solapamiento_que_repite_el_chunker():
    primero = "Párrafo uno, bastante largo. " * 10
    segundo = primero[-120:] + "\n\nPárrafo dos."

    [window] = build_windows(1, [C(0, primero), C(1, segundo)])

    assert window.text == primero.strip() + "\n\nPárrafo dos."


def test_el_encabezado_se_busca_despues_del_solapamiento():
    primero = "a" * 3100
    segundo = primero[-120:] + "\n\nEJEMPLO 2 Tres puntos forman un triángulo"

    assert _keys(build_windows(1, [C(0, primero), C(1, segundo)])) == ["1:0-0", "1:1-1"]


def test_strip_overlap_no_toca_textos_sin_solapamiento():
    assert strip_overlap("fin del anterior.", "Otro texto.") == "Otro texto."
    # Coincidencias cortas (un punto, una palabra) no son solapamiento.
    assert strip_overlap("termina en punto.", ".empieza en punto") == ".empieza en punto"


def test_el_orden_es_por_ordinal_y_siempre_igual():
    chunks = [C(2, "tres"), C(0, "uno"), C(1, "dos")]

    assert build_windows(1, chunks) == build_windows(1, sorted(chunks, key=lambda c: c.ordinal))
    assert build_windows(1, chunks)[0].text == "uno\n\ndos\n\ntres"


def test_chunks_vacios_no_generan_ventanas():
    assert build_windows(1, [C(0, "   "), C(1, "")]) == []
    assert _keys(build_windows(1, [C(0, "  "), C(1, "Texto")])) == ["1:1-1"]
```

- [ ] **Step 2: Run to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_windows.py -q`
Expected: FAIL con `ModuleNotFoundError: No module named 'qgen.windows'`.

- [ ] **Step 3: Implement** — crea `question_generator/src/qgen/windows.py`:

```python
"""Ventanas de texto para generar preguntas (spec §4).

Una ventana es un grupo de chunks consecutivos de un mismo nodo, de unos
4 000 caracteres. Todas las preguntas de una ventana salen de una sola llamada,
así que el tamaño decide cuánto texto ve el modelo a la vez.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol, Sequence

OBJETIVO = 4000
MINIMO_CORTE = 3000
MAXIMO = 6000

# El chunker repite al inicio de cada chunk los últimos ~120 caracteres del anterior.
_SOLAPE_MAX = 200
_SOLAPE_MIN = 20

# Un chunk que empieza así abre un bloque nuevo: mejor no partirlo entre ventanas.
_ENCABEZADO_RE = re.compile(r"^(EJEMPLO\s+\d+|\d+\.\d+\.?\s+[A-ZÁÉÍÓÚÑ¿]|Definición|DEFINICIÓN|Teorema)")


class ChunkLike(Protocol):
    ordinal: int
    text: str
    page_start: int
    page_end: int


@dataclass(frozen=True)
class Window:
    node_id: int
    ordinal_desde: int
    ordinal_hasta: int
    text: str
    page_start: int
    page_end: int

    @property
    def key(self) -> str:
        """Identidad estable de la ventana: `<node_id>:<ordinal_desde>-<ordinal_hasta>`."""
        return f"{self.node_id}:{self.ordinal_desde}-{self.ordinal_hasta}"


def strip_overlap(prev: str, text: str) -> str:
    """Quita del inicio de `text` lo que repite del final de `prev` (y el salto que lo sigue)."""
    for n in range(min(_SOLAPE_MAX, len(prev), len(text)), _SOLAPE_MIN - 1, -1):
        if text.startswith(prev[-n:]):
            return text[n:].lstrip()
    return text


def build_windows(node_id: int, chunks: Sequence[ChunkLike]) -> list[Window]:
    """Agrupa los chunks de un nodo en ventanas. Puro y determinista."""
    piezas: list[tuple[ChunkLike, str]] = []
    anterior: ChunkLike | None = None
    for chunk in sorted(chunks, key=lambda c: c.ordinal):
        texto = chunk.text if anterior is None else strip_overlap(anterior.text, chunk.text)
        anterior = chunk
        if texto.strip():
            piezas.append((chunk, texto.strip()))

    ventanas: list[Window] = []
    actual: list[tuple[ChunkLike, str]] = []
    for chunk, texto in piezas:
        if actual:
            tamano = len(_unir(actual))
            if (
                tamano >= OBJETIVO
                or tamano + 2 + len(texto) > MAXIMO
                or (tamano >= MINIMO_CORTE and _ENCABEZADO_RE.match(texto))
            ):
                ventanas.append(_ventana(node_id, actual))
                actual = []
        actual.append((chunk, texto))
    if actual:
        ventanas.append(_ventana(node_id, actual))
    return ventanas


def _unir(piezas: list[tuple[ChunkLike, str]]) -> str:
    return "\n\n".join(texto for _, texto in piezas)


def _ventana(node_id: int, piezas: list[tuple[ChunkLike, str]]) -> Window:
    return Window(
        node_id=node_id,
        ordinal_desde=piezas[0][0].ordinal,
        ordinal_hasta=piezas[-1][0].ordinal,
        text=_unir(piezas),
        page_start=min(c.page_start for c, _ in piezas),
        page_end=max(c.page_end for c, _ in piezas),
    )
```

- [ ] **Step 4: Run to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_windows.py -q`
Expected: 12 passed.

- [ ] **Step 5: Commit**

```bash
git add question_generator/src/qgen/windows.py question_generator/tests/test_windows.py
git commit -m "feat(qgen): ventanas de texto a partir de los chunks de un nodo

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Esquemas de salida de la llamada por ventana

**Files:**
- Modify: `question_generator/src/qgen/prompts/schemas.py`
- Test: `question_generator/tests/test_schemas.py`

**Interfaces:**
- Produces (en `qgen.prompts.schemas`): `QuestionType` (StrEnum `teoria`, `ejercicio_libro`, `ejercicio_nuevo`); `WindowOption(rol: OptionRole, texto: str)`; `WindowQuestion(tipo, pregunta, opciones: list[WindowOption], cita, justificacion)`; `WindowResponse(preguntas: list[WindowQuestion])`; `VerificationResult(razonamiento: str, opcion: Literal["A","B","C","D","ninguna","varias"], dificultad: Literal["menor","igual","mayor"])`; constantes `MAX_PREGUNTAS_POR_VENTANA = 30` y `LETRAS = ("A", "B", "C", "D")`.

- [ ] **Step 1: Write the failing tests** — añade al final de `question_generator/tests/test_schemas.py`:

```python
from qgen.prompts.schemas import (
    MAX_PREGUNTAS_POR_VENTANA,
    QuestionType,
    VerificationResult,
    WindowQuestion,
    WindowResponse,
)


def _window_item(**cambios) -> dict:
    item = {
        "tipo": "teoria",
        "pregunta": "¿Qué es la guerra?",
        "opciones": [
            {"rol": "correct", "texto": "un conflicto entre sociedades"},
            {"rol": "confusa", "texto": "un conflicto entre individuos"},
            {"rol": "distractor", "texto": "una doctrina militar"},
            {"rol": "distractor", "texto": "un tratado internacional"},
        ],
        "cita": "La guerra es un conflicto entre sociedades.",
        "justificacion": "Lo dice el texto.",
    }
    item.update(cambios)
    return item


def test_una_pregunta_de_ventana_valida():
    q = WindowQuestion.model_validate(_window_item(tipo="ejercicio_nuevo"))
    assert q.tipo == QuestionType.EJERCICIO_NUEVO


def test_ventana_rechaza_reparto_de_roles_incorrecto():
    item = _window_item()
    item["opciones"][1]["rol"] = "correct"
    with pytest.raises(ValidationError):
        WindowQuestion.model_validate(item)


def test_ventana_rechaza_cita_vacia():
    with pytest.raises(ValidationError):
        WindowQuestion.model_validate(_window_item(cita="   "))


def test_ventana_rechaza_opciones_repetidas():
    item = _window_item()
    item["opciones"][3]["texto"] = "Una  doctrina militar"
    with pytest.raises(ValidationError):
        WindowQuestion.model_validate(item)


def test_ventana_rechaza_tipo_desconocido():
    with pytest.raises(ValidationError):
        WindowQuestion.model_validate(_window_item(tipo="examen"))


def test_la_respuesta_de_ventana_es_una_lista_de_preguntas():
    assert len(WindowResponse.model_validate({"preguntas": [_window_item()]}).preguntas) == 1
    assert MAX_PREGUNTAS_POR_VENTANA == 30


def test_verificacion_solo_admite_letras_ninguna_o_varias():
    assert VerificationResult(razonamiento="…", opcion="B", dificultad="igual").opcion == "B"
    with pytest.raises(ValidationError):
        VerificationResult(razonamiento="…", opcion="E", dificultad="igual")
    with pytest.raises(ValidationError):
        VerificationResult(razonamiento="…", opcion="A", dificultad="altísima")
```

- [ ] **Step 2: Run to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_schemas.py -q`
Expected: FAIL con `ImportError: cannot import name 'MAX_PREGUNTAS_POR_VENTANA'`.

- [ ] **Step 3: Implement** — en `prompts/schemas.py`, cambia `from enum import StrEnum` por:

```python
from enum import StrEnum
from typing import Literal
```

y añade al final del fichero:

```python
# ─── Llamada por ventana (spec §6) ─────────────────────────────────────────

MAX_PREGUNTAS_POR_VENTANA = 30
LETRAS = ("A", "B", "C", "D")


class QuestionType(StrEnum):
    TEORIA = "teoria"
    EJERCICIO_LIBRO = "ejercicio_libro"
    EJERCICIO_NUEVO = "ejercicio_nuevo"


class WindowOption(BaseModel):
    rol: OptionRole
    texto: str = Field(min_length=1, max_length=500)


class WindowQuestion(BaseModel):
    """Una pregunta completa tal como la devuelve la llamada por ventana."""

    tipo: QuestionType
    pregunta: str = Field(min_length=1, max_length=1000)
    opciones: list[WindowOption] = Field(min_length=4, max_length=4)
    cita: str = Field(min_length=1, max_length=2000)
    justificacion: str = Field(min_length=1, max_length=2000)

    @model_validator(mode="after")
    def _check(self) -> "WindowQuestion":
        counts = Counter(o.rol.value for o in self.opciones)
        for role, expected in REQUIRED_ROLE_COUNTS.items():
            if counts.get(role, 0) != expected:
                raise ValueError(f"reparto de roles inválido: {dict(counts)}")
        textos = [" ".join(o.texto.split()).lower() for o in self.opciones]
        if len(set(textos)) != len(textos):
            raise ValueError("opciones con el mismo texto")
        if not self.cita.strip():
            raise ValueError("cita vacía")
        return self


class WindowResponse(BaseModel):
    preguntas: list[WindowQuestion]


class VerificationResult(BaseModel):
    """Lo que devuelve la verificación de un ejercicio nuevo (spec §7)."""

    razonamiento: str = Field(min_length=1, max_length=3000)
    opcion: Literal["A", "B", "C", "D", "ninguna", "varias"]
    dificultad: Literal["menor", "igual", "mayor"]
```

- [ ] **Step 4: Run to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_schemas.py -q`
Expected: todo en verde.

- [ ] **Step 5: Commit**

```bash
git add question_generator/src/qgen/prompts/schemas.py question_generator/tests/test_schemas.py
git commit -m "feat(qgen): esquemas de la respuesta por ventana y de la verificación

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Revisiones de cada pregunta

**Files:**
- Create: `question_generator/src/qgen/validation/checks.py`
- Modify: `question_generator/src/qgen/validation/__init__.py`
- Test: `question_generator/tests/test_checks.py`

**Interfaces:**
- Consumes: `WindowQuestion`, `WindowOption`, `QuestionType`, `VerificationResult`, `GeneratedQuestion`, `GeneratedOption`, `OptionRole`, `MAX_PREGUNTAS_POR_VENTANA`, `LETRAS` (Task 3).
- Produces (en `qgen.validation.checks`): `norm_text(str) -> str`; `norm_math(str) -> str`; `Verdict(status: str, motivos: tuple[str, ...])` con `Verdict.from_motivos(iterable) -> Verdict` y `verdict.with_motivos(iterable) -> Verdict`; `parse_items(items: list) -> tuple[list[WindowQuestion], list[str]]`; `tipo_permitido(q, tipos) -> bool`; `review(q, window_text) -> Verdict`; `to_generated(q) -> GeneratedQuestion` (opciones barajadas, reproducible); `verification_options(q) -> tuple[list[str], str]` (textos en otro orden y letra de la clave); `verification_motivos(result: VerificationResult | None, letra_correcta: str) -> list[str]`; `DuplicateIndex` con `add(node_id, pregunta, tipo)` e `is_duplicate(node_id, pregunta, tipo) -> bool`.

- [ ] **Step 1: Write the failing tests** — crea `question_generator/tests/test_checks.py`:

```python
"""Revisiones de cada pregunta de una ventana (spec §7)."""

from qgen.prompts.schemas import LETRAS, GeneratedQuestion, OptionRole, VerificationResult, WindowQuestion
from qgen.validation.checks import (
    DuplicateIndex,
    Verdict,
    norm_math,
    norm_text,
    parse_items,
    review,
    tipo_permitido,
    to_generated,
    verification_motivos,
    verification_options,
)

VENTANA = (
    "Para México, la guerra se conceptúa como “un conflicto entre sociedades o grupos "
    "de seres humanos”.\n\nEJEMPLO 1 Derivar f(x) = 𝑥² − 4.\nSolución: f′(x) = 2𝑥."
)


def _item(pregunta="¿Cómo se conceptúa la guerra?", *, tipo="teoria",
          correcta="un conflicto entre sociedades",
          cita='la guerra se conceptúa como "un conflicto entre sociedades') -> dict:
    return {
        "tipo": tipo,
        "pregunta": pregunta,
        "opciones": [
            {"rol": "correct", "texto": correcta},
            {"rol": "confusa", "texto": "confusa"},
            {"rol": "distractor", "texto": "distractor uno"},
            {"rol": "distractor", "texto": "distractor dos"},
        ],
        "cita": cita,
        "justificacion": "…",
    }


def _q(*args, **kwargs) -> WindowQuestion:
    return WindowQuestion.model_validate(_item(*args, **kwargs))


# ─── Normalización ─────────────────────────────────────────────────────────


def test_norm_text_ignora_espacios_mayusculas_y_comillas():
    assert norm_text("  “Hola”   Mundo – x ") == '"hola" mundo - x'


def test_norm_math_iguala_la_notacion_de_los_pdf_de_word():
    assert norm_math("x^2 − 4") == norm_math("x2 - 4") == norm_math("𝑥² − 4")
    assert norm_math("f′(x) = 2𝑥") == norm_math("f'(x)=2x")


# ─── Revisión por tipo ─────────────────────────────────────────────────────


def test_teoria_literal_pasa():
    assert review(_q(), VENTANA) == Verdict("pending", ())


def test_teoria_parafraseada_va_a_revision():
    assert review(_q(correcta="una lucha violenta entre pueblos"), VENTANA).motivos == ("respuesta parafraseada",)


def test_teoria_con_cita_inventada_va_a_revision():
    verdict = review(_q(cita="la guerra es la continuación de la política"), VENTANA)
    assert verdict == Verdict("needs_review", ("cita no encontrada",))


def test_ejercicio_del_libro_con_su_resultado_pasa():
    q = _q("Deriva f(x) = x^2 − 4.", tipo="ejercicio_libro", correcta="f'(x) = 2x",
           cita="Derivar f(x) = 𝑥² − 4.\nSolución: f′(x) = 2𝑥.")
    assert review(q, VENTANA).status == "pending"


def test_ejercicio_del_libro_sin_su_resultado_va_a_revision():
    q = _q("Deriva f(x) = x^2 − 4.", tipo="ejercicio_libro", correcta="f'(x) = x",
           cita="Derivar f(x) = 𝑥² − 4.\nSolución: f′(x) = 2𝑥.")
    assert review(q, VENTANA).motivos == ("el resultado no aparece en el ejemplo citado",)


def test_ejercicio_nuevo_sin_ejemplo_de_referencia_va_a_revision():
    q = _q("Deriva g(x) = x^3.", tipo="ejercicio_nuevo", correcta="3x^2", cita="Derivar g(x) = x³")
    assert review(q, VENTANA).motivos == ("sin ejemplo de referencia",)


def test_ejercicio_nuevo_con_su_ejemplo_pasa_la_revision_de_texto():
    q = _q("Deriva g(x) = x^3.", tipo="ejercicio_nuevo", correcta="3x^2",
           cita="Derivar f(x) = 𝑥² − 4.\nSolución: f′(x) = 2𝑥.")
    assert review(q, VENTANA).status == "pending"


# ─── Estructura ────────────────────────────────────────────────────────────


def test_parse_items_descarta_solo_lo_malo():
    preguntas, descartes = parse_items([_item(), {"tipo": "teoria"}])
    assert len(preguntas) == 1
    assert len(descartes) == 1 and descartes[0].startswith("pregunta 2: estructura inválida")


def test_parse_items_corta_en_30():
    preguntas, descartes = parse_items([_item(f"¿Pregunta {i}?") for i in range(31)])
    assert len(preguntas) == 30
    assert descartes == ["pregunta 31: pasa de las 30 preguntas por ventana"]


def test_tipo_permitido():
    teoria, ejercicio = _q(), _q("Deriva.", tipo="ejercicio_libro")
    assert tipo_permitido(teoria, ("teoria",))
    assert not tipo_permitido(ejercicio, ("teoria",))
    assert tipo_permitido(ejercicio, ("teoria", "ejercicio"))


# ─── Opciones barajadas ────────────────────────────────────────────────────


def test_to_generated_baraja_de_forma_reproducible():
    g = to_generated(_q())
    assert isinstance(g, GeneratedQuestion)
    assert [o.text for o in g.options] == [o.text for o in to_generated(_q()).options]
    assert sorted(o.role.value for o in g.options) == ["confusa", "correct", "distractor", "distractor"]


def test_la_correcta_no_queda_siempre_primera():
    posiciones = [
        next(i for i, o in enumerate(to_generated(_q(f"¿Pregunta {n}?")).options) if o.role == OptionRole.CORRECT)
        for n in range(8)
    ]
    assert any(p != 0 for p in posiciones)


def test_verification_options_devuelve_la_letra_de_la_clave():
    textos, letra = verification_options(_q())
    assert textos[LETRAS.index(letra)] == "un conflicto entre sociedades"
    assert sorted(textos) == sorted(["un conflicto entre sociedades", "confusa", "distractor uno", "distractor dos"])


# ─── Verificación ──────────────────────────────────────────────────────────


def _verif(opcion: str, dificultad: str = "igual") -> VerificationResult:
    return VerificationResult(razonamiento="…", opcion=opcion, dificultad=dificultad)


def test_verification_motivos():
    assert verification_motivos(None, "A") == ["verificación fallida"]
    assert verification_motivos(_verif("A"), "A") == []
    assert verification_motivos(_verif("B"), "A") == ["la verificación eligió B; la clave es A"]
    assert verification_motivos(_verif("ninguna"), "A") == ["la verificación respondió «ninguna»"]
    assert verification_motivos(_verif("A", "mayor"), "A") == ["supera la dificultad del PDF"]


def test_verdict_with_motivos_recalcula_el_estado():
    assert Verdict.from_motivos([]).with_motivos(["x"]) == Verdict("needs_review", ("x",))


# ─── Duplicadas ────────────────────────────────────────────────────────────


def test_duplicadas_de_teoria_por_similitud_dentro_del_mismo_nodo():
    index = DuplicateIndex()
    index.add(1, "¿Cómo se conceptúa la guerra para México?", "teoria")
    assert index.is_duplicate(1, "¿Cómo se conceptúa la guerra, para México?", "teoria")
    assert not index.is_duplicate(2, "¿Cómo se conceptúa la guerra, para México?", "teoria")


def test_ejercicios_solo_se_descartan_si_son_identicos():
    index = DuplicateIndex()
    index.add(1, "Deriva f(x) = 3x^2.", "ejercicio_nuevo")
    assert not index.is_duplicate(1, "Deriva f(x) = 5x^2.", "ejercicio_nuevo")
    assert index.is_duplicate(1, "Deriva  f(x) = 3x^2.", "ejercicio_nuevo")
```

- [ ] **Step 2: Run to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_checks.py -q`
Expected: FAIL con `ModuleNotFoundError: No module named 'qgen.validation.checks'`.

- [ ] **Step 3: Implement** — crea `question_generator/src/qgen/validation/checks.py`:

```python
"""Revisiones de cada pregunta generada por ventana (spec §7).

Todo es determinista y sin llamadas a Gemini: la verificación de los ejercicios
nuevos la hace el pipeline; aquí solo se traduce su resultado a motivos.
"""

from __future__ import annotations

import difflib
import hashlib
import random
import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable

from pydantic import ValidationError

from qgen.prompts.schemas import (
    LETRAS,
    MAX_PREGUNTAS_POR_VENTANA,
    GeneratedOption,
    GeneratedQuestion,
    OptionRole,
    QuestionType,
    VerificationResult,
    WindowOption,
    WindowQuestion,
)

SIMILITUD_DUPLICADO = 0.90

_SIGNOS = str.maketrans({
    "“": '"', "”": '"', "«": '"', "»": '"', "‘": "'", "’": "'", "′": "'",
    "–": "-", "—": "-", "−": "-",
})


def norm_text(text: str) -> str:
    """Para comparar texto literal: NFC, espacios colapsados, comillas y guiones unificados, sin mayúsculas."""
    text = unicodedata.normalize("NFC", text).translate(_SIGNOS)
    return " ".join(text.split()).casefold()


def norm_math(text: str) -> str:
    """Como `norm_text`, pero además iguala la notación: 𝑥² y x^2 quedan como x2 (así llegan los PDF de Word)."""
    text = unicodedata.normalize("NFKC", text).translate(_SIGNOS)
    return re.sub(r"[\s^·*]", "", text).casefold()


@dataclass(frozen=True)
class Verdict:
    status: str  # "pending" | "needs_review"
    motivos: tuple[str, ...] = ()

    @classmethod
    def from_motivos(cls, motivos: Iterable[str]) -> "Verdict":
        motivos = tuple(motivos)
        return cls("needs_review" if motivos else "pending", motivos)

    def with_motivos(self, extra: Iterable[str]) -> "Verdict":
        return Verdict.from_motivos(self.motivos + tuple(extra))


def parse_items(items: list) -> tuple[list[WindowQuestion], list[str]]:
    """Valida cada pregunta por separado: una mala no tumba a las demás."""
    preguntas: list[WindowQuestion] = []
    descartes: list[str] = []
    for i, item in enumerate(items, start=1):
        if i > MAX_PREGUNTAS_POR_VENTANA:
            descartes.append(f"pregunta {i}: pasa de las {MAX_PREGUNTAS_POR_VENTANA} preguntas por ventana")
            continue
        try:
            preguntas.append(WindowQuestion.model_validate(item))
        except ValidationError as exc:
            descartes.append(f"pregunta {i}: estructura inválida ({exc.errors()[0]['msg']})")
    return preguntas, descartes


def tipo_permitido(question: WindowQuestion, tipos: tuple[str, ...]) -> bool:
    return ("teoria" if question.tipo == QuestionType.TEORIA else "ejercicio") in tipos


def _correcta(question: WindowQuestion) -> str:
    return next(o.texto for o in question.opciones if o.rol == OptionRole.CORRECT)


def review(question: WindowQuestion, window_text: str) -> Verdict:
    """Revisión por tipo contra el texto de la ventana (spec §7, tabla de revisiones)."""
    correcta = _correcta(question)
    if question.tipo == QuestionType.TEORIA:
        ventana = norm_text(window_text)
        motivos = []
        if norm_text(question.cita) not in ventana:
            motivos.append("cita no encontrada")
        if norm_text(correcta) not in ventana:
            motivos.append("respuesta parafraseada")
        return Verdict.from_motivos(motivos)

    cita = norm_math(question.cita)
    if cita not in norm_math(window_text):
        falta = "cita no encontrada" if question.tipo == QuestionType.EJERCICIO_LIBRO else "sin ejemplo de referencia"
        return Verdict.from_motivos([falta])
    if question.tipo == QuestionType.EJERCICIO_LIBRO and norm_math(correcta) not in cita:
        return Verdict.from_motivos(["el resultado no aparece en el ejemplo citado"])
    return Verdict.from_motivos([])


def _barajadas(question: WindowQuestion, sal: str) -> list[WindowOption]:
    semilla = int(hashlib.sha256(f"{sal}:{question.pregunta}".encode("utf-8")).hexdigest()[:16], 16)
    opciones = list(question.opciones)
    random.Random(semilla).shuffle(opciones)
    return opciones


def to_generated(question: WindowQuestion) -> GeneratedQuestion:
    """La pregunta lista para guardar, con las opciones barajadas de forma reproducible."""
    return GeneratedQuestion(
        question=question.pregunta,
        options=[GeneratedOption(role=o.rol, text=o.texto) for o in _barajadas(question, "guardar")],
        justification=question.justificacion,
    )


def verification_options(question: WindowQuestion) -> tuple[list[str], str]:
    """Textos de las opciones para la verificación (en otro orden, sin roles) y la letra de la clave."""
    opciones = _barajadas(question, "verificar")
    letra = LETRAS[next(i for i, o in enumerate(opciones) if o.rol == OptionRole.CORRECT)]
    return [o.texto for o in opciones], letra


def verification_motivos(result: VerificationResult | None, letra_correcta: str) -> list[str]:
    if result is None:
        return ["verificación fallida"]
    motivos = []
    if result.opcion in ("ninguna", "varias"):
        motivos.append(f"la verificación respondió «{result.opcion}»")
    elif result.opcion != letra_correcta:
        motivos.append(f"la verificación eligió {result.opcion}; la clave es {letra_correcta}")
    if result.dificultad == "mayor":
        motivos.append("supera la dificultad del PDF")
    return motivos


class DuplicateIndex:
    """Enunciados ya aceptados, por nodo, para descartar duplicadas (spec §7)."""

    def __init__(self) -> None:
        self._por_nodo: dict[int, list[tuple[str, str]]] = {}

    def add(self, node_id: int, pregunta: str, tipo: str) -> None:
        self._por_nodo.setdefault(node_id, []).append((norm_text(pregunta), tipo))

    def is_duplicate(self, node_id: int, pregunta: str, tipo: str) -> bool:
        nueva = norm_text(pregunta)
        for otra, otro_tipo in self._por_nodo.get(node_id, ()):
            if nueva == otra:
                return True
            # Dos ejercicios del mismo tipo se parecen a propósito: solo cuenta si son idénticos.
            if tipo == otro_tipo == QuestionType.TEORIA.value:
                matcher = difflib.SequenceMatcher(None, nueva, otra)
                if (
                    matcher.real_quick_ratio() >= SIMILITUD_DUPLICADO
                    and matcher.quick_ratio() >= SIMILITUD_DUPLICADO
                    and matcher.ratio() >= SIMILITUD_DUPLICADO
                ):
                    return True
        return False
```

Sustituye el contenido de `question_generator/src/qgen/validation/__init__.py` por:

```python
"""Revisiones deterministas de las preguntas generadas; ver `checks`."""
```

- [ ] **Step 4: Run to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_checks.py -q`
Expected: todo en verde. Si `test_la_correcta_no_queda_siempre_primera` fallara (las 8 semillas dejan la correcta primera), sube el rango a 16 preguntas: es determinista, no intermitente.

- [ ] **Step 5: Commit**

```bash
git add question_generator/src/qgen/validation question_generator/tests/test_checks.py
git commit -m "feat(qgen): revisiones por tipo, duplicadas y opciones barajadas

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Instrucciones por familia

**Files:**
- Create: `question_generator/src/qgen/prompts/families.py`
- Test: `question_generator/tests/test_families.py`

**Interfaces:**
- Consumes: `DocumentRules` (Task 1), `Window` (Task 2), `MAX_PREGUNTAS_POR_VENTANA` y `LETRAS` (Task 3).
- Produces (en `qgen.prompts.families`): `SYSTEM_VERSION = "2026-09-23.v5"`; `build_window_instruction(rules, *, manual_title: str, exemplars: Sequence[dict] | None = None) -> str`; `build_window_message(window: Window, *, manual_title: str, breadcrumb: str) -> str`; `build_verification_instruction() -> str`; `build_verification_message(pregunta: str, opciones: Sequence[str], ejemplo: str) -> str` (líneas `"A) texto"`).

- [ ] **Step 1: Write the failing tests** — crea `question_generator/tests/test_families.py`:

```python
"""Instrucciones de la llamada por ventana, por familia (spec §6)."""

from qgen.prompts.families import (
    build_verification_message,
    build_window_instruction,
    build_window_message,
)
from qgen.rules.defaults import get_default_rules
from qgen.windows import Window


def test_la_instruccion_militar_usa_el_titulo_real_del_manual():
    instr = build_window_instruction(get_default_rules("manual"), manual_title="Manual de Operaciones Militares")
    assert "Conforme al Manual de Operaciones Militares" in instr
    assert "Conforme al manual," not in instr
    assert "Materias Militares" in instr


def test_sin_ejemplos_la_familia_militar_usa_los_de_siempre():
    instr = build_window_instruction(get_default_rules("codigo_legal"), manual_title="Código de Justicia Militar")
    assert "Para México, la guerra se conceptúa como" in instr


def test_la_familia_civil_no_lleva_nada_militar():
    instr = build_window_instruction(get_default_rules("historia_universal"), manual_title="Historia Universal")
    assert "Materias Militares" not in instr
    assert "Conforme al" not in instr
    assert "la guerra se conceptúa" not in instr
    assert "EJEMPLOS DE REFERENCIA" not in instr


def test_sin_ejercicios_en_el_perfil_se_prohiben():
    instr = build_window_instruction(get_default_rules("geografia_moderna_mexico"), manual_title="Geografía Moderna de México")
    assert "No generes ejercicios" in instr
    assert "ejercicio_nuevo" not in instr


def test_con_ejercicios_se_piden_el_del_libro_y_uno_nuevo_sin_subir_la_dificultad():
    instr = build_window_instruction(get_default_rules("calculo_una_variable"), manual_title="Cálculo, una variable")
    assert '"ejercicio_libro"' in instr and '"ejercicio_nuevo"' in instr
    assert "dificultad igual o menor" in instr
    assert "error más típico" in instr


def test_las_reglas_del_perfil_entran_en_la_instruccion():
    instr = build_window_instruction(get_default_rules("codigo_legal"), manual_title="CJM")
    assert "tipos de delitos y faltas militares" in instr
    assert "años de condena específicos" in instr


def test_los_ejemplos_de_referencia_sustituyen_a_los_de_siempre():
    ejemplos = [{"question_text": "¿Qué es un monomio?",
                 "options": [{"role": "correct", "text": "Una expresión de un solo término."}]}]
    instr = build_window_instruction(get_default_rules("manual"), manual_title="M", exemplars=ejemplos)
    assert "¿Qué es un monomio?" in instr
    assert "la guerra se conceptúa" not in instr


def test_el_mensaje_lleva_ruta_paginas_y_texto():
    window = Window(node_id=1, ordinal_desde=0, ordinal_hasta=2, text="Texto de la ventana.", page_start=3, page_end=5)
    msg = build_window_message(window, manual_title="Cálculo, una variable", breadcrumb="Capítulo 2 — Límites")
    assert "Capítulo 2 — Límites" in msg and "pp. 3-5" in msg and "Texto de la ventana." in msg


def test_la_verificacion_presenta_opciones_con_letras():
    msg = build_verification_message("Deriva x^3.", ["3x^2", "x^2", "3x", "x^3/3"], "EJEMPLO 1 Deriva x^2: 2x")
    assert "A) 3x^2" in msg and "D) x^3/3" in msg and "EJEMPLO 1 Deriva x^2: 2x" in msg
```

- [ ] **Step 2: Run to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_families.py -q`
Expected: FAIL con `ModuleNotFoundError: No module named 'qgen.prompts.families'`.

- [ ] **Step 3: Implement** — crea `question_generator/src/qgen/prompts/families.py`:

```python
"""Instrucciones de la llamada por ventana y de la verificación (spec §6 y §7).

Incrementar ``SYSTEM_VERSION`` invalida los caches existentes para que se
recreen con las nuevas instrucciones en la siguiente corrida.
"""

from __future__ import annotations

from typing import Any, Sequence

from qgen.prompts.schemas import LETRAS, MAX_PREGUNTAS_POR_VENTANA
from qgen.rules.base import DocumentRules
from qgen.windows import Window

SYSTEM_VERSION = "2026-09-23.v5"

_ROLES = {
    "militar": (
        "Actúa como un experto en Materias Militares y Evaluador de Adiestramiento que "
        "diseña exámenes de promoción."
    ),
    "civil": (
        "Actúa como evaluador del examen de admisión: diseñas preguntas de opción múltiple "
        "de nivel bachillerato."
    ),
}

_FORMATOS = {
    "militar": (
        'Cada enunciado empieza así: "Conforme al {manual}, <Ruta del mensaje>, ¿…?". '
        "Usa la Ruta tal como llega en el mensaje."
    ),
    "civil": "Enunciados directos, sin mencionar el libro ni la ubicación del texto.",
}

_TEORIA = (
    '- "teoria": una pregunta por CADA elemento evaluable del texto: definiciones, propiedades, '
    "reglas, clasificaciones, hechos, actores, años y ubicaciones. La opción \"correct\" es un "
    "fragmento LITERAL del texto (copia exacta, palabra por palabra; prohibido parafrasear)."
)

_EJERCICIOS = (
    '- "ejercicio_libro": por CADA ejemplo o ejercicio resuelto del texto (cualquier pasaje en que '
    "se aplica una regla o un procedimiento y se muestra el resultado), una pregunta con ese mismo "
    'ejemplo tal cual. La "correct" es el resultado que da el libro.\n'
    '- "ejercicio_nuevo": por cada ejemplo resuelto, además, un ejercicio NUEVO del mismo tipo y '
    "procedimiento, con datos distintos y dificultad igual o menor que la del libro (nunca mayor). "
    "Resuélvelo y comprueba el resultado antes de escribir las opciones."
)

_SIN_EJERCICIOS = '- No generes ejercicios: solo preguntas de tipo "teoria".'

_OPCIONES_EJERCICIOS = (
    '- En ejercicios: la "confusa" es el resultado del error más típico; los "distractor", otros '
    "errores típicos (signos, exponentes, orden de operaciones, fórmula equivocada). Las opciones "
    "pueden parecerse entre sí.\n"
)

_EJEMPLOS_MILITARES = """\
Ejemplo 1 (Concepto directo):
- Pregunta: "Para México, la guerra se conceptúa como:"
- correct: "un conflicto entre sociedades o grupos de seres humanos que luchan entre sí violentamente, para imponer los intereses de uno de ellos."
- confusa: "fenómeno social que ha acompañado a la especie humana en toda su historia"

Ejemplo 2 (Definición teórica):
- Pregunta: "¿Qué es la teoría de la guerra?"
- correct: "Es la exposición sistémica de los conflictos bélicos, integrando a ella sus aspectos como fenómeno social, connotación política, histórica y sus componentes físicos, ideológicos y materiales."
- distractor: "Es un conocimiento especulativo, ideal, independiente de toda aplicación; conjunto de teoremas de leyes organizadas sistemáticamente..."
"""

_PLANTILLA = """\
{rol}

TU TAREA
El mensaje trae el TEXTO de una ventana de "{manual}". Crea TODAS las preguntas de opción múltiple que ese texto permita: no hay cuota, una por cada elemento evaluable, hasta un máximo de {maximo}. No uses información de fuera del texto.

TIPOS DE PREGUNTA
{tipos}

OPCIONES (exactamente 4 por pregunta)
- 1 "correct", 1 "confusa" y 2 "distractor", de longitud parecida; la "correct" no debe ser la más larga.
- En "teoria": la "confusa" es un concepto parecido con un detalle crítico cambiado; los "distractor" son otros conceptos reales del texto.
{opciones_ejercicios}- Nunca pongas incisos (A, B, C, D) en el enunciado ni en las opciones.

CITA Y JUSTIFICACIÓN
- "cita": el fragmento LITERAL del texto en que se apoya la pregunta. En ejercicios, el ejemplo del libro (con su resultado) en que se basa.
- "justificacion": en "teoria", por qué la correcta lo es; en ejercicios, la resolución paso a paso.

ENUNCIADOS
{formato}

ESTILO Y RESTRICCIONES DE "{manual}"
- Estilo: {estilo}
- Temas preferentes: {preferentes}
- Temas a EVITAR (no generes preguntas sobre estos): {prohibidos}
- Instrucciones extra: {extra}
{ejemplos}
Salida: un único objeto JSON {{"preguntas": [...]}} conforme al schema, sin texto fuera del JSON.
"""

_VERIFICACION = """\
Eres un profesor que revisa un examen de opción múltiple.
1. Resuelve el EJERCICIO paso a paso, sin suponer que alguna opción es la correcta.
2. Elige la opción correcta ("A", "B", "C" o "D"); responde "ninguna" si ninguna lo es y "varias" si hay más de una.
3. Compara la dificultad del EJERCICIO con la del EJEMPLO DEL LIBRO: "menor", "igual" o "mayor".
Salida: un único objeto JSON conforme al schema, sin texto fuera del JSON."""


def build_window_instruction(
    rules: DocumentRules,
    *,
    manual_title: str,
    exemplars: Sequence[dict[str, Any]] | None = None,
) -> str:
    """Instrucción del sistema para la llamada por ventana: plantilla de la familia + reglas + ejemplos."""
    con_ejercicios = "ejercicio" in rules.tipos
    return _PLANTILLA.format(
        rol=_ROLES[rules.familia],
        manual=manual_title,
        maximo=MAX_PREGUNTAS_POR_VENTANA,
        tipos=_TEORIA + "\n" + (_EJERCICIOS if con_ejercicios else _SIN_EJERCICIOS),
        opciones_ejercicios=_OPCIONES_EJERCICIOS if con_ejercicios else "",
        formato=_FORMATOS[rules.familia].format(manual=manual_title),
        estilo=rules.style_guide or "(sin estilo específico)",
        preferentes=", ".join(rules.preferred_topics) or "(ninguno)",
        prohibidos=", ".join(rules.forbidden_topics) or "(ninguno)",
        extra=rules.extra_instructions or "(ninguna)",
        ejemplos=_ejemplos(rules.familia, exemplars),
    )


def _ejemplos(familia: str, exemplars: Sequence[dict[str, Any]] | None) -> str:
    """Ejemplos de referencia; si no hay, los militares de siempre solo en la familia militar."""
    if exemplars:
        bloques = []
        for i, ex in enumerate(exemplars, start=1):
            lineas = [f"Ejemplo {i}:", f'- Pregunta: "{ex.get("question_text") or ex.get("question", "")}"']
            lineas += [f'- {opt.get("role", "distractor")}: "{opt.get("text", "")}"' for opt in ex.get("options", [])]
            bloques.append("\n".join(lineas))
        cuerpo = "\n\n".join(bloques)
    elif familia == "militar":
        cuerpo = _EJEMPLOS_MILITARES
    else:
        return ""
    return f"\nEJEMPLOS DE REFERENCIA\n{cuerpo}\n"


def build_window_message(window: Window, *, manual_title: str, breadcrumb: str) -> str:
    """Mensaje de la llamada: el manual, la ruta del nodo, las páginas y el texto de la ventana."""
    paginas = (
        f"p. {window.page_start}"
        if window.page_end == window.page_start
        else f"pp. {window.page_start}-{window.page_end}"
    )
    return (
        f"Manual: {manual_title}\n"
        f"Ruta: {breadcrumb}\n"
        f"Ubicación: {paginas}\n\n"
        f'TEXTO:\n"""\n{window.text}\n"""\n\n'
        "Crea todas las preguntas que este texto permita, siguiendo las instrucciones."
    )


def build_verification_instruction() -> str:
    return _VERIFICACION


def build_verification_message(pregunta: str, opciones: Sequence[str], ejemplo: str) -> str:
    """Mensaje de la verificación: el ejemplo del libro, el ejercicio y sus opciones con letra."""
    lineas = [f"{letra}) {texto}" for letra, texto in zip(LETRAS, opciones)]
    return f'EJEMPLO DEL LIBRO:\n"""\n{ejemplo}\n"""\n\nEJERCICIO: {pregunta}\n' + "\n".join(lineas)
```

- [ ] **Step 4: Run to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_families.py -q`
Expected: 9 passed.

- [ ] **Step 5: Commit**

```bash
git add question_generator/src/qgen/prompts/families.py question_generator/tests/test_families.py
git commit -m "feat(qgen): instrucciones por familia para la llamada por ventana

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Llamadas a Gemini: ventana y verificación

**Files:**
- Modify: `question_generator/src/qgen/gemini/generate.py` (añadir; lo viejo se retira en Task 9)
- Test: `question_generator/tests/test_generate_window.py`

**Interfaces:**
- Consumes: `WindowResponse`, `VerificationResult` (Task 3).
- Produces (en `qgen.gemini.generate`): `WindowOutcome(items: list[dict], error: str | None = None, input_tokens: int = 0, output_tokens: int = 0, cached_tokens: int = 0, latency_s: float = 0.0)`; `generate_window(*, cache=None, model=None, message: str, system_instruction: str, client=None, attempts: int = 2) -> WindowOutcome` (los `items` son los dicts crudos de `preguntas`, sin validar; `error` solo si no hay items); `VerificationOutcome(result: VerificationResult | None, error: str | None = None, input_tokens=0, output_tokens=0, cached_tokens=0)`; `verify_exercise(*, model: str, message: str, system_instruction: str, client=None) -> VerificationOutcome`.

- [ ] **Step 1: Write the failing tests** — crea `question_generator/tests/test_generate_window.py`:

```python
"""Las dos llamadas a Gemini del flujo por ventanas, con un cliente falso."""

import json
from types import SimpleNamespace

from qgen.gemini.client import MODEL_FLASH
from qgen.gemini.generate import generate_window, verify_exercise
from qgen.prompts.schemas import VerificationResult


class _FakeClient:
    """Cliente mínimo: devuelve las respuestas en orden, o falla con `raises`."""

    def __init__(self, *responses, raises: Exception | None = None) -> None:
        self.responses = list(responses)
        self.raises = raises
        self.calls: list[dict] = []
        self.models = self

    def get(self):
        return self

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        if self.raises:
            raise self.raises
        return self.responses.pop(0)


def _response(text: str, tokens=(12, 3, 0)):
    return SimpleNamespace(text=text, usage_metadata=SimpleNamespace(
        prompt_token_count=tokens[0], candidates_token_count=tokens[1], cached_content_token_count=tokens[2],
    ))


def _window(client, **kw):
    return generate_window(model=MODEL_FLASH, message="texto", system_instruction="instrucciones", client=client, **kw)


def test_devuelve_las_preguntas_sin_validar_y_los_tokens():
    client = _FakeClient(_response(json.dumps({"preguntas": [{"tipo": "teoria"}]})))

    outcome = _window(client)

    assert outcome.items == [{"tipo": "teoria"}]
    assert (outcome.input_tokens, outcome.output_tokens, outcome.error) == (12, 3, None)
    config = client.calls[0]["config"]
    assert config.temperature == 0.3
    assert "instrucciones" in str(config.system_instruction)
    assert client.calls[0]["contents"] == "texto"


def test_una_respuesta_ilegible_se_reintenta_una_vez():
    client = _FakeClient(_response("esto no es json"), _response('{"preguntas": []}'))

    outcome = _window(client)

    assert outcome.error is None and outcome.items == []
    assert len(client.calls) == 2
    assert outcome.input_tokens == 24  # se pagaron los dos intentos


def test_dos_respuestas_ilegibles_dejan_la_ventana_fallida():
    client = _FakeClient(_response("x"), _response('{"preguntas": "hola"}'))

    outcome = _window(client)

    assert outcome.items == []
    assert outcome.error.startswith("respuesta ilegible")
    assert outcome.input_tokens == 24


def test_un_error_de_la_api_no_se_reintenta():
    client = _FakeClient(raises=RuntimeError("400 INVALID_ARGUMENT: request not supported"))

    outcome = _window(client)

    assert "400 INVALID_ARGUMENT" in outcome.error
    assert len(client.calls) == 1


def test_una_respuesta_real_de_gemini_3_con_thought_signature_se_lee():
    from google.genai import types

    response = types.GenerateContentResponse(
        candidates=[types.Candidate(content=types.Content(role="model", parts=[types.Part(
            text=json.dumps({"preguntas": [{"tipo": "teoria"}]}),
            thought_signature=b"\x12\x8e'\n\x8b'\x01i\x14}\x13\xbe",
        )]))],
        usage_metadata=types.GenerateContentResponseUsageMetadata(prompt_token_count=100, candidates_token_count=50),
    )

    outcome = _window(_FakeClient(response))

    assert outcome.items == [{"tipo": "teoria"}]
    assert (outcome.input_tokens, outcome.output_tokens) == (100, 50)


def test_verify_exercise_lee_el_resultado():
    result = VerificationResult(razonamiento="…", opcion="C", dificultad="igual")
    client = _FakeClient(_response(result.model_dump_json(), tokens=(30, 20, 0)))

    outcome = verify_exercise(model=MODEL_FLASH, message="m", system_instruction="s", client=client)

    assert outcome.result == result and outcome.error is None
    assert (outcome.input_tokens, outcome.output_tokens) == (30, 20)
    assert client.calls[0]["config"].temperature == 0


def test_verify_exercise_con_respuesta_ilegible_devuelve_el_motivo():
    outcome = verify_exercise(model=MODEL_FLASH, message="m", system_instruction="s",
                              client=_FakeClient(_response("no")))
    assert outcome.result is None and outcome.error.startswith("respuesta ilegible")


def test_verify_exercise_con_error_de_la_api_devuelve_el_motivo():
    outcome = verify_exercise(model=MODEL_FLASH, message="m", system_instruction="s",
                              client=_FakeClient(raises=RuntimeError("500 INTERNAL")))
    assert outcome.result is None and "500 INTERNAL" in outcome.error
```

- [ ] **Step 2: Run to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_generate_window.py -q`
Expected: FAIL con `ImportError: cannot import name 'generate_window'`.

- [ ] **Step 3: Implement** — en `gemini/generate.py`, cambia `from qgen.prompts.schemas import GeneratedQuestion` por:

```python
from qgen.prompts.schemas import GeneratedQuestion, VerificationResult, WindowResponse
```

y añade al final del fichero:

```python
# ─── Flujo por ventanas (spec §6 y §7) ─────────────────────────────────────


@dataclass
class WindowOutcome:
    """Las preguntas crudas de una ventana (sin validar) y lo que costó pedirlas."""

    items: list[dict]
    error: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    latency_s: float = 0.0


def generate_window(
    *,
    cache: DocumentCache | None = None,
    model: str | None = None,
    message: str,
    system_instruction: str,
    client: GeminiClient | None = None,
    attempts: int = 2,
) -> WindowOutcome:
    """Una llamada por ventana. Si la respuesta no se puede leer, se reintenta
    (`attempts` en total); los tokens de todos los intentos se suman."""
    gc = client or default_client()
    raw_client = gc.get()
    target_model = cache.model if cache else model
    if not target_model:
        raise ValueError("Must provide either cache or model")

    from google.genai import types

    config_kwargs = {
        "response_mime_type": "application/json",
        "response_schema": WindowResponse,
        "system_instruction": system_instruction,
        "temperature": 0.3,
    }
    if cache:
        config_kwargs["cached_content"] = cache.name

    tokens = [0, 0, 0]
    error: str | None = None
    started = time.perf_counter()
    for _ in range(attempts):
        try:
            response = _generate_with_retry(
                raw_client=raw_client,
                model=target_model,
                contents=message,
                config=types.GenerateContentConfig(**config_kwargs),
            )
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            break
        for i, n in enumerate(_extract_usage(response)):
            tokens[i] += n
        try:
            items = json.loads(getattr(response, "text", "") or "")["preguntas"]
            if not isinstance(items, list):
                raise TypeError("`preguntas` no es una lista")
        except Exception as exc:
            error = f"respuesta ilegible: {type(exc).__name__}: {exc}"
            continue
        return WindowOutcome(
            items=items, input_tokens=tokens[0], output_tokens=tokens[1], cached_tokens=tokens[2],
            latency_s=time.perf_counter() - started,
        )
    return WindowOutcome(
        items=[], error=error, input_tokens=tokens[0], output_tokens=tokens[1], cached_tokens=tokens[2],
        latency_s=time.perf_counter() - started,
    )


@dataclass
class VerificationOutcome:
    result: VerificationResult | None
    error: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0


def verify_exercise(
    *,
    model: str,
    message: str,
    system_instruction: str,
    client: GeminiClient | None = None,
) -> VerificationOutcome:
    """Resuelve un ejercicio nuevo a ciegas y compara su dificultad con la del libro (temperatura 0)."""
    raw_client = (client or default_client()).get()

    from google.genai import types

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=VerificationResult,
        system_instruction=system_instruction,
        temperature=0,
    )
    try:
        response = _generate_with_retry(raw_client=raw_client, model=model, contents=message, config=config)
    except Exception as exc:
        return VerificationOutcome(result=None, error=f"{type(exc).__name__}: {exc}")

    in_tok, out_tok, cached_tok = _extract_usage(response)
    try:
        result = VerificationResult.model_validate_json(getattr(response, "text", "") or "")
    except Exception as exc:
        return VerificationOutcome(
            result=None, error=f"respuesta ilegible: {type(exc).__name__}: {exc}",
            input_tokens=in_tok, output_tokens=out_tok, cached_tokens=cached_tok,
        )
    return VerificationOutcome(result=result, input_tokens=in_tok, output_tokens=out_tok, cached_tokens=cached_tok)
```

- [ ] **Step 4: Run to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_generate_window.py question_generator/tests -q`
Expected: todo en verde.

- [ ] **Step 5: Commit**

```bash
git add question_generator/src/qgen/gemini/generate.py question_generator/tests/test_generate_window.py
git commit -m "feat(qgen): llamada por ventana y verificación de ejercicios en Gemini

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: Columnas nuevas, migración y persistencia

**Files:**
- Modify: `question_generator/src/qgen/models/schema.py` (clase `Question`)
- Modify: `question_generator/src/qgen/db/migration.py`
- Modify: `question_generator/src/qgen/db/persistence.py`
- Test: `question_generator/tests/test_qgen_persistence.py`

**Interfaces:**
- Produces: columnas `Question.question_type: str` (no nula, por defecto `"teoria"`), `Question.source_quote: str` (no nula, por defecto `""`), `Question.window_key: str | None` (indexada); `persist_question(..., question_type: str = "teoria", source_quote: str = "", window_key: str | None = None)`; `remove_questions_for_windows(session, *, manual_id: int, window_keys: list[str], node_ids: list[int]) -> int` (sustituye a `remove_existing_questions_for_nodes`, que se elimina); `init_question_tables()` añade las columnas que falten.

- [ ] **Step 1: Write the failing tests** — en `question_generator/tests/test_qgen_persistence.py`, cambia el import de `remove_existing_questions_for_nodes` por `remove_questions_for_windows`, sustituye `test_remove_existing_for_nodes` entero por lo siguiente y añade los demás tests al final:

```python
def test_regenerar_borra_solo_las_ventanas_que_se_rehacen():
    init_question_tables()
    with session_scope() as s:
        manual_id, node_id = _seed_manual_and_node(s)
        run = create_run(
            s, manual_id=manual_id, model="gemini-3.6-flash", mode="immediate",
            profile_used="manual", rules_snapshot={}, nodes_total=1,
        )
        for order, (prefix, window_key) in enumerate([("A", "1:0-0"), ("B", "1:1-1"), ("C", None)]):
            persist_question(
                s, run=run, node_id=node_id, manual_id=manual_id, generation_order=order,
                payload=_make_question(prefix), raw_response={}, window_key=window_key,
            )

    with session_scope() as s:
        # La de la ventana 1:0-0 y la antigua sin ventana del mismo nodo; la de 1:1-1 se queda.
        assert remove_questions_for_windows(s, manual_id=manual_id, window_keys=["1:0-0"], node_ids=[node_id]) == 2

    with session_scope() as s:
        assert [q.window_key for q in s.query(Question).all()] == ["1:1-1"]


def test_la_pregunta_guarda_tipo_cita_y_ventana():
    init_question_tables()
    with session_scope() as s:
        manual_id, node_id = _seed_manual_and_node(s)
        run = create_run(
            s, manual_id=manual_id, model="gemini-3.6-flash", mode="immediate",
            profile_used="manual", rules_snapshot={}, nodes_total=1,
        )
        persist_question(
            s, run=run, node_id=node_id, manual_id=manual_id, generation_order=0,
            payload=_make_question(), raw_response={},
            question_type="ejercicio_nuevo", source_quote="Texto de prueba.", window_key="1:0-0",
        )

    with session_scope() as s:
        q = s.query(Question).one()
        assert (q.question_type, q.source_quote, q.window_key) == ("ejercicio_nuevo", "Texto de prueba.", "1:0-0")


def test_por_defecto_una_pregunta_es_de_teoria_sin_cita():
    init_question_tables()
    with session_scope() as s:
        manual_id, node_id = _seed_manual_and_node(s)
        run = create_run(
            s, manual_id=manual_id, model="gemini-3.6-flash", mode="immediate",
            profile_used="manual", rules_snapshot={}, nodes_total=1,
        )
        persist_question(
            s, run=run, node_id=node_id, manual_id=manual_id, generation_order=0,
            payload=_make_question(), raw_response={},
        )

    with session_scope() as s:
        q = s.query(Question).one()
        assert (q.question_type, q.source_quote, q.window_key) == ("teoria", "", None)


def test_la_migracion_anade_las_columnas_nuevas_a_una_base_antigua():
    from etl.db.session import get_engine
    from sqlalchemy import inspect, text

    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE questions (id INTEGER PRIMARY KEY, run_id INTEGER, node_id INTEGER, "
            "manual_id INTEGER, generation_order INTEGER, question_text TEXT, justification TEXT, "
            "raw_response_json JSON, validation_status VARCHAR(32), validated_at DATETIME, "
            "created_at DATETIME, metadata_json JSON)"
        ))
        conn.execute(text("INSERT INTO questions (id, question_text) VALUES (1, 'vieja')"))

    init_question_tables()
    init_question_tables()  # se puede repetir

    columnas = {c["name"] for c in inspect(engine).get_columns("questions")}
    assert {"question_type", "source_quote", "window_key"} <= columnas
    with engine.connect() as conn:
        fila = conn.execute(text("SELECT question_type, source_quote FROM questions WHERE id = 1")).one()
    assert tuple(fila) == ("teoria", "")
```

- [ ] **Step 2: Run to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_qgen_persistence.py -q`
Expected: FAIL con `ImportError: cannot import name 'remove_questions_for_windows'`.

- [ ] **Step 3: Implement**

En `models/schema.py`, dentro de `class Question`, justo después de `metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)`, añade:

```python
    # qgen v2 (spec §8): tipo de pregunta, cita en que se apoya y ventana que la produjo.
    question_type: Mapped[str] = mapped_column(String(32), default="teoria", server_default="teoria")
    source_quote: Mapped[str] = mapped_column(Text, default="", server_default="")
    window_key: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
```

Sustituye `db/migration.py` entero por:

```python
"""Idempotent creation of the question-generation tables.

Importing :mod:`qgen.models.schema` registers the ORM mappings against the
same `Base.metadata` used by `etl.models.schema`. ``Base.metadata.create_all``
issues `CREATE TABLE IF NOT EXISTS` for *all* tables, but it never touches a
table that already exists: the columns added later are added here, one by one.
"""

from __future__ import annotations

from sqlalchemy import inspect, text

from etl.db.session import get_engine
from etl.models.schema import Base

# noqa: F401 — los imports son requeridos para que SQLAlchemy registre las nuevas tablas
import qgen.models.schema  # noqa: F401
import qgen.models.reference_schema  # noqa: F401

# Columnas de `questions` que llegaron después de crear la tabla (qgen v2, spec §8).
_QUESTION_COLUMNS: dict[str, str] = {
    "question_type": "VARCHAR(32) NOT NULL DEFAULT 'teoria'",
    "source_quote": "TEXT NOT NULL DEFAULT ''",
    "window_key": "VARCHAR(64)",
}


def init_question_tables(db_url: str | None = None) -> None:
    engine = get_engine(db_url)
    Base.metadata.create_all(engine)
    _add_missing_columns(engine)


def _add_missing_columns(engine) -> None:
    existing = {c["name"] for c in inspect(engine).get_columns("questions")}
    with engine.begin() as conn:
        for name, ddl in _QUESTION_COLUMNS.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE questions ADD COLUMN {name} {ddl}"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_questions_window_key ON questions (window_key)"))
```

En `db/persistence.py`:

1. En la firma de `persist_question`, después de `validation_status: str = "pending",`, añade:

```python
    question_type: str = "teoria",
    source_quote: str = "",
    window_key: str | None = None,
```

2. En el `Question(...)` de `persist_question`, después de `metadata_json=metadata or {},`, añade:

```python
        question_type=question_type,
        source_quote=source_quote,
        window_key=window_key,
```

3. Sustituye la función `remove_existing_questions_for_nodes` entera por:

```python
def remove_questions_for_windows(
    session: Session, *, manual_id: int, window_keys: list[str], node_ids: list[int]
) -> int:
    """--regenerate: borra las preguntas de las ventanas que se van a rehacer y las
    antiguas sin ventana (anteriores a v2) de esos nodos. Las demás ventanas del nodo
    conservan sus preguntas. Las opciones caen en cascada."""
    if not window_keys:
        return 0
    rows = (
        session.execute(
            select(Question)
            .where(Question.manual_id == manual_id)
            .where(
                Question.window_key.in_(window_keys)
                | (Question.window_key.is_(None) & Question.node_id.in_(node_ids))
            )
        )
        .scalars()
        .all()
    )
    for q in rows:
        session.delete(q)
    session.flush()
    return len(rows)
```

- [ ] **Step 4: Keep the package importable** — `pipeline.py` todavía importa la función borrada. Cambia en `pipeline.py` el import `remove_existing_questions_for_nodes` por `remove_questions_for_windows` y, en `run_generation`, la llamada

```python
        remove_existing_questions_for_nodes(session, manual_id=manual_id, node_ids=[n.id for n in nodes])
```

por esta (temporal: con `window_keys=[]` no borra nada; Task 9 reescribe `run_generation`, y ningún test actual usa `--regenerate`):

```python
        remove_questions_for_windows(session, manual_id=manual_id, window_keys=[], node_ids=[n.id for n in nodes])
```

- [ ] **Step 5: Run to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests -q`
Expected: todo en verde.

- [ ] **Step 6: Commit**

```bash
git add question_generator/src/qgen/models/schema.py question_generator/src/qgen/db question_generator/src/qgen/pipeline.py question_generator/tests/test_qgen_persistence.py
git commit -m "feat(qgen): tipo, cita y ventana en cada pregunta, con migración

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: Planificación de ventanas y reanudación

**Files:**
- Modify: `question_generator/src/qgen/pipeline.py` (añadir; el resto se reescribe en Task 9)
- Test: `question_generator/tests/test_plan_windows.py`

**Interfaces:**
- Consumes: `build_windows`, `Window` (Task 2); `Question.window_key` (Task 7); `persist_question(..., window_key=)` en tests.
- Produces (en `qgen.pipeline`): `WindowJob(window: Window, node_id: int, node_label: str, node_title: str, node_breadcrumb: str)` (dataclass congelada); `plan_windows(session, *, manual_id: int, only_node_id: int | None = None, regenerate: bool = False, limit: int | None = None) -> list[WindowJob]`; helpers `_nodes_with_text(session, *, manual_id, only_node_id) -> list[Node]` y `_done_window_keys(session, manual_id) -> set[str]`.

- [ ] **Step 1: Write the failing tests** — crea `question_generator/tests/test_plan_windows.py`:

```python
"""Qué ventanas procesa una corrida (spec §4): selección, reanudación y --limit."""

from datetime import datetime, timezone

from etl.db.session import session_scope
from etl.models.schema import Chunk, Manual, Node

from qgen.db.migration import init_question_tables
from qgen.db.persistence import create_run, persist_question
from qgen.pipeline import plan_windows
from qgen.prompts.schemas import GeneratedOption, GeneratedQuestion, OptionRole


def _seed(titles=("Capítulo 1", "Capítulo 2"), chunk_texts=("Texto del nodo.",)) -> tuple[int, list[int]]:
    init_question_tables()
    with session_scope() as session:
        manual = Manual(
            code="TST", title="Manual de prueba", source_path="no-existe.pdf", page_count=10,
            extractor_used="docling", ingested_at=datetime.now(timezone.utc), metadata_json={"profile": "manual"},
        )
        session.add(manual)
        session.flush()
        node_ids = []
        for i, title in enumerate(titles):
            node = Node(
                manual_id=manual.id, level=0, level_label="Capítulo", ordinal=str(i + 1), title=title,
                breadcrumb=title, page_start=i + 1, sort_key=f"{i + 1:02d}",
            )
            session.add(node)
            session.flush()
            node_ids.append(node.id)
            for j, text in enumerate(chunk_texts):
                session.add(Chunk(
                    node_id=node.id, manual_id=manual.id, ordinal=j, text=text,
                    char_count=len(text), page_start=i + 1, page_end=i + 1,
                ))
        return manual.id, node_ids


def _keys(manual_id: int, **kwargs) -> list[str]:
    with session_scope() as session:
        return [job.window.key for job in plan_windows(session, manual_id=manual_id, **kwargs)]


def _question() -> GeneratedQuestion:
    return GeneratedQuestion(
        question="¿Algo?",
        options=[
            GeneratedOption(role=OptionRole.CORRECT, text="a"),
            GeneratedOption(role=OptionRole.CONFUSA, text="b"),
            GeneratedOption(role=OptionRole.DISTRACTOR, text="c"),
            GeneratedOption(role=OptionRole.DISTRACTOR, text="d"),
        ],
        justification="…",
    )


def test_una_ventana_por_nodo_pequeno_en_orden():
    manual_id, (n1, n2) = _seed()

    with session_scope() as session:
        jobs = plan_windows(session, manual_id=manual_id)
        assert [job.window.key for job in jobs] == [f"{n1}:0-0", f"{n2}:0-0"]
        assert (jobs[0].node_label, jobs[0].node_title, jobs[0].node_breadcrumb) == ("Capítulo 1", "Capítulo 1", "Capítulo 1")


def test_las_introducciones_quedan_fuera():
    manual_id, (_, n2) = _seed(titles=("Introducción", "Capítulo 1"))
    assert _keys(manual_id) == [f"{n2}:0-0"]


def test_limit_cuenta_ventanas():
    manual_id, _ = _seed(chunk_texts=tuple(str(i) * 1500 for i in range(6)))  # 2 ventanas por nodo
    assert len(_keys(manual_id)) == 4
    assert len(_keys(manual_id, limit=3)) == 3


def test_solo_un_nodo():
    manual_id, (_, n2) = _seed()
    assert _keys(manual_id, only_node_id=n2) == [f"{n2}:0-0"]


def test_se_saltan_las_ventanas_ok_y_se_reintentan_las_fallidas():
    manual_id, (n1, n2) = _seed()
    with session_scope() as session:
        create_run(
            session, manual_id=manual_id, model="gemini-3.6-flash", mode="immediate", profile_used="manual",
            rules_snapshot={}, nodes_total=2, metadata_json={"ventanas": {f"{n1}:0-0": "ok", f"{n2}:0-0": "fallida"}},
        )
    assert _keys(manual_id) == [f"{n2}:0-0"]


def test_se_saltan_ventanas_con_preguntas_aunque_la_corrida_no_se_cerrara():
    manual_id, (n1, n2) = _seed()
    with session_scope() as session:
        run = create_run(
            session, manual_id=manual_id, model="gemini-3.6-flash", mode="immediate", profile_used="manual",
            rules_snapshot={}, nodes_total=2,
        )
        persist_question(
            session, run=run, node_id=n1, manual_id=manual_id, generation_order=0,
            payload=_question(), raw_response={}, window_key=f"{n1}:0-0",
        )
    assert _keys(manual_id) == [f"{n2}:0-0"]


def test_regenerate_ignora_el_historial():
    manual_id, (n1, n2) = _seed()
    with session_scope() as session:
        create_run(
            session, manual_id=manual_id, model="gemini-3.6-flash", mode="immediate", profile_used="manual",
            rules_snapshot={}, nodes_total=2, metadata_json={"ventanas": {f"{n1}:0-0": "ok"}},
        )
    assert _keys(manual_id, regenerate=True) == [f"{n1}:0-0", f"{n2}:0-0"]
```

- [ ] **Step 2: Run to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_plan_windows.py -q`
Expected: FAIL con `ImportError: cannot import name 'plan_windows'`.

- [ ] **Step 3: Implement** — en `pipeline.py`, añade el import `from qgen.windows import Window, build_windows` y, justo antes de la sección `# ---- Entrada Pública`, añade:

```python
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
```

- [ ] **Step 4: Run to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_plan_windows.py -q`
Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add question_generator/src/qgen/pipeline.py question_generator/tests/test_plan_windows.py
git commit -m "feat(qgen): plan de ventanas por corrida, con reanudación

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 9: Corrida por ventanas, estimación y CLI (retira el flujo viejo)

**Files:**
- Modify (reescribir): `question_generator/src/qgen/pipeline.py`
- Modify: `question_generator/src/qgen/cost.py`
- Modify: `question_generator/src/qgen/cli/generate.py`
- Modify: `question_generator/src/qgen/gemini/generate.py` (quitar `generate_one`, `GenerationOutcome`, `DraftOutcome`, `generate_draft_questions`)
- Modify: `question_generator/src/qgen/prompts/__init__.py`, `question_generator/src/qgen/prompts/schemas.py` (quitar `QuestionDraftList`)
- Delete: `question_generator/src/qgen/prompts/creator.py`, `prompts/system.py`, `prompts/render.py`, `question_generator/tests/test_prompts.py`, `question_generator/tests/test_dynamic_prompts.py`
- Modify: `question_generator/tests/test_baldor_rules.py`
- Test (reescribir): `question_generator/tests/test_pipeline.py`; Create: `question_generator/tests/test_cost.py`

**Interfaces:**
- Consumes: todo lo de Tasks 1–8.
- Produces: `run_generation(session, *, manual_id, model_name=MODEL_FLASH, mode="immediate", limit=None, only_node_id=None, regenerate=False, cache_ttl_seconds=3600, progress_cb=None) -> RunSummary` (mismas opciones; `limit` cuenta ventanas); `RunSummary` con los campos nuevos `windows_total`, `windows_failed`, `questions_saved`; `progress_cb(idx: int, total: int, job: WindowJob, resumen: dict | None, error: str | None)` donde `resumen = {"guardadas": int, "revision": int, "descartes": int}`; `estimate_only(...) -> tuple[WindowEstimate, int]` (el `int` son ventanas); en `qgen.cost`: `WindowEstimate` y `estimate_windows(*, model, mode, windows, window_chars, with_exercises, doc_tokens, cache_storage_hours=1.0) -> WindowEstimate` (sustituyen a `CostEstimate`/`estimate_run`, que se eliminan).

- [ ] **Step 1: Write the failing tests**

Crea `question_generator/tests/test_cost.py`:

```python
"""Estimación de costo por ventanas (spec §9)."""

from qgen.cost import estimate_windows
from qgen.gemini.client import MODEL_FLASH


def _estimate(**kwargs):
    base = dict(model=MODEL_FLASH, mode="immediate", windows=2, window_chars=3500, with_exercises=True, doc_tokens=0)
    return estimate_windows(**{**base, **kwargs})


def test_cuenta_preguntas_y_verificaciones_por_caracteres():
    e = _estimate()
    assert (e.windows, e.n_questions, e.verifications) == (2, 10, 2)
    assert e.total_usd > 0


def test_sin_ejercicios_no_hay_verificaciones():
    assert _estimate(with_exercises=False).verifications == 0
    assert _estimate(with_exercises=False).total_usd < _estimate().total_usd


def test_sin_ventanas_no_cuesta_nada():
    assert _estimate(windows=0, window_chars=0).total_usd == 0
```

Sustituye `question_generator/tests/test_pipeline.py` entero por:

```python
"""Orquestación de `qgen-generate` por ventanas (spec §4–§8), con Gemini simulado.

No se prueba la calidad de las preguntas sino lo que rodea a las llamadas: una
llamada por ventana, qué se guarda y con qué estado, qué se descarta, que la
corrida siempre se cierre, que se pueda reanudar y que el costo cuente todo.
"""

from datetime import datetime, timezone

import pytest
from etl.db.session import session_scope
from etl.models.schema import Chunk, Manual, Node
from sqlalchemy import select

import qgen.pipeline as pipeline
from qgen.cli.generate import _progress_cb
from qgen.cost import actual_cost_usd
from qgen.db.migration import init_question_tables
from qgen.gemini.cache import DocumentCache
from qgen.gemini.client import MODEL_FLASH, MODEL_PRO
from qgen.gemini.generate import VerificationOutcome, WindowOutcome
from qgen.models.schema import GenerationRun, Question
from qgen.prompts.schemas import VerificationResult

TEXTO = "La guerra es un conflicto entre sociedades que luchan violentamente."
EJEMPLO = "EJEMPLO 1 Derivar f(x) = x^2. Solución: f'(x) = 2x."


def _item(pregunta="¿Qué es la guerra?", *, tipo="teoria", correcta="un conflicto entre sociedades",
          cita=TEXTO, prefijo="T") -> dict:
    return {
        "tipo": tipo,
        "pregunta": pregunta,
        "opciones": [
            {"rol": "correct", "texto": correcta},
            {"rol": "confusa", "texto": f"{prefijo} confusa"},
            {"rol": "distractor", "texto": f"{prefijo} distractor 1"},
            {"rol": "distractor", "texto": f"{prefijo} distractor 2"},
        ],
        "cita": cita,
        "justificacion": "Lo dice el texto.",
    }


def _ejercicio_nuevo() -> dict:
    return _item("Deriva f(x) = x^3.", tipo="ejercicio_nuevo", correcta="3x^2", cita=EJEMPLO, prefijo="E")


def _seed(n_nodes: int = 2, *, profile: str = "manual", texto: str = TEXTO) -> int:
    init_question_tables()
    with session_scope() as session:
        manual = Manual(
            code="TST", title="Manual de prueba", source_path="no-existe.pdf", page_count=10,
            extractor_used="docling", ingested_at=datetime.now(timezone.utc), metadata_json={"profile": profile},
        )
        session.add(manual)
        session.flush()
        for i in range(n_nodes):
            node = Node(
                manual_id=manual.id, level=0, level_label="Capítulo", ordinal=str(i + 1),
                title=f"Capítulo {i + 1}", breadcrumb=f"Capítulo {i + 1}", page_start=i + 1, sort_key=f"{i + 1:02d}",
            )
            session.add(node)
            session.flush()
            session.add(Chunk(
                node_id=node.id, manual_id=manual.id, ordinal=0, text=texto,
                char_count=len(texto), page_start=i + 1, page_end=i + 1,
            ))
        return manual.id


def _letra(message: str, texto: str) -> str:
    """La letra con que la verificación presenta la opción `texto`."""
    for line in message.splitlines():
        if line[1:3] == ") " and line[3:] == texto:
            return line[0]
    raise AssertionError(f"{texto!r} no está en las opciones de la verificación")


class FakeGemini:
    """Sustituye cache, llamada por ventana y verificación del pipeline."""

    def __init__(self, monkeypatch, *, cache_tokens: int = 0) -> None:
        self.cache_models: list[str] = []
        self.deleted: list[str] = []
        self.messages: list[str] = []
        self.cache_tokens = cache_tokens
        self.window = lambda message: WindowOutcome(items=[_item()], input_tokens=100, output_tokens=50, cached_tokens=80)
        self.verify = lambda message: VerificationOutcome(
            result=VerificationResult(razonamiento="…", opcion=_letra(message, "3x^2"), dificultad="igual"),
        )
        monkeypatch.setattr(pipeline, "build_or_get_cache", self._build_cache)
        monkeypatch.setattr(pipeline, "delete_cache", lambda cache: self.deleted.append(cache.name))
        monkeypatch.setattr(pipeline, "generate_window", self._generate_window)
        monkeypatch.setattr(pipeline, "verify_exercise", lambda *, message, **_: self.verify(message))

    def _generate_window(self, *, message, **_):
        self.messages.append(message)
        return self.window(message)

    def _build_cache(self, *, model, **_):
        self.cache_models.append(model)
        return DocumentCache(
            name="cachedContents/test", model=model, file_name="files/test",
            system_version="test", expire_at_epoch=0.0, token_count=self.cache_tokens,
        )


def _run(manual_id: int, **kwargs):
    with session_scope() as session:
        return pipeline.run_generation(session, manual_id=manual_id, **kwargs)


def _runs():
    with session_scope() as session:
        return session.execute(select(GenerationRun).order_by(GenerationRun.id)).scalars().all()


def _questions() -> list[dict]:
    with session_scope() as session:
        return [
            {
                "tipo": q.question_type, "estado": q.validation_status, "ventana": q.window_key,
                "cita": q.source_quote, "motivos": (q.metadata_json or {}).get("motivos"),
            }
            for q in session.execute(select(Question).order_by(Question.id)).scalars().all()
        ]


# ─── Una llamada por ventana ───────────────────────────────────────────────


def test_una_llamada_por_ventana_y_sus_preguntas_se_guardan(monkeypatch):
    manual_id = _seed()
    fake = FakeGemini(monkeypatch)

    summary = _run(manual_id)

    assert len(fake.messages) == 2
    assert (summary.windows_total, summary.windows_failed, summary.questions_saved) == (2, 0, 2)
    [run] = _runs()
    assert run.status == "succeeded"
    assert (run.nodes_total, run.nodes_completed, run.nodes_failed) == (2, 2, 0)
    assert sorted(run.metadata_json["ventanas"].values()) == ["ok", "ok"]
    assert run.metadata_json["preguntas"] == {"teoria/pending": 2}
    preguntas = _questions()
    assert [(q["tipo"], q["estado"], q["cita"]) for q in preguntas] == [("teoria", "pending", TEXTO)] * 2
    assert {q["ventana"] for q in preguntas} == set(run.metadata_json["ventanas"])
    assert fake.deleted == ["cachedContents/test"]


def test_el_mensaje_lleva_el_titulo_del_manual_la_ruta_y_el_texto(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)

    _run(manual_id)

    [message] = fake.messages
    assert "Manual de prueba" in message and "Capítulo 1" in message and TEXTO in message


# ─── Descartes y revisión ──────────────────────────────────────────────────


def test_una_pregunta_mal_formada_no_tumba_la_ventana(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)
    fake.window = lambda message: WindowOutcome(items=[_item(), {"tipo": "teoria"}])

    _run(manual_id)

    [run] = _runs()
    assert run.status == "succeeded"
    assert len(_questions()) == 1
    assert run.metadata_json["descartes"][0]["motivo"].startswith("pregunta 2: estructura inválida")


def test_un_tipo_que_el_perfil_no_permite_se_descarta(monkeypatch):
    manual_id = _seed(n_nodes=1, profile="manual")  # militar: solo teoría
    fake = FakeGemini(monkeypatch)
    fake.window = lambda message: WindowOutcome(items=[_item(), _ejercicio_nuevo()])

    _run(manual_id)

    assert [q["tipo"] for q in _questions()] == ["teoria"]
    [run] = _runs()
    assert run.metadata_json["descartes"][0]["motivo"] == "tipo ejercicio_nuevo no permitido en manual"


def test_una_respuesta_parafraseada_queda_en_revision_con_su_motivo(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)
    fake.window = lambda message: WindowOutcome(items=[_item(correcta="una pelea violenta")])

    _run(manual_id)

    [q] = _questions()
    assert (q["estado"], q["motivos"]) == ("needs_review", ["respuesta parafraseada"])


def test_las_duplicadas_se_descartan(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)
    fake.window = lambda message: WindowOutcome(items=[_item(), _item(prefijo="U")])

    _run(manual_id)

    [q] = _questions()
    [run] = _runs()
    assert run.metadata_json["descartes"] == [{"window_key": q["ventana"], "motivo": "duplicada"}]


# ─── Ejercicios nuevos ─────────────────────────────────────────────────────


def test_el_ejercicio_nuevo_verificado_queda_pendiente(monkeypatch):
    manual_id = _seed(n_nodes=1, profile="calculo_una_variable", texto=EJEMPLO)
    fake = FakeGemini(monkeypatch)
    fake.window = lambda message: WindowOutcome(items=[_ejercicio_nuevo()])

    _run(manual_id)

    [q] = _questions()
    assert (q["tipo"], q["estado"]) == ("ejercicio_nuevo", "pending")


@pytest.mark.parametrize("opcion, dificultad, motivo", [
    ("otra", "igual", "la verificación eligió"),
    ("ninguna", "igual", "ninguna"),
    ("clave", "mayor", "supera la dificultad del PDF"),
])
def test_la_verificacion_manda_a_revision(monkeypatch, opcion, dificultad, motivo):
    manual_id = _seed(n_nodes=1, profile="calculo_una_variable", texto=EJEMPLO)
    fake = FakeGemini(monkeypatch)
    fake.window = lambda message: WindowOutcome(items=[_ejercicio_nuevo()])

    def verify(message):
        clave = _letra(message, "3x^2")
        elegida = {"clave": clave, "otra": "A" if clave != "A" else "B"}.get(opcion, opcion)
        return VerificationOutcome(result=VerificationResult(razonamiento="…", opcion=elegida, dificultad=dificultad))

    fake.verify = verify

    _run(manual_id)

    [q] = _questions()
    assert q["estado"] == "needs_review"
    assert any(motivo in m for m in q["motivos"])


def test_si_la_verificacion_falla_la_pregunta_queda_en_revision(monkeypatch):
    manual_id = _seed(n_nodes=1, profile="calculo_una_variable", texto=EJEMPLO)
    fake = FakeGemini(monkeypatch)
    fake.window = lambda message: WindowOutcome(items=[_ejercicio_nuevo()])
    fake.verify = lambda message: VerificationOutcome(result=None, error="RuntimeError: 500 INTERNAL")

    _run(manual_id)

    [q] = _questions()
    assert (q["estado"], q["motivos"]) == ("needs_review", ["verificación fallida"])


# ─── Reanudar ──────────────────────────────────────────────────────────────


def test_una_ventana_fallida_se_retoma_en_la_siguiente_corrida(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)
    fake.window = lambda message: WindowOutcome(items=[], error="respuesta ilegible: JSONDecodeError", input_tokens=10)

    _run(manual_id)

    [primera] = _runs()
    assert primera.status == "partial"
    assert (primera.nodes_completed, primera.nodes_failed) == (0, 1)
    assert list(primera.metadata_json["ventanas"].values()) == ["fallida"]
    assert primera.metadata_json["failures"][0]["error"].startswith("respuesta ilegible")

    fake.window = lambda message: WindowOutcome(items=[_item()])
    _run(manual_id)

    assert len(fake.messages) == 2
    assert _runs()[1].status == "succeeded"
    assert len(_questions()) == 1


def test_las_ventanas_ya_hechas_no_se_repiten(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)

    _run(manual_id)
    segunda = _run(manual_id)

    assert len(fake.messages) == 1
    assert (segunda.nodes_total, segunda.windows_total) == (0, 0)
    assert len(_questions()) == 1


def test_regenerate_rehace_las_ventanas(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)

    _run(manual_id)
    _run(manual_id, regenerate=True)

    assert len(fake.messages) == 2
    assert len(_questions()) == 1  # la primera se borró antes de rehacer la ventana


# ─── La corrida siempre se cierra ──────────────────────────────────────────


def test_un_error_inesperado_marca_la_corrida_failed_y_borra_el_cache(monkeypatch):
    manual_id = _seed()
    fake = FakeGemini(monkeypatch)

    def boom(message):
        raise RuntimeError("se cayó a medias")

    fake.window = boom

    with pytest.raises(RuntimeError, match="se cayó a medias"):
        _run(manual_id)

    [run] = _runs()
    assert run.status == "failed"
    assert run.completed_at is not None
    assert fake.deleted == ["cachedContents/test"]


def test_ctrl_c_marca_la_corrida_cancelled_y_conserva_lo_guardado(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)

    def interrupt(*_):
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        _run(manual_id, progress_cb=interrupt)

    [run] = _runs()
    assert run.status == "cancelled"
    assert run.nodes_completed == 1
    # Se guarda antes de avisar al callback: lo ya pagado no se pierde.
    assert len(_questions()) == 1
    assert fake.deleted == ["cachedContents/test"]


def test_el_callback_del_cli_acepta_ventanas_buenas_y_fallidas(monkeypatch):
    manual_id = _seed()
    fake = FakeGemini(monkeypatch)
    # `list.pop` es atómico: las dos ventanas se piden desde dos hilos.
    respuestas = [WindowOutcome(items=[_item()]), WindowOutcome(items=[], error="respuesta ilegible")]
    fake.window = lambda message: respuestas.pop(0)

    summary = _run(manual_id, progress_cb=_progress_cb)

    assert (summary.windows_total, summary.windows_failed) == (2, 1)


# ─── Modelo ────────────────────────────────────────────────────────────────


def test_el_alias_del_modelo_se_resuelve_antes_de_llamar(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)

    summary = _run(manual_id, model_name="pro")

    assert summary.model == MODEL_PRO
    assert fake.cache_models == [MODEL_PRO]
    assert summary.actual_cost_usd > 0


def test_un_modelo_desconocido_se_rechaza_antes_de_crear_la_corrida(monkeypatch):
    manual_id = _seed(n_nodes=1)
    FakeGemini(monkeypatch)

    with pytest.raises(ValueError, match="Unknown model"):
        _run(manual_id, model_name="deepseek-r1:8b")

    assert _runs() == []


# ─── Costo ─────────────────────────────────────────────────────────────────


def test_el_costo_cuenta_la_ventana_la_verificacion_y_el_cache(monkeypatch):
    manual_id = _seed(n_nodes=1, profile="calculo_una_variable", texto=EJEMPLO)
    fake = FakeGemini(monkeypatch, cache_tokens=1_000)
    fake.window = lambda message: WindowOutcome(items=[_ejercicio_nuevo()], input_tokens=100, output_tokens=50, cached_tokens=80)
    fake.verify = lambda message: VerificationOutcome(
        result=VerificationResult(razonamiento="…", opcion=_letra(message, "3x^2"), dificultad="igual"),
        input_tokens=30, output_tokens=20,
    )

    summary = _run(manual_id)

    [run] = _runs()
    assert (run.cost_input_tokens, run.cost_output_tokens, run.cost_cached_tokens) == (130, 70, 80)
    assert run.metadata_json["cache_tokens"] == 1_000
    sin_cache = actual_cost_usd(model=MODEL_FLASH, mode="immediate", input_tokens=130, output_tokens=70, cached_tokens=80)
    assert summary.actual_cost_usd > sin_cache


# ─── Dry-run ───────────────────────────────────────────────────────────────


def _estimate(manual_id: int):
    with session_scope() as session:
        return pipeline.estimate_only(
            session, manual_id=manual_id, model_name="flash", mode="immediate",
            limit=None, only_node_id=None, regenerate=False,
        )


def test_el_dry_run_estima_por_ventanas():
    manual_id = _seed(n_nodes=3)

    estimate, n_windows = _estimate(manual_id)

    assert n_windows == 3 and estimate.windows == 3
    assert estimate.model == MODEL_FLASH
    assert estimate.verifications == 0  # manual militar: sin ejercicios
    assert estimate.cache_tokens > 0 and estimate.total_usd > 0


def test_el_dry_run_sin_nada_que_generar_no_cuesta(monkeypatch):
    manual_id = _seed(n_nodes=1)
    FakeGemini(monkeypatch)
    _run(manual_id)

    estimate, n_windows = _estimate(manual_id)

    assert n_windows == 0 and estimate.total_usd == 0
```

En `question_generator/tests/test_baldor_rules.py`, sustituye los imports de `creator`/`system` por `from qgen.prompts.families import build_window_instruction` y el test `test_algebra_baldor_prompt_rendering` por:

```python
def test_algebra_baldor_prompt_rendering():
    """La instrucción por ventana lleva las reglas de Baldor y pide ejercicios."""
    instr = build_window_instruction(get_default_rules("algebra_baldor"), manual_title="Álgebra de Baldor")
    assert "factorización" in instr or "factorizacion" in instr
    assert "errores algebraicos típicos" in instr
    assert '"ejercicio_nuevo"' in instr
```

Borra `question_generator/tests/test_prompts.py` y `question_generator/tests/test_dynamic_prompts.py` (cubiertos por `test_families.py`).

- [ ] **Step 2: Run to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_pipeline.py question_generator/tests/test_cost.py -q`
Expected: FAIL (`ImportError: cannot import name 'estimate_windows'` y `WindowOutcome` no parcheado en `pipeline`).

- [ ] **Step 3: Implement**

**3a. `cost.py`** — sustituye la dataclass `CostEstimate` y la función `estimate_run` enteras por:

```python
# Supuestos de la estimación por ventanas (spec §9): valores iniciales, se calibran
# con la primera corrida real.
INSTRUCTION_TOKENS = 1500
CHARS_PER_QUESTION = 350
OUTPUT_TOKENS_PER_QUESTION = 350
CHARS_PER_NEW_EXERCISE = 1500
VERIFICATION_INPUT_TOKENS = 1000
VERIFICATION_OUTPUT_TOKENS = 800


@dataclass
class WindowEstimate:
    model: str
    mode: str
    windows: int
    window_tokens: int
    n_questions: int
    verifications: int
    cache_tokens: int
    cache_create_usd: float
    cache_storage_usd: float
    generation_usd: float
    verification_usd: float
    total_usd: float


def estimate_windows(
    *,
    model: str,
    mode: str,
    windows: int,
    window_chars: int,
    with_exercises: bool,
    doc_tokens: int,
    cache_storage_hours: float = 1.0,
) -> WindowEstimate:
    """Una llamada por ventana (instrucción + texto de la ventana + documento cacheado)
    y una verificación por cada ejercicio nuevo estimado."""
    if model not in _PRICING:
        raise ValueError(f"No pricing entry for {model!r}")
    in_p, cached_p, out_p, store_p = _PRICING[model]
    discount = BATCH_DISCOUNT if mode == "batch" else 1.0

    window_tokens = int(window_chars / CHARS_PER_TOKEN)
    n_questions = round(window_chars / CHARS_PER_QUESTION)
    verifications = round(window_chars / CHARS_PER_NEW_EXERCISE) if with_exercises else 0

    cache_create = (doc_tokens * in_p) / 1_000_000
    cache_storage = (doc_tokens * store_p * cache_storage_hours) / 1_000_000
    generation = (
        windows * (doc_tokens * cached_p + INSTRUCTION_TOKENS * in_p * discount)
        + window_tokens * in_p * discount
        + n_questions * OUTPUT_TOKENS_PER_QUESTION * out_p * discount
    ) / 1_000_000
    verification = verifications * (
        VERIFICATION_INPUT_TOKENS * in_p + VERIFICATION_OUTPUT_TOKENS * out_p
    ) * discount / 1_000_000
    total = cache_create + cache_storage + generation + verification if windows else 0.0

    return WindowEstimate(
        model=model,
        mode=mode,
        windows=windows,
        window_tokens=window_tokens,
        n_questions=n_questions,
        verifications=verifications,
        cache_tokens=doc_tokens,
        cache_create_usd=round(cache_create, 4),
        cache_storage_usd=round(cache_storage, 4),
        generation_usd=round(generation, 6),
        verification_usd=round(verification, 6),
        total_usd=round(total, 6),
    )
```

**3b. `pipeline.py`** — sustituye el fichero entero por:

```python
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
```

**3c. `cli/generate.py`** — cambia la ayuda de las opciones:

```python
    limit: int | None = typer.Option(None, help="Process at most N windows (dev/iteration)."),
    node_id: int | None = typer.Option(None, "--node-id", help="Generate only the windows of this node id."),
    regenerate: bool = typer.Option(False, "--regenerate", help="Delete and redo the questions of the selected windows."),
```

y sustituye `_progress_cb`, `_print_estimate` y `_print_summary` por:

```python
def _progress_cb(idx: int, total: int, job, resumen: dict | None, error: str | None) -> None:
    etiqueta = f"{job.node_label} [{job.window.key}]"
    if error is not None:
        console.print(f"[red][{idx + 1}/{total}] {etiqueta}  ERROR: {error}[/]")
    else:
        console.print(
            f"[green][{idx + 1}/{total}] {etiqueta}  OK[/] {resumen['guardadas']} preguntas "
            f"({resumen['revision']} a revisar, {resumen['descartes']} descartadas)"
        )


def _print_estimate(estimate, n_windows: int, mode: str) -> None:
    table = Table(title=f"Cost estimate ({mode}, {estimate.model})")
    table.add_column("Field")
    table.add_column("Value", justify="right")
    rows = [
        ("Windows to process", str(n_windows)),
        ("Window tokens", f"{estimate.window_tokens:,}"),
        ("Questions (est.)", str(estimate.n_questions)),
        ("Exercise verifications (est.)", str(estimate.verifications)),
        ("Doc tokens (cached)", f"{estimate.cache_tokens:,}"),
        ("Cache create (one-off)", f"${estimate.cache_create_usd:.4f}"),
        ("Cache storage (1h)", f"${estimate.cache_storage_usd:.4f}"),
        ("Generation", f"${estimate.generation_usd:.4f}"),
        ("Verification", f"${estimate.verification_usd:.4f}"),
        ("TOTAL", f"${estimate.total_usd:.4f}"),
    ]
    for k, v in rows:
        table.add_row(k, v)
    console.print(table)


def _print_summary(summary) -> None:
    table = Table(title=f"Run #{summary.run_id} summary")
    table.add_column("Field")
    table.add_column("Value", justify="right")
    rows = [
        ("Mode", summary.mode),
        ("Model", summary.model),
        ("Profile", summary.profile),
        ("Windows", str(summary.windows_total)),
        ("Windows failed", str(summary.windows_failed)),
        ("Questions saved", str(summary.questions_saved)),
        ("Nodes total", str(summary.nodes_total)),
        ("Nodes completed", str(summary.nodes_completed)),
        ("Actual cost (USD)", f"${summary.actual_cost_usd:.4f}"),
    ]
    if summary.batch_job_id:
        rows.append(("Batch job id", summary.batch_job_id))
    for k, v in rows:
        table.add_row(k, v)
    console.print(table)
```

**3d. Retirar el flujo viejo:**

- Borra `question_generator/src/qgen/prompts/creator.py`, `prompts/system.py` y `prompts/render.py`.
- En `gemini/generate.py`, borra `GenerationOutcome`, `generate_one`, `DraftOutcome` y `generate_draft_questions`; cambia el docstring del módulo por `"""Llamadas a Gemini en modo inmediato: una por ventana y la verificación de ejercicios."""` y el import de schemas por `from qgen.prompts.schemas import VerificationResult, WindowResponse`. Quita `from pydantic import ValidationError` si queda sin uso.
- En `prompts/schemas.py`, borra la clase `QuestionDraftList`.
- Sustituye `prompts/__init__.py` por:

```python
from qgen.prompts.families import (
    SYSTEM_VERSION,
    build_verification_instruction,
    build_verification_message,
    build_window_instruction,
    build_window_message,
)
from qgen.prompts.schemas import (
    LETRAS,
    MAX_PREGUNTAS_POR_VENTANA,
    REQUIRED_ROLE_COUNTS,
    GeneratedOption,
    GeneratedQuestion,
    OptionRole,
    QuestionType,
    VerificationResult,
    WindowOption,
    WindowQuestion,
    WindowResponse,
)

__all__ = [
    "GeneratedOption",
    "GeneratedQuestion",
    "LETRAS",
    "MAX_PREGUNTAS_POR_VENTANA",
    "OptionRole",
    "QuestionType",
    "REQUIRED_ROLE_COUNTS",
    "SYSTEM_VERSION",
    "VerificationResult",
    "WindowOption",
    "WindowQuestion",
    "WindowResponse",
    "build_verification_instruction",
    "build_verification_message",
    "build_window_instruction",
    "build_window_message",
]
```

- [ ] **Step 4: Run to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests -q`
Expected: todo en verde.

Run: `grep -rn "generate_draft_questions\|build_creator_instruction\|build_variable_prompt\|build_system_instruction\|QuestionDraftList\|estimate_run\|CostEstimate\|generate_one" question_generator/src explorer/src --include=*.py`
Expected: sin resultados.

- [ ] **Step 5: Commit**

```bash
git add -A question_generator
git commit -m "feat(qgen): generación por ventanas con una sola llamada y verificación

Sustituye el flujo creador + una llamada por pregunta. Cada ventana se pide
una vez; las preguntas se revisan por tipo, los ejercicios nuevos se
verifican, las duplicadas se descartan y la corrida se puede reanudar.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 10: Contrato v2 del bundle

**Files:**
- Modify: `question_generator/src/qgen/bundle/spec.py`
- Modify: `question_generator/src/qgen/bundle/build.py`
- Modify: `CONTRATO-BUNDLE.md`
- Test: `question_generator/tests/test_bundle_spec.py`, `question_generator/tests/test_bundle_export.py`, `explorer/tests/test_export_page.py`

**Interfaces:**
- Consumes: `Question.question_type`, `Question.source_quote` (Task 7).
- Produces: `BUNDLE_VERSION = 2`, `SUPPORTED_VERSIONS = frozenset({1, 2})`, `QUESTION_TYPES`, `MAX_LEN["source_quote"] = 2000`; cada pregunta del bundle v2 trae `question_type` y `source_quote`; identidad v2 = `(run_ref, generation_order)`.

- [ ] **Step 1: Write the failing tests**

En `test_bundle_spec.py`: en `_bundle()`, dentro de la pregunta, después de `"justification": "Porque el artículo 1 dice …",` añade:

```python
                "question_type": "teoria",
                "source_quote": "El fuero de guerra …",
```

Sustituye `test_dos_preguntas_para_la_misma_corrida_y_nodo` por:

```python
def _v1(b):
    b["bundle_version"] = 1
    for q in b["questions"]:
        q.pop("question_type")
        q.pop("source_quote")


def test_v2_admite_varias_preguntas_por_nodo():
    def mutate(b):
        otra = deepcopy(b["questions"][0])
        otra.update(generation_order=1, options=_options("z"))
        b["questions"].append(otra)

    assert _errors(mutate) == []


def test_v2_rechaza_el_mismo_orden_dos_veces_en_una_corrida():
    def mutate(b):
        otra = deepcopy(b["questions"][0])
        otra["options"] = _options("z")
        b["questions"].append(otra)

    assert any("`generation_order` 0" in e and "índice único" in e for e in _errors(mutate))


def test_v2_exige_un_tipo_de_pregunta_conocido():
    assert any("`question_type`" in e for e in _errors(lambda b: b["questions"][0].update(question_type="examen")))
    assert any("`question_type`" in e for e in _errors(lambda b: b["questions"][0].pop("question_type")))


def test_v2_exige_la_cita():
    assert any("`source_quote`" in e for e in _errors(lambda b: b["questions"][0].pop("source_quote")))
    assert any("máximo es 2000" in e for e in _errors(lambda b: b["questions"][0].update(source_quote="x" * 2001)))


def test_v1_sigue_siendo_valido_sin_los_campos_nuevos():
    assert _errors(_v1) == []


def test_v1_mantiene_una_pregunta_por_corrida_y_nodo():
    def mutate(b):
        _v1(b)
        otra = deepcopy(b["questions"][0])
        otra.update(generation_order=1, options=_options("z"))
        b["questions"].append(otra)

    assert any("índice único" in e for e in _errors(mutate))
```

En `test_bundle_export.py`: añade arriba `from qgen.models.schema import GenerationRun` y la constante `CITA = "El fuero de guerra subsiste para los delitos del orden militar."`; en **todas** las llamadas a `persist_question` del fichero añade `question_type="teoria", source_quote=CITA,`; y añade al final:

```python
def test_la_pregunta_viaja_con_su_tipo_y_su_cita():
    init_question_tables()
    with session_scope() as session:
        manual_id, _, _ = _seed_with_questions(session)
        bundle = build_bundle(session, manual_id=manual_id)

    assert bundle["bundle_version"] == 2
    q = bundle["questions"][0]
    assert (q["question_type"], q["source_quote"]) == ("teoria", CITA)


def test_varias_preguntas_del_mismo_nodo_se_exportan():
    init_question_tables()
    with session_scope() as session:
        manual_id, node_ids, run_id = _seed_with_questions(session)
        persist_question(
            session, run=session.get(GenerationRun, run_id), node_id=node_ids[-1], manual_id=manual_id,
            generation_order=1, payload=_question("B"), raw_response={},
            question_type="ejercicio_nuevo", source_quote=CITA,
        )
        bundle = build_bundle(session, manual_id=manual_id)

    report = validate(bundle)
    assert report.ok, report.errors
    assert [q["generation_order"] for q in bundle["questions"]] == [0, 1]
```

En `explorer/tests/test_export_page.py`, en el `persist_question` de `_seed`, añade `source_quote=text,` (la variable `text` ya existe en esa función).

- [ ] **Step 2: Run to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_bundle_spec.py question_generator/tests/test_bundle_export.py -q`
Expected: FAIL (las preguntas v1 con dos por nodo dan error, falta `question_type` en el bundle exportado, `bundle_version` es 1).

- [ ] **Step 3: Implement**

En `bundle/spec.py`:

1. Primera línea del docstring: `"""Formato del bundle de contenido (v1 y v2).`
2. `BUNDLE_VERSION = 2` y `SUPPORTED_VERSIONS = frozenset({1, 2})`.
3. Después de `SERVED_STATUSES = …`, añade:

```python
#: Tipos de pregunta (v2).
QUESTION_TYPES = frozenset({"teoria", "ejercicio_libro", "ejercicio_nuevo"})
```

4. En `MAX_LEN`, añade `"source_quote": 2000,`.
5. Cambia `seen_questions: set[tuple[str, str]] = set()` por `seen_questions: set[tuple[str, Any]] = set()`.
6. En el bucle de preguntas de `validate`, sustituye desde `if q_run is not None and q_node is not None:` hasta `_text(report, question, "justification", where, limit_key="justification")` (ambos incluidos) por:

```python
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
```

En `bundle/build.py`: en el docstring de `build_bundle`, `v1` → `v2`; en el dict de cada pregunta, después de `"justification": question.justification,`, añade:

```python
                "question_type": question.question_type,
                "source_quote": question.source_quote,
```

En `CONTRATO-BUNDLE.md`:

1. Título: `# Contrato: bundle de contenido v2`.
2. En el ejemplo JSON: `"bundle_version": 1,` → `"bundle_version": 2,`; y en la pregunta, después de `"justification": "El artículo 142 establece …",`, añade las líneas `"question_type": "teoria",` y `"source_quote": "El artículo 142 establece que …",`.
3. Sustituye el párrafo **`questions`** de "Notas por bloque" por: `**\`questions\`** — cada una apunta a su corrida y a su nodo por \`ref\`, con sus 4 opciones ordenadas. Desde v2 trae \`question_type\` (\`teoria\`, \`ejercicio_libro\` o \`ejercicio_nuevo\`) y \`source_quote\` (la cita del texto en que se apoya), y un nodo puede tener varias preguntas en la misma corrida.`
4. §4, fila Pregunta: `| Pregunta | \`(run_ref, generation_order)\` | desde v2; espeja el índice único de Postgres. En v1 era \`(run_ref, node_ref)\` |`.
5. §5: al punto 3 añade `, \`source_quote\` ≤ 2000 (v2)` antes del punto final; sustituye el punto 5 por `5. Todo \`node_ref\` y \`run_ref\` de una pregunta existe en el bundle, y no hay dos preguntas con la misma identidad (§4): mismo \`(run_ref, generation_order)\` en v2, mismo \`(run_ref, node_ref)\` en v1.`; y añade `11. (v2) \`question_type\` ∈ \`teoria | ejercicio_libro | ejercicio_nuevo\` y \`source_quote\` no vacío.`
6. §7, antes de "Pendiente conocido", añade:

```markdown
### Historial

- **v2 (2026-09-23)** — generación por ventanas: la identidad de una pregunta pasa a
  `(run_ref, generation_order)`, así que un nodo puede tener varias preguntas por
  corrida; cada pregunta trae `question_type` y `source_quote` (obligatorios). El
  importador acepta v1 y v2. En Postgres: el índice único de `questions` cambia de
  (corrida, nodo) a (corrida, `generation_order`) y se añaden las dos columnas.
```

7. En "Pendiente conocido": `(run_ref, node_ref)` → `(run_ref, generation_order)`.

- [ ] **Step 4: Run to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests explorer/tests -q`
Expected: todo en verde.

- [ ] **Step 5: Commit**

```bash
git add question_generator/src/qgen/bundle CONTRATO-BUNDLE.md question_generator/tests/test_bundle_spec.py question_generator/tests/test_bundle_export.py explorer/tests/test_export_page.py
git commit -m "feat(bundle): contrato v2 con varias preguntas por nodo, tipo y cita

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 11: Explorador: tipo, cita y motivos

**Files:**
- Modify: `explorer/src/explorer/questions_access.py`
- Modify: `explorer/src/explorer/pages/6_❓_Preguntas.py`
- Test: `explorer/tests/test_questions_access.py`, `explorer/tests/test_export_page.py`

**Interfaces:**
- Consumes: columnas de Task 7 y `metadata_json["motivos"]` que escribe el pipeline (Task 9).
- Produces: `QuestionView.question_type: str = "teoria"`, `QuestionView.source_quote: str = ""`, `QuestionView.motivos: list[str] = []`; constante `TYPE_LABEL` en `explorer.questions_access`.

- [ ] **Step 1: Write the failing tests**

En `explorer/tests/test_questions_access.py`, en `_seed_questions_data`, añade al `persist_question` los argumentos:

```python
            question_type="ejercicio_nuevo",
            source_quote="Texto relevante del manual sobre disciplina.",
            metadata={"motivos": ["la verificación eligió B; la clave es A"]},
```

y añade al final:

```python
def test_la_pregunta_trae_su_tipo_su_cita_y_sus_motivos():
    st.cache_data.clear()
    manual_id, _, _, _ = _seed_questions_data()

    [q] = list_questions(manual_id)

    assert q.question_type == "ejercicio_nuevo"
    assert q.source_quote == "Texto relevante del manual sobre disciplina."
    assert q.motivos == ["la verificación eligió B; la clave es A"]
```

En `explorer/tests/test_export_page.py`, en el `persist_question` de `_seed`, añade `question_type="ejercicio_nuevo", metadata={"motivos": ["supera la dificultad del PDF"]},` y añade al final:

```python
def test_la_pregunta_muestra_su_tipo_y_sus_motivos():
    at = _open_page(_seed(run_status="succeeded"))

    assert any("Ejercicio nuevo" in c.value for c in at.caption)
    assert any("supera la dificultad del PDF" in w.value for w in at.warning)
```

- [ ] **Step 2: Run to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest explorer/tests -q`
Expected: FAIL (`QuestionView` no tiene `question_type`; la página no muestra el tipo).

- [ ] **Step 3: Implement**

En `questions_access.py`, después de `ROLE_LABEL`, añade:

```python
#: Tipo de pregunta (qgen v2).
TYPE_LABEL: dict[str, str] = {
    "teoria": "📘 Teoría",
    "ejercicio_libro": "✏️ Ejercicio del libro",
    "ejercicio_nuevo": "🆕 Ejercicio nuevo",
}
```

En `class QuestionView`, después de `node_page_start: int`, añade:

```python
    question_type: str = "teoria"
    source_quote: str = ""
    motivos: list[str] = Field(default_factory=list)
```

En `list_questions`, en el `QuestionView(...)`, después de `node_page_start=node.page_start,`, añade:

```python
                question_type=q.question_type,
                source_quote=q.source_quote,
                motivos=list((q.metadata_json or {}).get("motivos") or []),
```

En `pages/6_❓_Preguntas.py`: añade `TYPE_LABEL,` al import de `explorer.questions_access`; en `_render_question`, justo después de `st.markdown(f"**{question.question_text}**")`, añade:

```python
        st.caption(TYPE_LABEL.get(question.question_type, question.question_type))
        if question.motivos:
            st.warning("A revisar: " + "; ".join(question.motivos))
```

y justo después de `st.caption(f"💡 {question.justification}")`, añade:

```python
        if question.source_quote:
            with st.expander("Cita del texto"):
                st.markdown(f"> {question.source_quote}")
```

- [ ] **Step 4: Run to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest explorer/tests -q`
Expected: todo en verde. Si la lista de preguntas de la página filtrara por estado por defecto, la pregunta sembrada está en `pending`, que es un estado servido: debe aparecer.

- [ ] **Step 5: Commit**

```bash
git add explorer
git commit -m "feat(explorer): tipo, cita y motivos de revisión de cada pregunta

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 12: Verificación final y prueba real

**Files:**
- Modify (solo si la calibración lo pide): `question_generator/src/qgen/cost.py` (constantes de estimación)
- Modify: `graphify-out/` (regenerado)

- [ ] **Step 1: Suite completa**

Run: `.venv/Scripts/python.exe -m pytest etl question_generator explorer -q -p no:cacheprovider`
Expected: todo en verde (los avisos que ya había antes siguen; ningún fallo nuevo).

- [ ] **Step 2: Migrar la base real con copia de seguridad**

```bash
.venv/Scripts/python.exe -c "
import sqlite3
src = sqlite3.connect('data/manuals.sqlite'); dst = sqlite3.connect('data/manuals.antes-qgen-v2.sqlite')
src.backup(dst); dst.close(); print('copia hecha')
from qgen.db.migration import init_question_tables; init_question_tables(); print('migrada')
"
```

Expected: `copia hecha` y `migrada`; `PRAGMA table_info(questions)` muestra `question_type`, `source_quote`, `window_key`.

- [ ] **Step 3: Estimaciones (sin llamar a Gemini)**

Run: `.venv/Scripts/qgen-generate.exe 12 --dry-run` (Cálculo) y `.venv/Scripts/qgen-generate.exe 2 --dry-run` (Operaciones Militares).
Expected: tablas con "Windows to process" ≈ 28 y ≈ 160, y verificaciones > 0 solo en Cálculo.

- [ ] **Step 4: Prueba real con el usuario (gasta cuota de Gemini: pedir confirmación antes)**

Run: `.venv/Scripts/qgen-generate.exe 12 --limit 2` y `.venv/Scripts/qgen-generate.exe 2 --limit 2`.
Revisar en el explorador (página de preguntas) con el usuario: tipos, citas, motivos de revisión y calidad. Anotar por ventana: preguntas guardadas, caracteres de la ventana, tokens de salida y ejercicios nuevos.

- [ ] **Step 5: Calibrar la estimación** — con lo anotado, ajusta en `cost.py` `CHARS_PER_QUESTION` (caracteres de ventana / preguntas), `OUTPUT_TOKENS_PER_QUESTION` (tokens de salida / preguntas) y `CHARS_PER_NEW_EXERCISE`; ajusta `test_cost.py` si cambian los números esperados; corre `question_generator/tests`.

- [ ] **Step 6: Grafo y commit**

```bash
PYTHONHASHSEED=0 graphify update .
git add question_generator/src/qgen/cost.py question_generator/tests/test_cost.py graphify-out
git commit -m "chore(qgen): estimación calibrada con la primera corrida real y grafo al día

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 7: Avisar al usuario de lo que toca en la webapp** (spec §11): copiar `bundle/spec.py`, cambiar en Postgres el índice único de preguntas a (corrida, `generation_order`), añadir `question_type` y `source_quote`, y actualizar `docs/06-contrato-bundle-de-contenido.md` con los cambios de `CONTRATO-BUNDLE.md`.
