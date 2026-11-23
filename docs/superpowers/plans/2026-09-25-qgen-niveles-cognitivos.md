# Niveles cognitivos en qgen (v3) — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que cada pregunta generada tenga un nivel cognitivo (conocimiento, comprensión, análisis, aplicación), en proporción 55/15/15/15, revisado por nivel, clasificado en la revisión con Claude y exportado a la webapp en el bundle v3.

**Architecture:** Un campo nuevo `nivel` en la respuesta por ventana (junto al `tipo` actual) que viaja a la columna `questions.cognitive_level` y al bundle v3. Las definiciones de los niveles viven en un solo módulo (`qgen/prompts/niveles.py`) que usan el prompt de generación y la rúbrica de revisión. La revisión automática (`review()`) cambia de regla según el nivel; la revisión con Claude clasifica y reclasifica.

**Tech Stack:** Python 3.14, workspace uv (`etl`, `question_generator`, `explorer`), SQLAlchemy 2 + SQLite, pydantic 2, typer, rich, Streamlit, openpyxl, pytest.

**Spec:** `docs/superpowers/specs/2026-09-25-qgen-niveles-cognitivos-design.md`

## Global Constraints

- Valores del nivel (datos, sin acentos): `conocimiento`, `comprension`, `analisis`, `aplicacion`. Etiquetas de pantalla: "Conocimiento", "Comprensión", "Análisis", "Aplicación".
- Proporción meta: 55/15/15/15 (conocimiento/comprensión/análisis/aplicación); todas las de conocimiento posibles como base K; otros niveles `round(K × 15 / 55)` cada uno, mínimo 1 si `K ≥ 3`.
- `MAX_PREGUNTAS_POR_VENTANA = 45` (cuenta todas, ejercicios incluidos).
- Umbral de "clave literal" en comprensión/análisis/aplicación: 6 palabras o más.
- `SYSTEM_VERSION = "2026-09-25.v7"`; `BUNDLE_VERSION = 3`; `SUPPORTED_VERSIONS = {1, 2, 3}`; `CHARS_PER_QUESTION = 190`.
- Los ejercicios (`ejercicio_libro`, `ejercicio_nuevo`) siempre son `aplicacion`.
- Enunciados directos en la familia civil: nada de "según el texto".
- Pruebas: `.venv/Scripts/python.exe -m pytest <ruta> -q` desde la raíz del repo.
- **Nunca `uv sync` a secas** (quita paquetes instalados a mano y OneDrive deja desinstalaciones a medias). Para el lockfile: `uv lock`.
- Mensajes de commit en español, terminando en `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **Esquema estructurado de Gemini con el enum `nivel`:** `WindowResponse.model_json_schema()` debe declarar los cuatro valores; si no, Gemini devuelve niveles libres y todo se descarta. (Prueba en Task 1.)
2. **xlsx con filas vacías o incompletas:** una fila sin pregunta se salta; una fila con menos de 4 respuestas es un error que nombra hoja y fila, no un ejemplo con 2 opciones. (Prueba en Task 4.)
3. **Veredictos viejos sin `nivel` en `revision/veredictos/`** (el Taller tiene 10 de la ronda anterior): el lote se reporta inválido y no aplica nada; no rompe la importación. (Prueba en Task 6.)
4. **Base real ya existente:** la migración agrega `cognitive_level` a `questions` y a `reference_questions` sin perder filas y es idempotente. (Prueba en Task 3.)
5. **Filtro "sin clasificar" en el explorador** con preguntas de nivel nulo (las 245 del Taller): debe usar `IS NULL`, no comparar con una cadena. (Prueba en Task 8.)

---

### Task 1: Niveles y esquema de la respuesta

**Files:**
- Create: `question_generator/src/qgen/prompts/niveles.py`
- Modify: `question_generator/src/qgen/prompts/schemas.py` (`MAX_PREGUNTAS_POR_VENTANA`, `WindowQuestion`)
- Test: `question_generator/tests/test_niveles.py` (nuevo), `question_generator/tests/test_schemas.py`
- Modify (fixtures): `question_generator/tests/test_checks.py`, `test_pipeline.py`, `test_claude_code.py`, `test_claude_review.py`

**Interfaces:**
- Produces: `qgen.prompts.niveles.Nivel` (StrEnum: `CONOCIMIENTO="conocimiento"`, `COMPRENSION="comprension"`, `ANALISIS="analisis"`, `APLICACION="aplicacion"`), `ORDEN: tuple[Nivel, ...]`, `NIVEL_LABEL: dict[str, str]`, `PROPORCION: dict[Nivel, int]`, `DEFINICIONES: str`, `falta_algun_nivel(conteo: Mapping[str, int]) -> bool`. `WindowQuestion.nivel: Nivel`. `MAX_PREGUNTAS_POR_VENTANA = 45`.

- [ ] **Step 1: Write the failing tests**

`question_generator/tests/test_niveles.py`:

```python
"""Niveles cognitivos: valores, proporción y definiciones compartidas."""

from qgen.prompts.niveles import DEFINICIONES, NIVEL_LABEL, ORDEN, PROPORCION, Nivel, falta_algun_nivel


def test_cuatro_niveles_en_el_orden_del_usuario():
    assert [n.value for n in ORDEN] == ["conocimiento", "comprension", "aplicacion", "analisis"]
    assert NIVEL_LABEL["comprension"] == "Comprensión" and NIVEL_LABEL["analisis"] == "Análisis"


def test_la_proporcion_es_55_15_15_15():
    assert PROPORCION == {Nivel.CONOCIMIENTO: 55, Nivel.COMPRENSION: 15, Nivel.ANALISIS: 15, Nivel.APLICACION: 15}


def test_una_ventana_con_3_de_conocimiento_debe_traer_los_otros_niveles():
    completo = {"conocimiento": 3, "comprension": 1, "analisis": 1, "aplicacion": 1}
    assert not falta_algun_nivel(completo)
    assert falta_algun_nivel({**completo, "analisis": 0})
    assert falta_algun_nivel({"conocimiento": 5})
    assert not falta_algun_nivel({"conocimiento": 2})  # con menos de 3 son opcionales


def test_las_definiciones_traen_clave_confusa_y_filtro_de_cada_nivel():
    for marca in ("copia LITERAL", "PARÁFRASIS", "CASO INVENTADO", "CONCLUSIÓN INFERIDA", "Filtro anti-falsos positivos"):
        assert marca in DEFINICIONES
    assert "¿Cómo se describe el proceso de" in DEFINICIONES
    assert "¿Cómo describe el texto" not in DEFINICIONES
```

En `question_generator/tests/test_schemas.py`, agregar `"nivel": "conocimiento",` al diccionario de `_window_item` (después de `"tipo": "teoria",`) y estas pruebas (con `import pytest`, `from pydantic import ValidationError`, `from qgen.prompts.niveles import Nivel` y `MAX_PREGUNTAS_POR_VENTANA` en los imports si faltan):

```python
def test_la_pregunta_de_ventana_exige_un_nivel_conocido():
    sin_nivel = _window_item()
    sin_nivel.pop("nivel")
    with pytest.raises(ValidationError):
        WindowQuestion.model_validate(sin_nivel)
    with pytest.raises(ValidationError):
        WindowQuestion.model_validate(_window_item(nivel="memoria"))


def test_un_ejercicio_siempre_es_de_aplicacion():
    for tipo in ("ejercicio_libro", "ejercicio_nuevo"):
        q = WindowQuestion.model_validate(_window_item(tipo=tipo, nivel="conocimiento"))
        assert q.nivel == Nivel.APLICACION


def test_el_esquema_para_gemini_declara_los_cuatro_niveles():
    esquema = WindowResponse.model_json_schema()
    assert set(esquema["$defs"]["Nivel"]["enum"]) == {"conocimiento", "comprension", "analisis", "aplicacion"}


def test_el_tope_por_ventana_es_45():
    assert MAX_PREGUNTAS_POR_VENTANA == 45
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_niveles.py question_generator/tests/test_schemas.py -q`
Expected: FAIL (`ModuleNotFoundError: qgen.prompts.niveles`).

- [ ] **Step 3: Create `qgen/prompts/niveles.py`**

```python
"""Niveles cognitivos de las preguntas (spec de niveles, §4).

Las definiciones son del usuario. Las usan el prompt de generación
(`prompts.families`) y la rúbrica de revisión (`claude_review`): viven aquí para
que nunca se desincronicen.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum


class Nivel(StrEnum):
    CONOCIMIENTO = "conocimiento"
    COMPRENSION = "comprension"
    ANALISIS = "analisis"
    APLICACION = "aplicacion"


#: El orden del usuario (aplicación antes que análisis).
ORDEN: tuple[Nivel, ...] = (Nivel.CONOCIMIENTO, Nivel.COMPRENSION, Nivel.APLICACION, Nivel.ANALISIS)

NIVEL_LABEL: dict[str, str] = {
    "conocimiento": "Conocimiento",
    "comprension": "Comprensión",
    "analisis": "Análisis",
    "aplicacion": "Aplicación",
}

#: Proporción meta por ventana, en porcentaje.
PROPORCION: dict[Nivel, int] = {
    Nivel.CONOCIMIENTO: 55,
    Nivel.COMPRENSION: 15,
    Nivel.ANALISIS: 15,
    Nivel.APLICACION: 15,
}

_OTROS = (Nivel.COMPRENSION, Nivel.ANALISIS, Nivel.APLICACION)


def falta_algun_nivel(conteo: Mapping[str, int]) -> bool:
    """Con 3 o más de conocimiento, la ventana debe traer al menos una de cada otro nivel."""
    if conteo.get(Nivel.CONOCIMIENTO.value, 0) < 3:
        return False
    return any(conteo.get(n.value, 0) == 0 for n in _OTROS)


DEFINICIONES = """\
1. "conocimiento" (Recordar)
- Definición cognitiva: evocación directa de datos, hechos, fechas, clasificaciones o definiciones explícitas.
- Sintaxis de la pregunta: directa. "¿Qué?", "¿Quién?", "¿Cuándo?", "¿Cuál es la definición de…?"
- Clave ("correct"): copia LITERAL y exacta del texto.
- "confusa": la misma oración literal, pero cambiando un nombre propio, una cifra, un elemento de la lista o una unidad de medida.
- Filtro anti-falsos positivos: si la pregunta requiere que el alumno explique con sus palabras, deduzca o analice un caso, no es conocimiento. Aquí solo se escanea y recupera información textual.

2. "comprension" (Entender / Explicar / Traducir)
- Definición cognitiva: demostrar entendimiento del significado explícito de una idea o proceso. No pide un dato aislado, sino reformular, explicar o resumir un fenómeno manteniendo la fidelidad conceptual.
- Sintaxis de la pregunta: "¿Cómo se describe el proceso de…?", "¿Qué significa la expresión…?", "En otras palabras, el concepto X se refiere a…"
- Clave ("correct"): una PARÁFRASIS precisa. Dice exactamente lo mismo que el texto, pero con otras palabras explicativas.
- "confusa": alteración del núcleo explicativo. Se invierte el verbo principal, el adjetivo descriptivo o la dirección del proceso (cambiar "aumenta" por "disminuye", "cóncavo" por "convexo"). Suena lógico pero es conceptualmente falso.
- Filtro anti-falsos positivos: si la pregunta se responde copiando literalmente una definición del texto, es de conocimiento. Para que sea comprensión debe obligar a identificar la traducción o explicación del concepto, no su memorización.

3. "aplicacion" (Usar reglas en casos nuevos)
- Definición cognitiva: uso de un método, regla, fórmula o criterio explícito del texto para resolver una situación inédita.
- Sintaxis de la pregunta: plantea un CASO INVENTADO (un equipo hipotético, una comisión nueva, un comandante en una situación específica). Ej.: "El Teniente X se encuentra en la situación Y. ¿Qué procedimiento debe aplicar?"
- Clave ("correct"): la solución correcta o el procedimiento exacto que dicta el texto, aplicado al caso inventado.
- "confusa": una solución que aplica la regla al revés, usa la herramienta equivocada para ese caso o aplica la regla de una excepción en lugar de la regla general.
- Filtro anti-falsos positivos: si la pregunta dice "¿Qué pasa cuando se aplica la regla X?", es de conocimiento o comprensión. Para que sea aplicación es OBLIGATORIO inventar un escenario hipotético que no está en el texto, pero cuya solución se extrae de las reglas del texto.

4. "analisis" (Deducir / Inferir / Relacionar)
- Definición cognitiva: extraer conclusiones, comparar datos o inferir información que no está escrita explícitamente, pero que es lógicamente innegable al sumar los datos del texto.
- Sintaxis de la pregunta: "¿Qué se puede deducir sobre…?", "Al comparar X con Y, es correcto afirmar que…", "¿Qué conclusión subyacente establece el autor sobre…?"
- Clave ("correct"): una CONCLUSIÓN INFERIDA. Si el texto dice "A tiene 10 metros y B tiene 50 metros", la clave dice: "El elemento A es cinco veces menor que el elemento B".
- "confusa": una deducción lógicamente inválida, una falsa correlación causa-efecto o la inversión de las variables ("B es cinco veces menor que A").
- Filtro anti-falsos positivos: si preguntas "¿Por qué ocurrió X?" y la respuesta empieza con un "Porque…" que está literal en el texto, es de comprensión. Para que sea análisis, la respuesta NO DEBE estar escrita textualmente: es una conclusión matemática, lógica o comparativa que el alumno construye cruzando datos del pasaje citado.

Los dos "distractor": en "conocimiento", otros datos reales del mismo texto; en los otros niveles, respuestas plausibles del mismo tema que fallan de otra manera que la "confusa".
"""
```

- [ ] **Step 4: Add `nivel` to `WindowQuestion` and raise the cap**

En `question_generator/src/qgen/prompts/schemas.py`:
- Agregar el import `from qgen.prompts.niveles import Nivel` junto a los demás.
- Cambiar `MAX_PREGUNTAS_POR_VENTANA = 30` por `MAX_PREGUNTAS_POR_VENTANA = 45`.
- En `WindowQuestion`, después de `tipo: QuestionType`, agregar `nivel: Nivel`.
- Al final de `WindowQuestion._check`, antes de `return self`, agregar:

```python
        # Un ejercicio del libro o nuevo siempre es de aplicación (spec de niveles §5).
        if self.tipo != QuestionType.TEORIA and self.nivel != Nivel.APLICACION:
            self.nivel = Nivel.APLICACION
```

- [ ] **Step 5: Add `nivel` to the test fixtures**

Agregar `"nivel": "conocimiento",` justo después de `"tipo": tipo,` (o `"tipo": "teoria",`) en el diccionario que devuelve `_item` en:
`question_generator/tests/test_checks.py`, `test_pipeline.py`, `test_claude_code.py`, `test_claude_review.py`.
En `test_checks.py`, `test_pipeline.py` y `test_claude_code.py`, `_item` gana además el parámetro `nivel="conocimiento"` (keyword-only, junto a `tipo`) y el diccionario usa `"nivel": nivel`.

- [ ] **Step 6: Run the whole qgen suite**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests -q`
Expected: PASS (todas, incluidas las nuevas).

- [ ] **Step 7: Commit**

```bash
git add question_generator/src/qgen/prompts/niveles.py question_generator/src/qgen/prompts/schemas.py question_generator/tests
git commit -m "feat(qgen): nivel cognitivo en la respuesta por ventana

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Revisión automática por nivel

**Files:**
- Modify: `question_generator/src/qgen/validation/checks.py` (`review`, nuevo `_copiado`, constante)
- Test: `question_generator/tests/test_checks.py`

**Interfaces:**
- Consumes: `WindowQuestion.nivel`, `Nivel` (Task 1).
- Produces: motivos exactos `"cita no encontrada"`, `"respuesta parafraseada"`, `"la clave es literal: por su forma es conocimiento"`, `"el caso no es inventado"`; constante `PALABRAS_MINIMAS_LITERAL = 6`.

- [ ] **Step 1: Write the failing tests**

Agregar a `question_generator/tests/test_checks.py`:

```python
COSTA = (
    "La costa avanza hacia el norte por efecto de depósitos aluviales formados por "
    "los ríos Grijalva y Usumacinta, unidos."
)


def _nivel(nivel, pregunta="¿Cómo avanza la costa?", correcta="por la acumulación de sedimentos de dos ríos",
           cita=COSTA):
    return _q(pregunta, nivel=nivel, correcta=correcta, cita=cita)


def test_en_conocimiento_la_clave_debe_ser_literal():
    assert review(_nivel("conocimiento", correcta="hacia el norte"), COSTA).motivos == ()
    assert review(_nivel("conocimiento"), COSTA).motivos == ("respuesta parafraseada",)


def test_en_comprension_una_clave_literal_larga_delata_conocimiento():
    literal = "por efecto de depósitos aluviales formados por los ríos Grijalva y Usumacinta"
    assert review(_nivel("comprension", correcta=literal), COSTA).motivos == (
        "la clave es literal: por su forma es conocimiento",
    )
    assert review(_nivel("comprension"), COSTA).motivos == ()  # paráfrasis


def test_una_clave_literal_corta_no_delata_nada():
    assert review(_nivel("analisis", correcta="hacia el norte"), COSTA).motivos == ()


def test_en_aplicacion_el_caso_debe_ser_inventado():
    copiado = "La costa avanza hacia el norte por efecto de depósitos aluviales. ¿Qué ocurre?"
    inventado = "Un equipo de geógrafos mide la línea costera de Tabasco durante diez años. ¿Qué cambio registrará?"
    assert review(_nivel("aplicacion", pregunta=copiado), COSTA).motivos == ("el caso no es inventado",)
    assert review(_nivel("aplicacion", pregunta=inventado), COSTA).motivos == ()


def test_la_cita_debe_ser_literal_en_todos_los_niveles():
    for nivel in ("conocimiento", "comprension", "analisis", "aplicacion"):
        motivos = review(_nivel(nivel, correcta="hacia el norte", cita="una cita inventada"), COSTA).motivos
        assert "cita no encontrada" in motivos
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_checks.py -q`
Expected: FAIL en las pruebas de comprensión, análisis y aplicación.

- [ ] **Step 3: Implement**

En `question_generator/src/qgen/validation/checks.py`:
- Agregar `from qgen.prompts.niveles import Nivel` a los imports.
- Debajo de `SIMILITUD_DUPLICADO = 0.90`, agregar:

```python
#: Una clave literal más corta que esto aparece en el texto por coincidencia (spec de niveles §7).
PALABRAS_MINIMAS_LITERAL = 6
```

- Reemplazar el bloque `if question.tipo == QuestionType.TEORIA:` de `review` por:

```python
    if question.tipo == QuestionType.TEORIA:
        motivos = []
        if not _literal(question.cita, window_text):
            motivos.append("cita no encontrada")
        if question.nivel == Nivel.CONOCIMIENTO:
            if not _literal(correcta, window_text):
                motivos.append("respuesta parafraseada")
        else:
            if len(correcta.split()) >= PALABRAS_MINIMAS_LITERAL and _literal(correcta, window_text):
                motivos.append("la clave es literal: por su forma es conocimiento")
            if question.nivel == Nivel.APLICACION and _copiado(question.pregunta, window_text):
                motivos.append("el caso no es inventado")
        return Verdict.from_motivos(motivos)
```

- Debajo de `_literal`, agregar:

```python
def _copiado(enunciado: str, texto: str) -> bool:
    """¿Más de la mitad del enunciado está copiada literal del texto? (caso no inventado)."""
    a, b = norm_text(enunciado), norm_text(texto)
    if not a:
        return False
    bloque = difflib.SequenceMatcher(None, a, b, autojunk=False).find_longest_match(0, len(a), 0, len(b))
    return bloque.size > len(a) / 2
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add question_generator/src/qgen/validation/checks.py question_generator/tests/test_checks.py
git commit -m "feat(qgen): revisión automática según el nivel cognitivo

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Columnas, guardado y conteo por nivel

**Files:**
- Modify: `question_generator/src/qgen/db/migration.py`
- Modify: `question_generator/src/qgen/models/schema.py` (`Question`), `question_generator/src/qgen/models/reference_schema.py` (`ReferenceQuestion`)
- Modify: `question_generator/src/qgen/db/persistence.py` (`persist_question`)
- Modify: `question_generator/src/qgen/pipeline.py` (`RunSummary`, `_run_immediate`)
- Modify: `question_generator/src/qgen/cli/generate.py` (`_print_summary`)
- Test: `question_generator/tests/test_qgen_persistence.py`, `question_generator/tests/test_pipeline.py`

**Interfaces:**
- Consumes: `Nivel`, `ORDEN`, `NIVEL_LABEL`, `PROPORCION`, `falta_algun_nivel` (Task 1).
- Produces: `Question.cognitive_level: str | None`; `ReferenceQuestion.cognitive_level: str | None`; `persist_question(..., cognitive_level: str | None = None)`; `RunSummary.niveles: dict[str, int]`, `RunSummary.ventanas_sin_algun_nivel: list[str]`; `GenerationRun.metadata_json["niveles"] = {"total": {...}, "ventanas": {key: {...}}, "sin_algun_nivel": [...]}`.

- [ ] **Step 1: Write the failing tests**

En `question_generator/tests/test_qgen_persistence.py` agregar (con `from sqlalchemy import inspect, text` y `from etl.db.session import get_engine` si faltan):

```python
def test_la_migracion_agrega_el_nivel_a_preguntas_y_referencias_sin_perder_filas():
    init_question_tables()
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO reference_questions (profile, question_text, created_at, metadata_json) "
                          "VALUES ('global', '¿Qué?', '2026-09-25', '{}')"))
        conn.execute(text("ALTER TABLE reference_questions DROP COLUMN cognitive_level"))
        conn.execute(text("ALTER TABLE questions DROP COLUMN cognitive_level"))
    init_question_tables()
    init_question_tables()  # idempotente
    for tabla in ("questions", "reference_questions"):
        assert "cognitive_level" in {c["name"] for c in inspect(get_engine()).get_columns(tabla)}
    with engine.begin() as conn:
        assert conn.execute(text("SELECT count(*) FROM reference_questions")).scalar_one() == 1
```

En `question_generator/tests/test_pipeline.py` agregar:

```python
def test_cada_pregunta_guarda_su_nivel_y_la_corrida_cuenta_los_niveles(monkeypatch):
    manual_id = _seed(1)
    fake = FakeGemini(monkeypatch)
    fake.window = lambda message: WindowOutcome(items=[
        _item(),
        _item("¿Cómo se explica la guerra?", nivel="comprension", correcta="choque violento de grupos", prefijo="C"),
    ])

    summary = _run(manual_id)

    with session_scope() as session:
        niveles = sorted(session.execute(select(Question.cognitive_level)).scalars())
        (run,) = session.execute(select(GenerationRun)).scalars().all()
        meta = run.metadata_json["niveles"]
    assert niveles == ["comprension", "conocimiento"]
    assert meta["total"] == {"conocimiento": 1, "comprension": 1}
    assert list(meta["ventanas"].values()) == [{"conocimiento": 1, "comprension": 1}]
    assert meta["sin_algun_nivel"] == []
    assert summary.niveles == {"conocimiento": 1, "comprension": 1}


def test_una_ventana_con_3_de_conocimiento_y_sin_otros_niveles_se_reporta(monkeypatch):
    manual_id = _seed(1)
    fake = FakeGemini(monkeypatch)
    fake.window = lambda message: WindowOutcome(items=[
        _item("¿Qué es la guerra?"),
        _item("¿Entre quiénes ocurre?", correcta="entre sociedades", prefijo="B"),
        _item("¿Cómo luchan?", correcta="violentamente", prefijo="C"),
    ])

    summary = _run(manual_id)

    assert len(summary.ventanas_sin_algun_nivel) == 1
```

(Los `_item` de `test_pipeline.py` usan la cita `TEXTO`; "choque violento de grupos" es una paráfrasis corta, así que no genera motivos.)

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_qgen_persistence.py question_generator/tests/test_pipeline.py -q`
Expected: FAIL (`no such column: cognitive_level` / `AttributeError: niveles`).

- [ ] **Step 3: Migration**

Reemplazar en `question_generator/src/qgen/db/migration.py` el diccionario `_QUESTION_COLUMNS` y la función `_add_missing_columns` por:

```python
# Columnas que llegaron después de crear cada tabla (qgen v2 y niveles cognitivos).
_NEW_COLUMNS: dict[str, dict[str, str]] = {
    "questions": {
        "question_type": "VARCHAR(32) NOT NULL DEFAULT 'teoria'",
        "source_quote": "TEXT NOT NULL DEFAULT ''",
        "window_key": "VARCHAR(64)",
        "cognitive_level": "VARCHAR(16)",
    },
    "reference_questions": {
        "cognitive_level": "VARCHAR(16)",
    },
}
```

```python
def _add_missing_columns(engine) -> None:
    inspector = inspect(engine)
    with engine.begin() as conn:
        for table, columns in _NEW_COLUMNS.items():
            existing = {c["name"] for c in inspector.get_columns(table)}
            for name, ddl in columns.items():
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_questions_window_key ON questions (window_key)"))
```

- [ ] **Step 4: Models and persistence**

En `question_generator/src/qgen/models/schema.py`, en `Question`, debajo de `window_key`:

```python
    # Niveles cognitivos (spec de niveles §5): NULL = sin clasificar.
    cognitive_level: Mapped[str | None] = mapped_column(String(16), nullable=True)
```

En `question_generator/src/qgen/models/reference_schema.py`, en `ReferenceQuestion`, debajo de `source_tag`:

```python
    cognitive_level: Mapped[str | None] = mapped_column(String(16), nullable=True)
```

En `question_generator/src/qgen/db/persistence.py`, `persist_question` gana el parámetro `cognitive_level: str | None = None` (después de `window_key`) y el constructor `Question(...)` recibe `cognitive_level=cognitive_level,`.

- [ ] **Step 5: Pipeline**

En `question_generator/src/qgen/pipeline.py`:
- Import: `from qgen.prompts.niveles import falta_algun_nivel`.
- En `RunSummary`, al final:

```python
    niveles: dict[str, int] = field(default_factory=dict)
    ventanas_sin_algun_nivel: list[str] = field(default_factory=list)
```

- En `_run_immediate`, junto a `conteo: Counter[str] = Counter()`:

```python
    por_nivel: Counter[str] = Counter()
    niveles_por_ventana: dict[str, dict[str, int]] = {}
```

- En `finalize`, dentro de `run.metadata_json = {...}`, después de `"preguntas": dict(conteo),`:

```python
            "niveles": {
                "total": dict(por_nivel),
                "ventanas": dict(niveles_por_ventana),
                "sin_algun_nivel": [k for k, c in niveles_por_ventana.items() if falta_algun_nivel(c)],
            },
```

- En el bucle principal, justo antes de `for accepted in result.accepted:` agregar `nivel_ventana: Counter[str] = Counter()`; en la llamada a `persist_question` agregar `cognitive_level=q.nivel.value,`; después de `conteo[f"{q.tipo.value}/{accepted.verdict.status}"] += 1` agregar:

```python
                nivel_ventana[q.nivel.value] += 1
                por_nivel[q.nivel.value] += 1
```

  y después de `ventanas[key] = "ok"`: `niveles_por_ventana[key] = dict(nivel_ventana)`.
- En el `return RunSummary(...)` final agregar:

```python
        niveles=dict(por_nivel),
        ventanas_sin_algun_nivel=[k for k, c in niveles_por_ventana.items() if falta_algun_nivel(c)],
```

- [ ] **Step 6: CLI summary**

En `question_generator/src/qgen/cli/generate.py`:
- Import: `from qgen.prompts.niveles import NIVEL_LABEL, ORDEN, PROPORCION`.
- Al final de `_print_summary`, después de `console.print(table)`: `_print_niveles(summary)`.
- Nueva función:

```python
def _print_niveles(summary) -> None:
    """Proporción real por nivel contra la meta (spec de niveles §6)."""
    niveles = getattr(summary, "niveles", None) or {}
    total = sum(niveles.values())
    if not total:
        return
    table = Table(title="Proporción por nivel")
    for col in ("Nivel", "Preguntas", "Real", "Meta"):
        table.add_column(col, justify="left" if col == "Nivel" else "right")
    for nivel in ORDEN:
        n = niveles.get(nivel.value, 0)
        table.add_row(NIVEL_LABEL[nivel.value], str(n), f"{100 * n / total:.0f}%", f"{PROPORCION[nivel]}%")
    console.print(table)
    if summary.ventanas_sin_algun_nivel:
        console.print(f"[yellow]Ventanas sin algún nivel: {', '.join(summary.ventanas_sin_algun_nivel)}[/]")
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests explorer/tests -q`
Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add question_generator/src/qgen question_generator/tests
git commit -m "feat(qgen): guardar el nivel cognitivo y contar la proporción por corrida

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Ejemplos por nivel (importador xlsx y repositorio)

**Files:**
- Modify: `question_generator/src/qgen/reference/importer.py`
- Modify: `question_generator/src/qgen/reference/repository.py`
- Modify: `question_generator/src/qgen/cli/import_examples.py` (texto de ayuda)
- Modify: `question_generator/pyproject.toml` (dependencia `openpyxl`), `uv.lock`
- Test: `question_generator/tests/test_reference_importer.py`

**Interfaces:**
- Consumes: `Nivel`, `ORDEN` (Task 1); `ReferenceQuestion.cognitive_level` (Task 3).
- Produces: `limpiar_ejemplo(texto: str) -> str`; `load_reference_file(path)` acepta `.xlsx` y devuelve dicts con `"nivel"`; `QuestionExemplarInput.nivel: str | None`; `get_level_exemplars(session, *, profile: str, manual_code: str | None) -> list[dict]` (un dict por nivel con claves `id`, `question_text`, `profile`, `manual_code`, `justification`, `nivel`, `options`).

- [ ] **Step 1: Write the failing tests**

Agregar a `question_generator/tests/test_reference_importer.py` (imports: `import openpyxl`, `import pytest`, `from qgen.reference.importer import limpiar_ejemplo`, `from qgen.reference.repository import get_level_exemplars`):

```python
def _xlsx(tmp_path, hojas: dict[str, list[list]]):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for nombre, filas in hojas.items():
        ws = wb.create_sheet(nombre)
        for fila in filas:
            ws.append(fila)
    ruta = tmp_path / "ejemplos.xlsx"
    wb.save(ruta)
    return ruta


ENCABEZADO = ["Pregunta", "Respuesta correcta", "Respuesta similar", "Respuesta incorrecta", "Respuesta incorrecta"]


def test_el_xlsx_da_un_ejemplo_por_fila_con_el_nivel_de_su_hoja(tmp_path):
    ruta = _xlsx(tmp_path, {
        "Conocimiento": [[None, *ENCABEZADO], [None, "Según el texto, ¿qué es A?", "A1", "A2", "A3", "A4"]],
        "Aplicacion": [ENCABEZADO, ["Un equipo mide X[cite: 1]. ¿Qué hace?", "B1 [cite: 1]", "B2", "B3", "B4"], [None] * 5],
    })

    items = load_reference_file(ruta)

    assert [(i["nivel"], i["question"]) for i in items] == [
        ("conocimiento", "¿Qué es A?"),
        ("aplicacion", "Un equipo mide X. ¿Qué hace?"),
    ]
    assert [o["role"] for o in items[1]["options"]] == ["correct", "confusa", "distractor", "distractor"]
    assert items[1]["options"][0]["text"] == "B1"


def test_una_hoja_que_no_es_un_nivel_se_rechaza(tmp_path):
    ruta = _xlsx(tmp_path, {"Resumen": [ENCABEZADO]})
    with pytest.raises(ValueError, match="Resumen"):
        load_reference_file(ruta)


def test_una_fila_con_menos_de_cuatro_respuestas_se_rechaza_con_hoja_y_fila(tmp_path):
    ruta = _xlsx(tmp_path, {"Analisis": [ENCABEZADO, ["¿Qué se deduce?", "C1", "C2"]]})
    with pytest.raises(ValueError, match="Analisis.*fila 2"):
        load_reference_file(ruta)


@pytest.mark.parametrize("sucio, limpio", [
    ("De acuerdo con la información del texto, ¿cuáles son las coordenadas?", "¿Cuáles son las coordenadas?"),
    ("A partir del texto, ¿cómo se explica el avance?", "¿Cómo se explica el avance?"),
    ("¿Cómo se establecieron los límites tras 1848, según el texto?", "¿Cómo se establecieron los límites tras 1848?"),
    ("Trazar la línea media del río[cite: 1].", "Trazar la línea media del río."),
])
def test_limpiar_ejemplo(sucio, limpio):
    assert limpiar_ejemplo(sucio) == limpio


def test_el_ejemplo_importado_guarda_su_nivel_y_se_elige_uno_por_nivel_con_prioridad():
    init_db()
    init_question_tables()
    def ej(pregunta, nivel, **extra):
        return {"question": pregunta, "nivel": nivel, **extra,
                "options": [{"text": f"{pregunta} {i}", "role": r} for i, r in
                            enumerate(("correct", "confusa", "distractor", "distractor"))]}
    with session_scope() as session:
        import_reference_questions(session, [
            ej("global conocimiento", "conocimiento"),
            ej("global análisis", "analisis"),
            ej("perfil conocimiento", "conocimiento", profile="historia_universal"),
            ej("manual conocimiento", "conocimiento", manual_code="HU"),
        ])
        elegidos = get_level_exemplars(session, profile="historia_universal", manual_code="HU")
    assert [(e["nivel"], e["question_text"]) for e in elegidos] == [
        ("conocimiento", "manual conocimiento"),
        ("analisis", "global análisis"),
    ]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_reference_importer.py -q`
Expected: FAIL (`ImportError: limpiar_ejemplo` / `get_level_exemplars`).

- [ ] **Step 3: Declare `openpyxl`**

En `question_generator/pyproject.toml`, agregar `"openpyxl>=3.1",` a `dependencies` (ya está instalado como dependencia transitiva, versión 3.1.5). Luego:

Run: `uv lock`
Expected: el lockfile solo agrega la arista `question-generator → openpyxl`. **No correr `uv sync`.**

- [ ] **Step 4: Importer**

En `question_generator/src/qgen/reference/importer.py`:
- Imports: `import re`, `import unicodedata`, `from pydantic import field_validator`, `from qgen.prompts.niveles import Nivel`.
- En `QuestionExemplarInput` agregar:

```python
    nivel: str | None = None

    @field_validator("nivel")
    @classmethod
    def _nivel_conocido(cls, value: str | None) -> str | None:
        if value is not None and value not in {n.value for n in Nivel}:
            raise ValueError(f"nivel {value!r} desconocido")
        return value
```

- En `import_reference_questions`, el constructor `ReferenceQuestion(...)` recibe `cognitive_level=input_obj.nivel,`.
- En `load_reference_file`, antes del `else:` final: `elif suffix == ".xlsx": return _load_xlsx(path)`; y el mensaje del error pasa a `"Use .json, .jsonl, .csv o .xlsx"`.
- Nuevas funciones al final del módulo:

```python
_ROLES_XLSX = ("correct", "confusa", "distractor", "distractor")
_PREFIJOS = ("de acuerdo con la información del texto,", "según el texto,", "a partir del texto,")
_CITA = re.compile(r"\s*\[cite:[^\]]*\]")
_SEGUN_AL_FINAL = re.compile(r",\s*según el texto(?=\s*\?)", re.IGNORECASE)


def _sin_acentos(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    ).casefold().strip()


def limpiar_ejemplo(texto: str) -> str:
    """Quita las marcas `[cite: …]` y las referencias al texto ("Según el texto, …"):
    los enunciados van directos (spec de niveles §6)."""
    limpio = _CITA.sub("", texto).strip()
    for prefijo in _PREFIJOS:
        if limpio.casefold().startswith(prefijo):
            limpio = limpio[len(prefijo):].lstrip()
            break
    limpio = _SEGUN_AL_FINAL.sub("", limpio)
    if limpio.startswith("¿") and len(limpio) > 1:
        return "¿" + limpio[1].upper() + limpio[2:]
    return limpio[:1].upper() + limpio[1:]


def _load_xlsx(path: Path) -> list[dict[str, Any]]:
    """Una hoja por nivel (el nombre de la hoja es el nivel); encabezado con "Pregunta" y,
    a su derecha, correcta, similar (confusa) e incorrecta ×2 (distractores)."""
    import openpyxl

    niveles = {n.value: n.value for n in Nivel}
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    items: list[dict[str, Any]] = []
    for ws in wb.worksheets:
        nivel = niveles.get(_sin_acentos(ws.title))
        if nivel is None:
            raise ValueError(f"Hoja «{ws.title}»: su nombre no es un nivel ({', '.join(n.value for n in Nivel)})")
        col: int | None = None
        for fila, row in enumerate(ws.iter_rows(values_only=True), start=1):
            celdas = ["" if c is None else str(c).strip() for c in row]
            if col is None:
                if "Pregunta" in celdas:
                    col = celdas.index("Pregunta")
                continue
            pregunta, *respuestas = (celdas[col:col + 5] + [""] * 5)[:5]
            if not pregunta:
                continue
            if sum(1 for r in respuestas if r) < 4:
                raise ValueError(f"Hoja «{ws.title}», fila {fila}: se esperaban 4 respuestas")
            items.append({
                "question": limpiar_ejemplo(pregunta),
                "nivel": nivel,
                "options": [{"text": limpiar_ejemplo(t), "role": r} for t, r in zip(respuestas, _ROLES_XLSX)],
            })
    return items
```

- [ ] **Step 5: Repository**

En `question_generator/src/qgen/reference/repository.py`:
- Import: `from qgen.prompts.niveles import ORDEN`.
- Extraer la construcción del diccionario del final de `get_reference_exemplars` a:

```python
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
```

  y `get_reference_exemplars` termina con `return [_as_dict(q) for q in exemplars]`.
- Nueva función:

```python
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
```

- [ ] **Step 6: CLI help**

En `question_generator/src/qgen/cli/import_examples.py`, el help de `file_path` pasa a `"Ruta al archivo JSON, JSONL, CSV o XLSX (una hoja por nivel) con preguntas de ejemplo."`.

- [ ] **Step 7: Run tests to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests -q`
Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add question_generator/pyproject.toml uv.lock question_generator/src/qgen/reference question_generator/src/qgen/cli/import_examples.py question_generator/tests/test_reference_importer.py
git commit -m "feat(qgen): ejemplos por nivel desde xlsx y selección de uno por nivel

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Prompt de generación con niveles

**Files:**
- Modify: `question_generator/src/qgen/prompts/families.py`
- Modify: `question_generator/src/qgen/pipeline.py` (`window_instruction`)
- Modify: `question_generator/src/qgen/cost.py` (`CHARS_PER_QUESTION`)
- Test: `question_generator/tests/test_families.py`, `question_generator/tests/test_cost.py`

**Interfaces:**
- Consumes: `DEFINICIONES`, `NIVEL_LABEL` (Task 1); `get_level_exemplars` (Task 4).
- Produces: `SYSTEM_VERSION = "2026-09-25.v7"`; `build_window_instruction(rules, *, manual_title, exemplars)` con sección `NIVELES COGNITIVOS`, sección `PROPORCIÓN` y ejemplos etiquetados por nivel.

- [ ] **Step 1: Write the failing tests**

Agregar a `question_generator/tests/test_families.py` (import `from qgen.prompts.families import SYSTEM_VERSION` junto a los demás):

```python
def test_las_dos_familias_piden_los_cuatro_niveles_con_su_proporcion():
    for perfil in ("manual", "geografia_moderna_mexico", "calculo_una_variable"):
        instr = build_window_instruction(get_default_rules(perfil), manual_title="Libro")
        assert "NIVELES COGNITIVOS" in instr and '"nivel"' in instr
        assert "CONCLUSIÓN INFERIDA" in instr and "CASO INVENTADO" in instr
        assert "55/15/15/15" in instr
        assert 'En "conocimiento" la opción "correct" es un fragmento LITERAL' in instr
    assert SYSTEM_VERSION == "2026-09-25.v7"


def test_los_ejercicios_van_fuera_de_la_proporcion_solo_donde_hay_ejercicios():
    mate = build_window_instruction(get_default_rules("calculo_una_variable"), manual_title="Cálculo")
    info = build_window_instruction(get_default_rules("historia_universal"), manual_title="Historia")
    assert 'los ejercicios son siempre "aplicacion"' in mate
    assert 'los ejercicios son siempre "aplicacion"' not in info


def test_los_ejemplos_van_etiquetados_por_nivel_como_modelo_de_forma():
    ejemplos = [
        {"question_text": "¿Qué islas forman el archipiélago?", "nivel": "conocimiento",
         "options": [{"role": "correct", "text": "María Madre, María Magdalena y María Cleofas"}]},
        {"question_text": "Un equipo de topógrafos…", "nivel": "aplicacion",
         "options": [{"role": "correct", "text": "La apertura de un cenote"}]},
    ]
    instr = build_window_instruction(get_default_rules("manual"), manual_title="M", exemplars=ejemplos)
    assert "Nivel Conocimiento:" in instr and "Nivel Aplicación:" in instr
    assert "modelo de FORMA, no de contenido" in instr
    assert "la guerra se conceptúa" not in instr
```

En `question_generator/tests/test_cost.py`, cambiar la expectativa de `test_cuenta_preguntas_y_verificaciones_por_caracteres` de `(2, 10, 2)` a `(2, 18, 2)`.

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_families.py question_generator/tests/test_cost.py -q`
Expected: FAIL.

- [ ] **Step 3: Implement the prompt changes**

En `question_generator/src/qgen/prompts/families.py`:
- Import: `from qgen.prompts.niveles import DEFINICIONES, NIVEL_LABEL`.
- `SYSTEM_VERSION = "2026-09-25.v7"`.
- Reemplazar `_TEORIA` por:

```python
_TEORIA = (
    '- "teoria": preguntas sobre el contenido del texto, en los cuatro niveles de abajo. '
    'En "conocimiento" la opción "correct" es un fragmento LITERAL del texto (copia exacta, '
    "palabra por palabra; prohibido parafrasear); en los otros niveles sigue la estructura de "
    "clave de su nivel."
)
```

- Nuevas constantes debajo de `_OPCIONES_EJERCICIOS`:

```python
_PROPORCION = (
    '- Genera TODAS las preguntas de "conocimiento" que el texto permita. Sobre esa base K, agrega '
    'de "comprension", "analisis" y "aplicacion" unas 3 de cada una por cada 11 de conocimiento '
    "(proporción 55/15/15/15), y al menos 1 de cada una si K es 3 o más. Con K menor que 3 son "
    "opcionales."
)
_PROPORCION_EJERCICIOS = '\n- Los ejercicios son siempre "aplicacion" y van aparte de esta proporción.'
```

- En `_PLANTILLA`:
  - Después del bloque `TIPOS DE PREGUNTA\n{tipos}\n`, insertar:

```
NIVELES COGNITIVOS (campo "nivel" de cada pregunta)
{niveles}
PROPORCIÓN
{proporcion}
```

  - En `OPCIONES`, reemplazar la línea `- En "teoria": la "confusa" es un concepto parecido con un detalle crítico cambiado; los "distractor" son otros conceptos reales del texto.` por `- La "confusa" y los "distractor" siguen la estructura de su nivel (ver NIVELES COGNITIVOS).`
  - En `CITA Y JUSTIFICACIÓN`, reemplazar la línea de `"cita"` por `- "cita": el fragmento LITERAL del texto en que se apoya la pregunta: el dato, el pasaje que se explica, los datos que se cruzan o la regla que se aplica. En ejercicios, el ejemplo del libro (con su resultado) en que se basa.` y la de `"justificacion"` por `- "justificacion": en "teoria", por qué la correcta lo es (en análisis y aplicación, el razonamiento desde la cita); en ejercicios, la resolución paso a paso.`
  - En la línea de notación, cambiar `la "correct" de "teoria"` por `la "correct" de "conocimiento"`.
- En `build_window_instruction`, agregar a `_PLANTILLA.format(...)`:

```python
        niveles=DEFINICIONES,
        proporcion=_PROPORCION + (_PROPORCION_EJERCICIOS if con_ejercicios else ""),
```

- Reemplazar la parte de `_ejemplos` que arma los bloques por:

```python
    if exemplars:
        bloques = []
        for i, ex in enumerate(exemplars, start=1):
            nivel = ex.get("nivel")
            titulo = f"Nivel {NIVEL_LABEL[nivel]}:" if nivel in NIVEL_LABEL else f"Ejemplo {i}:"
            lineas = [titulo, f'- Pregunta: "{ex.get("question_text") or ex.get("question", "")}"']
            lineas += [f'- {opt.get("role", "distractor")}: "{opt.get("text", "")}"' for opt in ex.get("options", [])]
            bloques.append("\n".join(lineas))
        cuerpo = (
            "Cada ejemplo es un modelo de FORMA, no de contenido: no lo copies ni uses sus datos.\n\n"
            + "\n\n".join(bloques)
        )
```

  (el resto de `_ejemplos` no cambia: sin referencias, la familia militar conserva sus ejemplos de siempre).

- [ ] **Step 4: Exemplars by level and cost**

En `question_generator/src/qgen/pipeline.py`:
- Cambiar el import `from qgen.reference.repository import get_reference_exemplars` por `from qgen.reference.repository import get_level_exemplars`.
- En `window_instruction`, reemplazar la línea de `exemplars = ...` por:

```python
    exemplars = get_level_exemplars(session, profile=profile, manual_code=manual.code)
```

En `question_generator/src/qgen/cost.py`: `CHARS_PER_QUESTION = 190` y actualizar el comentario de supuestos: "≈ 20/11 veces más preguntas por ventana con los niveles (spec de niveles §6)".

- [ ] **Step 5: Run tests to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add question_generator/src/qgen/prompts/families.py question_generator/src/qgen/pipeline.py question_generator/src/qgen/cost.py question_generator/tests
git commit -m "feat(qgen): el prompt pide los cuatro niveles en proporción 55/15/15/15

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Revisión con Claude: nivel, reclasificación y "solo clasificar"

**Files:**
- Modify: `question_generator/src/qgen/claude_review.py`
- Modify: `question_generator/src/qgen/cli/claude_code.py` (salidas de `exportar-revision` e `importar-revision`)
- Test: `question_generator/tests/test_claude_review.py`

**Interfaces:**
- Consumes: `Nivel`, `DEFINICIONES` (Task 1); `Question.cognitive_level` (Task 3).
- Produces: `Veredicto(id, nivel: Nivel, veredicto: Literal[...] | None = None, calificacion: int | None = None, motivos)`; `ExportacionRevision.solo_clasificar: int`; `ResumenRevision.reclasificadas: int`, `ResumenRevision.solo_clasificadas: int`; `metadata_json["revision"]["nivel"]`, `metadata_json["nivel_generado"]`, `metadata_json["clasificacion"] = {"por", "nivel", "fecha"}`.

- [ ] **Step 1: Update existing tests and write the failing ones**

En `question_generator/tests/test_claude_review.py`, agregar `"nivel": "conocimiento"` a **cada** diccionario de veredicto de las pruebas existentes. Luego agregar:

```python
def _sin_nivel(qid: int) -> None:
    with session_scope() as session:
        session.get(Question, qid).cognitive_level = None


def _nivel(qid: int) -> str | None:
    with session_scope() as session:
        return session.get(Question, qid).cognitive_level


def test_la_rubrica_trae_los_niveles_y_sus_criterios(tmp_path):
    manual_id = _seed()
    carpeta = tmp_path / "TST"
    _generar(manual_id, carpeta)
    _exportar_revision(manual_id, carpeta)
    rubrica = (carpeta / "revision" / "instruccion.md").read_text(encoding="utf-8")
    for marca in ("CONCLUSIÓN INFERIDA", "Paráfrasis infiel", "lógicamente innegable",
                  "no se resuelve con la regla citada", "solo clasificar"):
        assert marca in rubrica
    (lote,) = _lotes(carpeta)
    assert "nivel declarado: conocimiento" in (carpeta / "revision" / "lotes" / f"{lote}.md").read_text(encoding="utf-8")


def test_si_el_nivel_revisado_difiere_la_pregunta_se_reclasifica(tmp_path):
    manual_id = _seed()
    carpeta = tmp_path / "TST"
    primera, *_ = _generar(manual_id, carpeta)
    _exportar_revision(manual_id, carpeta)
    _veredictos(carpeta, _lotes(carpeta)[0], [
        {"id": primera, "nivel": "analisis", "veredicto": "aceptar", "calificacion": 4, "motivos": []},
    ])

    resumen = _importar_revision(manual_id, carpeta)

    estado, meta = _estado(primera)
    assert (estado, _nivel(primera), meta["nivel_generado"], meta["revision"]["nivel"]) == (
        "valid", "analisis", "conocimiento", "analisis",
    )
    assert resumen.reclasificadas == 1


def test_las_decididas_sin_nivel_solo_se_clasifican_sin_tocar_su_estado(tmp_path):
    manual_id = _seed()
    carpeta = tmp_path / "TST"
    aprobada, _, _ = _generar(manual_id, carpeta)
    _marcar(aprobada, "valid")
    _sin_nivel(aprobada)

    exportacion = _exportar_revision(manual_id, carpeta)
    contenido = (carpeta / "revision" / "lotes" / f"{_lotes(carpeta)[0]}.md").read_text(encoding="utf-8")
    assert exportacion.solo_clasificar == 1 and "SOLO CLASIFICAR" in contenido

    _veredictos(carpeta, _lotes(carpeta)[0], [
        {"id": aprobada, "nivel": "comprension", "veredicto": "rechazar", "calificacion": 1, "motivos": ["x"]},
    ])
    resumen = _importar_revision(manual_id, carpeta)

    estado, meta = _estado(aprobada)
    assert (estado, _nivel(aprobada), meta["clasificacion"]["nivel"]) == ("valid", "comprension", "comprension")
    assert resumen.solo_clasificadas == 1 and resumen.rechazadas == 0
    assert (aprobada, "ya decidida (valid): solo se clasificó") in resumen.omitidas


def test_una_sin_decidir_sin_veredicto_se_omite(tmp_path):
    manual_id = _seed()
    carpeta = tmp_path / "TST"
    primera, *_ = _generar(manual_id, carpeta)
    _exportar_revision(manual_id, carpeta)
    _veredictos(carpeta, _lotes(carpeta)[0], [{"id": primera, "nivel": "conocimiento"}])

    resumen = _importar_revision(manual_id, carpeta)

    assert (primera, "falta el veredicto") in resumen.omitidas
    assert _estado(primera)[0] == "pending"


def test_un_lote_de_la_ronda_anterior_sin_nivel_no_aplica_nada(tmp_path):
    manual_id = _seed()
    carpeta = tmp_path / "TST"
    primera, *_ = _generar(manual_id, carpeta)
    _exportar_revision(manual_id, carpeta)
    _veredictos(carpeta, "viejo", [{"id": primera, "veredicto": "aceptar", "calificacion": 5, "motivos": []}])

    resumen = _importar_revision(manual_id, carpeta)

    assert [nombre for nombre, _ in resumen.lotes_invalidos] == ["viejo"]
    assert _estado(primera)[0] == "pending"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_claude_review.py -q`
Expected: FAIL.

- [ ] **Step 3: Implement**

En `question_generator/src/qgen/claude_review.py`:
- Imports: `from qgen.prompts.niveles import DEFINICIONES, Nivel`.
- Reemplazar `Veredicto` por:

```python
class Veredicto(BaseModel):
    id: int
    nivel: Nivel
    #: Sin veredicto = solo clasificar (preguntas ya decididas sin nivel).
    veredicto: Literal["aceptar", "rechazar", "dudosa"] | None = None
    calificacion: int | None = Field(default=None, ge=1, le=5)
    motivos: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _coherente(self) -> "Veredicto":
        if self.veredicto is None:
            return self
        if self.calificacion is None:
            raise ValueError(f"pregunta {self.id}: '{self.veredicto}' exige calificación")
        if self.veredicto != "aceptar" and not self.motivos:
            raise ValueError(f"pregunta {self.id}: '{self.veredicto}' exige al menos un motivo")
        if self.veredicto == "aceptar" and self.calificacion < 3:
            raise ValueError(f"pregunta {self.id}: una aceptada lleva calificación 3 o más")
        if self.veredicto == "rechazar" and self.calificacion > 2:
            raise ValueError(f"pregunta {self.id}: una rechazada lleva calificación 2 o menos")
        return self
```

- `ExportacionRevision` gana `solo_clasificar: int = 0`; `ResumenRevision` gana `reclasificadas: int = 0` y `solo_clasificadas: int = 0`.
- Reemplazar `_revisables` por:

```python
def _a_revisar(session: Session, manual_id: int) -> list[tuple[Question, bool]]:
    """(pregunta, solo_clasificar). Revisión completa: sin decidir y sin revisión previa.
    Solo clasificar: cualquier otra pregunta sin nivel (spec de niveles §8)."""
    salida = []
    for q in session.execute(
        select(Question).where(Question.manual_id == manual_id).order_by(Question.id)
    ).scalars():
        if q.validation_status in REVISABLES and "revision" not in (q.metadata_json or {}):
            salida.append((q, False))
        elif q.cognitive_level is None:
            salida.append((q, True))
    return salida
```

- En `exportar_revision`: el agrupamiento usa `for q, solo in _a_revisar(session, manual_id):` y guarda tuplas `(q, solo)` en `grupos`; `_lote` recibe esas tuplas; el `return` pasa `preguntas=sum(map(len, grupos.values()))` y `solo_clasificar=sum(1 for ps in grupos.values() for _, solo in ps if solo)`. `node_id = preguntas[0][0].node_id`.
- En `_lote`, el bucle pasa a `for q, solo in preguntas:` y el encabezado de cada pregunta a:

```python
        partes += [f"## Pregunta {q.id} · {q.question_type} · nivel declarado: {q.cognitive_level or 'sin nivel'}"]
        if solo:
            partes.append("SOLO CLASIFICAR: ya está decidida; escribe solo su id y su nivel.")
        partes.append(q.question_text)
```

  (y se quita el `q.question_text` que iba en la línea del encabezado anterior).
- Reemplazar el cuerpo del bucle `for v in lote.veredictos:` de `importar_revision` por:

```python
        for v in lote.veredictos:
            q = session.get(Question, v.id)
            if q is None or q.manual_id != manual_id:
                resumen.omitidas.append((v.id, "no es de este manual"))
                continue
            revisable = q.validation_status in REVISABLES
            if v.veredicto is not None and revisable:
                if _aplicar(q, v, model_name, ahora):
                    resumen.reclasificadas += 1
                if v.veredicto == "aceptar":
                    resumen.aceptadas += 1
                elif v.veredicto == "rechazar":
                    resumen.rechazadas += 1
                else:
                    resumen.dudosas += 1
                continue
            if q.cognitive_level is None:
                _clasificar(q, v.nivel, model_name, ahora)
                resumen.solo_clasificadas += 1
                if v.veredicto is not None:
                    resumen.omitidas.append((v.id, f"ya decidida ({q.validation_status}): solo se clasificó"))
                continue
            resumen.omitidas.append((v.id, "falta el veredicto" if revisable else f"ya decidida ({q.validation_status})"))
```

- Reemplazar `_aplicar` por (y agregar `_clasificar`):

```python
def _aplicar(q: Question, v: Veredicto, model_name: str, ahora: datetime) -> bool:
    """Aplica el veredicto y el nivel; devuelve si la pregunta se reclasificó. Los motivos
    van en `revision`, aparte de los `motivos` de la revisión automática."""
    meta = dict(q.metadata_json or {})
    reclasificada = q.cognitive_level is not None and q.cognitive_level != v.nivel.value
    if reclasificada:
        meta["nivel_generado"] = q.cognitive_level
    meta["revision"] = {
        "por": model_name, "veredicto": v.veredicto, "calificacion": v.calificacion,
        "motivos": list(v.motivos), "nivel": v.nivel.value, "fecha": ahora.isoformat(),
    }
    q.metadata_json = meta
    q.validation_status = ESTADO_DE[v.veredicto]
    q.validated_at = ahora
    q.cognitive_level = v.nivel.value
    return reclasificada


def _clasificar(q: Question, nivel: Nivel, model_name: str, ahora: datetime) -> None:
    """Solo el nivel: el estado y la fecha de validación de una pregunta decidida no se tocan."""
    q.metadata_json = {
        **(q.metadata_json or {}),
        "clasificacion": {"por": model_name, "nivel": nivel.value, "fecha": ahora.isoformat()},
    }
    q.cognitive_level = nivel.value
```

- La prueba existente de `meta["revision"] == {...}` pasa a incluir `"nivel": "conocimiento"`.
- En `_rubrica`:
  - Después de `## Temas del manual`, agregar una sección:

```
## Niveles cognitivos

Clasifica cada pregunta en uno de estos cuatro niveles (campo "nivel"), según lo que
de verdad pide, no según lo que declaró la generación:

{DEFINICIONES}
```

  (construido con f-string: `{DEFINICIONES}` es la constante importada).
  - Después del punto 5 de la rúbrica, agregar:

```
6. **Paráfrasis infiel** (comprensión): la clave no dice lo mismo que el texto.
7. **Conclusión dudosa** (análisis): la clave no es lógicamente innegable a partir de los datos citados.
8. **Caso sin solución en el texto** (aplicación): el caso no se resuelve con la regla citada.

Si el nivel que declaró la generación no es el que la pregunta pide de verdad, **no la
rechaces por eso**: escribe el nivel correcto y juzga la pregunta en ese nivel.
```

  - En `## Formato del veredicto`, agregar `"nivel"` a los tres ejemplos del JSON (por ejemplo `"nivel": "conocimiento"`, `"nivel": "analisis"`, `"nivel": "comprension"`) y este párrafo:

```
Cada veredicto lleva su "nivel" (obligatorio). Las preguntas marcadas **SOLO
CLASIFICAR** ya están decididas: escribe solo `{{"id": 123, "nivel": "aplicacion"}}`,
sin veredicto ni calificación, y su estado no cambia (solo clasificar).
```

En `question_generator/src/qgen/cli/claude_code.py`:
- `exportar_revision_cmd` imprime: `f"{exportacion.preguntas} preguntas ({exportacion.solo_clasificar} solo para clasificar) en {exportacion.lotes} lotes en {exportacion.carpeta}"`.
- `importar_revision_cmd` agrega a la primera línea: `f", {resumen.reclasificadas} reclasificadas, {resumen.solo_clasificadas} solo clasificadas"`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add question_generator/src/qgen/claude_review.py question_generator/src/qgen/cli/claude_code.py question_generator/tests/test_claude_review.py
git commit -m "feat(qgen): la revisión con Claude clasifica el nivel y reclasifica

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: Contrato v3 del bundle

**Files:**
- Modify: `question_generator/src/qgen/bundle/spec.py`
- Modify: `question_generator/src/qgen/bundle/build.py`
- Modify: `CONTRATO-BUNDLE.md`
- Test: `question_generator/tests/test_bundle_spec.py`, `question_generator/tests/test_bundle_export.py`

**Interfaces:**
- Consumes: `Question.cognitive_level` (Task 3).
- Produces: `BUNDLE_VERSION = 3`, `SUPPORTED_VERSIONS = frozenset({1, 2, 3})`, `COGNITIVE_LEVELS = frozenset({"conocimiento", "comprension", "analisis", "aplicacion"})`; cada pregunta del bundle v3 trae la clave `cognitive_level`.

- [ ] **Step 1: Write the failing tests**

En `question_generator/tests/test_bundle_spec.py`:
- En `_bundle()`, agregar `"cognitive_level": "conocimiento",` a la pregunta (después de `"source_quote"`).
- En `_v1`, agregar `q.pop("cognitive_level")` dentro del bucle.
- Agregar:

```python
def _v2(b):
    b["bundle_version"] = 2
    for q in b["questions"]:
        q.pop("cognitive_level")


def test_v3_exige_la_clave_del_nivel():
    assert any("`cognitive_level`" in e for e in _errors(lambda b: b["questions"][0].pop("cognitive_level")))


def test_v3_rechaza_un_nivel_desconocido():
    assert any("`cognitive_level`" in e for e in _errors(lambda b: b["questions"][0].update(cognitive_level="memoria")))


def test_v3_admite_null_sin_clasificar_y_avisa():
    bundle = _bundle()
    bundle["questions"][0]["cognitive_level"] = None
    report = validate(bundle)
    assert report.ok
    assert any("sin nivel cognitivo" in w for w in report.warnings)


def test_v2_sigue_siendo_valido_sin_el_nivel():
    assert _errors(_v2) == []
```

En `question_generator/tests/test_bundle_export.py`, agregar:

```python
def test_el_nivel_cognitivo_viaja_en_el_bundle():
    init_question_tables()
    with session_scope() as session:
        manual_id, node_ids = _seed(session)
        run = create_run(
            session, manual_id=manual_id, model="claude-opus-5-5", mode="immediate",
            profile_used="codigo", rules_snapshot={"name": "codigo"}, nodes_total=1,
        )
        persist_question(
            session, run=run, node_id=node_ids[-1], manual_id=manual_id, question_type="teoria",
            source_quote=CITA, generation_order=0, payload=_question(), raw_response={},
            cognitive_level="analisis",
        )
        finalize_run(
            session, run=run, nodes_completed=1, nodes_failed=0, cost_input_tokens=0,
            cost_output_tokens=0, cost_cached_tokens=0, cost_estimate_usd=0.0, status="succeeded",
        )
        bundle = build_bundle(session, manual_id=manual_id)
    assert bundle["bundle_version"] == 3
    assert bundle["questions"][0]["cognitive_level"] == "analisis"
    assert validate(bundle).ok
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests/test_bundle_spec.py question_generator/tests/test_bundle_export.py -q`
Expected: FAIL.

- [ ] **Step 3: Implement**

En `question_generator/src/qgen/bundle/spec.py`:
- `BUNDLE_VERSION = 3` y `SUPPORTED_VERSIONS = frozenset({1, 2, 3})`.
- Debajo de `QUESTION_TYPES`:

```python
#: Niveles cognitivos (v3); `null` = pregunta anterior a los niveles, sin clasificar.
COGNITIVE_LEVELS = frozenset({"conocimiento", "comprension", "analisis", "aplicacion"})
```

- En `validate`, junto a `by_status: dict[str, int] = {}`: `sin_nivel = 0`.
- Dentro del bucle de preguntas, después del bloque `if version >= 2:` que valida `question_type` y `source_quote`:

```python
        if version >= 3:
            if "cognitive_level" not in question:
                report.error(f"{where}: falta `cognitive_level` (v3); usa null si no está clasificada.")
            elif question["cognitive_level"] is None:
                sin_nivel += 1
            elif question["cognitive_level"] not in COGNITIVE_LEVELS:
                report.error(
                    f"{where}: `cognitive_level` = {question['cognitive_level']!r}; debe ser uno de "
                    f"{sorted(COGNITIVE_LEVELS)} o null."
                )
```

- Junto a los demás avisos del final (después del de preguntas rechazadas):

```python
    if sin_nivel:
        report.warn(f"{sin_nivel} pregunta(s) sin nivel cognitivo (`cognitive_level` null).")
```

En `question_generator/src/qgen/bundle/build.py`, en el diccionario de cada pregunta, después de `"source_quote": question.source_quote,`: `"cognitive_level": question.cognitive_level,`.

En `CONTRATO-BUNDLE.md`:
- En el ejemplo JSON de la pregunta (junto a `"source_quote"`), agregar `"cognitive_level": "conocimiento",`.
- En las notas por bloque (donde dice "Desde v2 trae `question_type` …"), agregar: "Desde v3 trae `cognitive_level`: `conocimiento`, `comprension`, `analisis` o `aplicacion`; `null` solo en preguntas generadas antes de los niveles y aún sin clasificar."
- En §5 (validaciones), agregar la 12: "(v3) `cognitive_level` presente; su valor es uno de los cuatro niveles o `null` (aviso con la cantidad de `null`)."
- En `### Historial`, antes de v2:

```
- **v3 (2026-09-25)** — niveles cognitivos: cada pregunta trae `cognitive_level`
  (`conocimiento | comprension | analisis | aplicacion`, o `null` si es anterior a los
  niveles y no se ha clasificado). La identidad no cambia. El importador acepta v1, v2 y
  v3. En Postgres: una columna nullable `cognitive_level`.
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest question_generator/tests explorer/tests -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add question_generator/src/qgen/bundle CONTRATO-BUNDLE.md question_generator/tests
git commit -m "feat(bundle): contrato v3 con el nivel cognitivo de cada pregunta

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: Explorador: nivel, filtro e indicadores

**Files:**
- Modify: `explorer/src/explorer/questions_access.py`
- Modify: `explorer/src/explorer/pages/6_❓_Preguntas.py`
- Test: `explorer/tests/test_questions_access.py`, `explorer/tests/test_export_page.py`

**Interfaces:**
- Consumes: `NIVEL_LABEL`, `ORDEN`, `PROPORCION` (Task 1); `Question.cognitive_level`, `metadata_json["nivel_generado"]` (Tasks 3 y 6).
- Produces: `QuestionView.cognitive_level: str | None`, `QuestionView.nivel_generado: str | None`; `SIN_NIVEL = "sin_nivel"`; `list_questions(..., levels: tuple[str, ...] | None = None)`; `QuestionKPIs.by_level: dict[str, int]`; `level_label(question: QuestionView) -> str`; `revision_label` añade el nivel si la revisión lo trae.

- [ ] **Step 1: Write the failing tests**

En `explorer/tests/test_questions_access.py` (imports: `level_label`, `SIN_NIVEL` desde `explorer.questions_access`):

```python
def test_filtra_por_nivel_incluido_sin_clasificar():
    st.cache_data.clear()
    manual_id, _, _, qid = _seed_questions_data()
    assert list_questions(manual_id, levels=(SIN_NIVEL,))  # el seed no tiene nivel
    assert list_questions(manual_id, levels=("analisis",)) == []
    with session_scope() as session:
        from qgen.models.schema import Question
        q = session.get(Question, qid)
        q.cognitive_level = "analisis"
        q.metadata_json = {**(q.metadata_json or {}), "nivel_generado": "comprension"}
    st.cache_data.clear()
    [q] = list_questions(manual_id, levels=("analisis",))
    assert level_label(q) == "Análisis (generada como Comprensión)"
    assert get_question_kpis(manual_id).by_level == {"analisis": 1}


def test_la_etiqueta_de_revision_lleva_el_nivel_si_lo_hay():
    revision = {"por": "claude-opus-5-5", "veredicto": "aceptar", "calificacion": 5, "motivos": [], "nivel": "aplicacion"}
    assert revision_label(revision) == "Revisión de claude-opus-5-5: aceptar · 5/5 · Aplicación"
```

En `explorer/tests/test_export_page.py`, en `_seed`, pasar `cognitive_level="aplicacion"` a `persist_question` y agregar:

```python
def test_la_pregunta_muestra_su_nivel_junto_al_tipo():
    at = _open_page(_seed(run_status="succeeded"))
    assert any("Ejercicio nuevo · Aplicación" in c.value for c in at.caption)
```

(La prueba existente `test_la_pregunta_muestra_su_tipo_y_sus_motivos` busca "Ejercicio nuevo" dentro del caption y sigue pasando.)

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest explorer/tests -q`
Expected: FAIL.

- [ ] **Step 3: Implement data access**

En `explorer/src/explorer/questions_access.py`:
- Import: `from qgen.prompts.niveles import NIVEL_LABEL, ORDEN, PROPORCION`.
- Debajo de `TYPE_LABEL`:

```python
#: Valor del filtro para las preguntas sin nivel cognitivo (anteriores a los niveles).
SIN_NIVEL = "sin_nivel"
```

- `QuestionView` gana `cognitive_level: str | None = None` y `nivel_generado: str | None = None`; en `list_questions`, el constructor recibe `cognitive_level=q.cognitive_level, nivel_generado=(q.metadata_json or {}).get("nivel_generado"),`.
- `list_questions` gana el parámetro `levels: tuple[str, ...] | None = None` y, después del filtro de `statuses`:

```python
        if levels:
            nombrados = [n for n in levels if n != SIN_NIVEL]
            condicion = Question.cognitive_level.in_(nombrados) if nombrados else None
            if SIN_NIVEL in levels:
                nulos = Question.cognitive_level.is_(None)
                condicion = nulos if condicion is None else (condicion | nulos)
            stmt = stmt.where(condicion)
```

- `QuestionKPIs` gana `by_level: dict[str, int] = Field(default_factory=dict)`; en `get_question_kpis`, calcular:

```python
        by_level = {
            nivel: n
            for nivel, n in session.execute(
                select(Question.cognitive_level, func.count(Question.id))
                .where(Question.manual_id == manual_id, Question.cognitive_level.is_not(None))
                .group_by(Question.cognitive_level)
            ).all()
        }
```

  y pasar `by_level=by_level` a `QuestionKPIs(...)`.
- Nuevas funciones (junto a `revision_label`):

```python
def level_label(question: QuestionView) -> str:
    """El nivel de la pregunta y, si la revisión lo cambió, el que declaró la generación."""
    if not question.cognitive_level:
        return "sin nivel"
    texto = NIVEL_LABEL.get(question.cognitive_level, question.cognitive_level)
    if question.nivel_generado:
        texto += f" (generada como {NIVEL_LABEL.get(question.nivel_generado, question.nivel_generado)})"
    return texto
```

- En `revision_label`, después de armar `texto` con la calificación: `if revision.get("nivel"): texto += f" · {NIVEL_LABEL.get(revision['nivel'], revision['nivel'])}"` (antes de los motivos).

- [ ] **Step 4: Implement the page**

En `explorer/src/explorer/pages/6_❓_Preguntas.py`:
- Importar `SIN_NIVEL`, `level_label` desde `explorer.questions_access` y `from qgen.prompts.niveles import NIVEL_LABEL, ORDEN, PROPORCION`.
- El caption del tipo pasa a:

```python
        st.caption(f"{TYPE_LABEL.get(question.question_type, question.question_type)} · {level_label(question)}")
```

- Después del `kpi_row` por estado:

```python
if kpis.by_level:
    total_niveles = sum(kpis.by_level.values())
    kpi_row(
        [
            (
                NIVEL_LABEL[n.value],
                kpis.by_level.get(n.value, 0),
                f"{100 * kpis.by_level.get(n.value, 0) / total_niveles:.0f}% (meta {PROPORCION[n]}%)",
            )
            for n in ORDEN
        ]
    )
```

- En los filtros de la pestaña Preguntas: `filtros = st.columns([0.25, 0.2, 0.2, 0.35])` y un multiselect de nivel en la segunda columna (corriendo corrida y búsqueda a la tercera y cuarta):

```python
    with filtros[1]:
        niveles = st.multiselect(
            "Nivel",
            options=[n.value for n in ORDEN] + [SIN_NIVEL],
            default=[],
            format_func=lambda n: NIVEL_LABEL.get(n, "sin nivel"),
            placeholder="Todos",
        )
```

  y `list_questions(..., levels=tuple(niveles) or None, ...)`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest explorer/tests question_generator/tests -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add explorer
git commit -m "feat(explorer): nivel cognitivo, filtro por nivel e indicadores de proporción

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 9: Documentación, grafo y verificación completa

**Files:**
- Modify: `README.md`
- Modify: `graphify-out/*` (regenerado)

- [ ] **Step 1: README**

En `README.md`, sección de generación desde Claude Code:
- Debajo del bloque de `qgen-claude exportar/importar`, agregar un párrafo "Niveles cognitivos": cada pregunta lleva `nivel` (conocimiento, comprensión, análisis, aplicación) en proporción 55/15/15/15; la clave es literal solo en conocimiento; el resumen muestra la proporción real.
- Agregar el bloque:

```bash
py -3.14 -m uv run qgen-import-examples ejemplos.xlsx --profile global   # una hoja por nivel
```

  con una línea: "El prompt usa un ejemplo por nivel (del manual, del perfil o global)."
- En la sección de revisión: "Cada veredicto lleva `nivel`; si difiere del generado, la pregunta se reclasifica. Las preguntas ya decididas sin nivel salen como SOLO CLASIFICAR: se clasifican sin cambiar su estado."

- [ ] **Step 2: Full suite and graph**

Run: `.venv/Scripts/python.exe -m pytest -q`
Expected: todo PASS (el conteo anterior era 300 passed, 1 skipped; ahora más).

Run: `PYTHONHASHSEED=0 graphify update .`
Expected: "Code graph updated".

- [ ] **Step 3: Commit**

```bash
git add README.md graphify-out
git commit -m "docs: niveles cognitivos en el README y grafo al día

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 10: Prueba piloto con Geografía (manual 11)

Tarea operativa sobre la base real (`data/manuals.sqlite`); no agrega código. Cada paso reporta su salida.

**Ventanas elegidas** (manual 11 no tiene preguntas; las claves salen de `plan_windows`):
`577:0-2` (coordenadas extremas, Suchiate), `578:0-0` (extensión; comparación con Canadá, Brasil…), `582:0-2` (Sierra Madre Occidental, Cordillera Neovolcánica), `582:9-10` (cenotes), `584:0-1` (islas Marías, pólipos).

- [ ] **Step 1: Respaldo**

```bash
.venv/Scripts/python.exe -c "import sqlite3,sys; s=sqlite3.connect('data/manuals.sqlite'); d=sqlite3.connect(sys.argv[1]); s.backup(d); d.close()" "<scratchpad>/manuals_antes_niveles.sqlite"
```

- [ ] **Step 2: Importar los 16 ejemplos**

```bash
.venv/Scripts/python.exe -m qgen.cli.import_examples "C:\Users\luis_\Downloads\datapreguntashistoria.xlsx" --profile global --source-tag ejemplos_niveles_geografia
```

Expected: "Se importaron 16 preguntas de ejemplo" (5 conocimiento, 4 comprensión, 3 análisis, 4 aplicación).

- [ ] **Step 3: Exportar las ventanas de Geografía**

```bash
.venv/Scripts/python.exe -m qgen.cli.claude_code exportar 11
```

Expected: 17 ventanas en `data/claude_code/Geografia Moderna de Mexico/`. Revisar que `instruccion.md` trae NIVELES COGNITIVOS, la proporción y un ejemplo por nivel.

- [ ] **Step 4: Escribir las respuestas de las 5 ventanas**

Seguir `instruccion.md` y escribir `respuestas/577_0-2.json`, `578_0-0.json`, `582_0-2.json`, `582_9-10.json`, `584_0-1.json`. Las otras 12 ventanas quedan pendientes.

- [ ] **Step 5: Importar y medir la proporción**

```bash
.venv/Scripts/python.exe -m qgen.cli.claude_code importar 11
```

Expected: 5 ventanas, tabla "Proporción por nivel" y lista de ventanas sin algún nivel.

- [ ] **Step 6: Revisión con Claude**

```bash
.venv/Scripts/python.exe -m qgen.cli.claude_code exportar-revision 11
```

Revisar cada lote con la rúbrica (veredicto, calificación y nivel) en `revision/veredictos/`, luego:

```bash
.venv/Scripts/python.exe -m qgen.cli.claude_code importar-revision 11
```

- [ ] **Step 7: Medir y reportar**

```bash
.venv/Scripts/python.exe -c "import sqlite3; c=sqlite3.connect('data/manuals.sqlite'); print(c.execute(\"select cognitive_level, validation_status, count(*) from questions where manual_id=11 group by 1,2\").fetchall()); print(c.execute(\"select count(*) from questions where manual_id=11 and json_extract(metadata_json,'$.nivel_generado') is not null\").fetchone())"
```

Reportar al usuario: proporción real contra 55/15/15/15, cuántas se reclasificaron (y de qué nivel a cuál), cuántas se rechazaron por nivel, y si alguna copió los ejemplos. **No** clasificar el Taller ni seguir con el resto de Geografía sin su visto bueno (spec §14.4).
