# Contrato: bundle de contenido v2

La interfaz entre quien **genera** las preguntas (este repo) y quien **opera**
la webapp. Un fichero JSON por manual, autocontenido, que viaja de un lado al
otro sin que ninguno necesite acceso al del otro.

> La implementación del contrato es
> [question_generator/src/qgen/bundle/spec.py](question_generator/src/qgen/bundle/spec.py),
> un módulo de solo-stdlib. Lo importan **los dos** comandos del §6: el
> exportador de aquí y el importador de la webapp. Que la validación viva en un
> solo sitio es lo que garantiza que el importador no pueda rechazar algo que el
> exportador dio por bueno.

---

## 1. Por qué existe

El puente anterior leía `data/manuals.sqlite` **en crudo** y copiaba sus tablas
a Postgres. Funciona mientras las dos mitades vivan en la misma máquina, pero
como interfaz entre dos personas tiene tres problemas:

1. **La entrega sería un binario.** Un `.sqlite` no se revisa, no se diffea, no
   se comenta. Hay que confiar en él a ciegas.
2. **Los ids son locales.** `manuals.id`, `nodes.id`, `questions.id` son
   autoincrementales de una base concreta: cambian al regenerar y no significan
   nada fuera de esa máquina.
3. **Acopla los esquemas.** Cualquier cambio en las tablas del pipeline rompe al
   importador en silencio, porque no hay contrato explícito que validar.

El bundle resuelve las tres: es texto revisable, identifica todo por claves
estables y con significado, y se valida contra este documento antes de que nadie
escriba en ninguna base.

---

## 2. Forma del fichero

- **Nombre:** `{codigo_manual}--{YYYYMMDD}--v{n}.json`, en minúsculas y solo
  `[a-z0-9._-]`. Ej.: `cjm--20260817--v1.json`. El `v{n}` se incrementa cuando
  se vuelve a entregar el **mismo** manual, se haga el mismo día o tres semanas
  después.
- **Codificación:** UTF-8 sin BOM, sin escapar acentos, indentado a 2 espacios
  (se diffea).
- **Fechas:** ISO 8601 en UTC con sufijo `Z` — `"2026-08-17T10:15:00Z"`.
- **Nulos explícitos:** un campo opcional sin valor va como `null`, no se omite.
- **Integridad:** junto al bundle viaja `{nombre}.sha256`. El importador lo
  verifica antes de leer, así que **los dos ficheros se entregan juntos**.
- **Tamaño:** por encima de 25 MB el exportador comprime a `.json.gz`. Se
  entrega igual; el importador lo lee comprimido.
- **Campos desconocidos:** el importador los ignora (así una versión menor nueva
  no rompe nada). Un campo requerido ausente es error duro.
- **Alcance:** un bundle = un manual. Nunca dos.

---

## 3. Estructura

```jsonc
{
  "bundle_version": 2,
  "generated_at": "2026-08-17T10:15:00Z",
  "generator": {
    "tool": "qgen",
    "version": "0.1.0",
    "pipeline_commit": "0a91bfc"
  },

  "manual": {
    "code": "CJM",
    "edition": null,
    "title": "Código de Justicia Militar",
    "branch": null,
    "source_path": "data/raw_pdfs/cjm_codigo_justicia_militar.pdf",
    "source_sha256": "9f2c…",
    "page_count": 320,
    "extractor_used": "docling",
    "ingested_at": "2026-08-16T22:04:11Z",
    "metadata": {}
  },

  "catalog_hint": {
    "grado_code": "SARG_2",
    "materia_code": "JUS_MIL"
  },

  "nodes": [
    {
      "ref": "01.03.02",
      "parent_ref": "01.03",
      "level": 2,
      "level_label": "Sección",
      "ordinal": "II",
      "title": "De las faltas contra el servicio",
      "breadcrumb": "PARTE I › Capítulo 3 › Sección II",
      "page_start": 42,
      "page_end": 47,
      "is_anexo": false,
      "metadata": {},
      "chunks": [
        {
          "ordinal": 0,
          "text": "…",
          "char_count": 1840,
          "page_start": 42,
          "page_end": 44,
          "has_table": false,
          "has_image_ref": false,
          "metadata": {}
        }
      ]
    }
  ],

  "runs": [
    {
      "ref": "gemini-3.6-flash--immediate--20260817T093000Z",
      "model": "gemini-3.6-flash",
      "mode": "immediate",
      "status": "succeeded",
      "profile_used": "default",
      "rules_snapshot": {},
      "started_at": "2026-08-17T09:30:00Z",
      "completed_at": "2026-08-17T09:58:22Z",
      "nodes_total": 214,
      "nodes_completed": 211,
      "nodes_failed": 3,
      "cost_input_tokens": 1840221,
      "cost_output_tokens": 96044,
      "cost_cached_tokens": 1712004,
      "cost_estimate_usd": 1.284312,
      "metadata": {}
    }
  ],

  "questions": [
    {
      "run_ref": "gemini-3.6-flash--immediate--20260817T093000Z",
      "node_ref": "01.03.02",
      "generation_order": 17,
      "question_text": "¿Cuál es …?",
      "justification": "El artículo 142 establece …",
      "question_type": "teoria",
      "source_quote": "El artículo 142 establece que …",
      "validation_status": "valid",
      "validated_at": "2026-08-17T11:02:00Z",
      "created_at": "2026-08-17T09:41:07Z",
      "metadata": {},
      "options": [
        { "role": "correct",    "order_in_question": 0, "text": "…", "is_correct": true,  "metadata": {} },
        { "role": "confusa",    "order_in_question": 1, "text": "…", "is_correct": false, "metadata": {} },
        { "role": "distractor", "order_in_question": 2, "text": "…", "is_correct": false, "metadata": {} },
        { "role": "distractor", "order_in_question": 3, "text": "…", "is_correct": false, "metadata": {} }
      ]
    }
  ]
}
```

### Notas por bloque

**`generator`** — trazabilidad. `pipeline_commit` es el commit de este repo con
el que se produjo la entrega; sirve para reproducir una vieja.

**`manual`** — la tabla `manuals` menos el `id`, más `source_sha256`: el hash del
PDF de origen, para saber si dos bundles salen del mismo documento. La identidad
del manual es el par **`(code, edition)`**.

**`catalog_hint`** — **opcional y orientativo.** El importador puede ignorarlo.
Existe porque del otro lado el emparejamiento manual → materia es una heurística
de una línea (`CJM*` → Justicia Militar, el resto → Operaciones Militares) que se
rompe en cuanto haya un tercer tipo de manual, y desde aquí se sabe mejor dónde
va cada cosa. Dónde se publica y a qué precio sigue siendo decisión de la webapp.

**`nodes`** — el árbol, **plano** con `parent_ref`, y los `chunks` **anidados**
dentro de su nodo. Ordenado por `ref`.

**`runs`** — las corridas con su contabilidad de tokens y costo. Un manual puede
traer varias: cada invocación de `qgen-generate` abre la suya, y las preguntas
que faltaban se llenan en corridas posteriores.

**`questions`** — cada una apunta a su corrida y a su nodo por `ref`, con sus 4
opciones ordenadas. Desde v2 trae `question_type` (`teoria`, `ejercicio_libro` o
`ejercicio_nuevo`) y `source_quote` (la cita del texto en que se apoya), y un nodo
puede tener varias preguntas en la misma corrida.

---

## 4. Identidad: las claves estables

Esta es la parte que hace que el bundle valga más que una copia del SQLite.
**Ningún id autoincremental viaja en el bundle.**

| Entidad | Clave | Cómo se construye |
|---|---|---|
| Manual | `(code, edition)` | el índice único de `manuals` |
| Nodo | `ref` | el `sort_key` que calcula el ensamblador: la ruta posicional `01.03.02` |
| Chunk | `(node_ref, ordinal)` | por anidamiento |
| Corrida | `ref` | `{model}--{mode}--{started_at compacto UTC}` |
| Pregunta | `(run_ref, generation_order)` | desde v2; espeja el índice único de Postgres. En v1 era `(run_ref, node_ref)` |
| Opción | `(pregunta, order_in_question)` | por anidamiento |

Dos exportaciones del mismo estado producen los mismos `ref` (lo único que
cambia entre ellas es `generated_at`). Eso permite diffear dos entregas de un
mismo manual y ver qué cambió de verdad, y deja la puerta abierta a un
importador incremental (§7) sin cambiar el formato.

> **Cuidado con el `ref` de nodo.** El `sort_key` se arma como
> `".".join(f"{c:02d}" …)`: con más de 99 hermanos en un nivel pasa a tres
> dígitos y el orden lexicográfico deja de coincidir con el jerárquico. La
> unicidad se mantiene, pero el exportador **comprueba que no haya `ref`
> repetidos y aborta** si los hay, en vez de confiar. Si ese error salta, la
> jerarquía está mal y hay que re-ingestar el manual.

---

## 5. Las validaciones

Todo o nada: si algo falla, no se escribe (ni se importa) nada. Las corre tanto
`qgen-export` antes de escribir como el importador antes de tocar Postgres.

1. El `.sha256` acompaña al fichero y cuadra.
2. `bundle_version` es una versión mayor conocida.
3. Están todos los campos requeridos, con su tipo y dentro de la longitud que
   aguanta cada columna: pregunta ≤ 1000, opción ≤ 500, justificación ≤ 2000,
   `manual.title` ≤ 512, `node.title` ≤ 1024, `source_quote` ≤ 2000 (v2).
4. Los `ref` de nodo son únicos; todo `parent_ref` existe en el bundle o es
   `null`; el árbol tiene raíz y no tiene ciclos.
5. Todo `node_ref` y `run_ref` de una pregunta existe en el bundle, y no hay dos
   preguntas con la misma identidad (§4): mismo `(run_ref, generation_order)` en v2,
   mismo `(run_ref, node_ref)` en v1.
6. Ninguna corrida está en `status: "running"` — una generación a medias no se
   entrega. `mode` ∈ `immediate | batch`.
7. Cada pregunta trae **exactamente 4 opciones**, con el reparto
   `1 correct · 1 confusa · 2 distractor`, un solo
   `is_correct: true`, y que sea justo la de rol `correct`.
8. Sin textos de opción duplicados dentro de una misma pregunta (comparando en
   minúsculas y sin espacios de sobra).
9. `validation_status` ∈ `pending | valid | needs_review | rejected`.
10. Ningún campo con pinta de secreto (API keys, cadenas de conexión con
    contraseña, claves PEM) en los bloques libres.
11. (v2) `question_type` ∈ `teoria | ejercicio_libro | ejercicio_nuevo` y
    `source_quote` no vacío.

Los errores salen con la ruta exacta dentro del fichero —
`questions[17].options[3]: …` — para poder localizarlos sin investigar.

Aparte hay **avisos**, que no bloquean: preguntas en `needs_review` o
`rejected`, corridas con nodos fallidos, nodos con texto que se quedaron sin
pregunta. Son para mirarlos antes de dar una entrega por buena.

### Lo que queda fuera del bundle a propósito

- **La respuesta cruda de Gemini.** Es el grueso del peso y no se usa en
  runtime; se queda en el SQLite de aquí. Se puede incluir con `--include-raw`
  cuando haga falta depurar algo del otro lado.
- **Nombres de cache y `batch_job_id`** de Gemini: identifican la cuenta de quien
  genera, no significan nada del otro lado.
- **Todo el catálogo** (grados, materias, exámenes, precios, créditos) salvo el
  `catalog_hint` orientativo.
- **Cualquier credencial.**

---

## 6. Los dos comandos

### Aquí — `qgen-export`

```bash
py -3.14 -m uv run qgen-export <manual_id>                    # a data/bundles/
py -3.14 -m uv run qgen-export <manual_id> --check            # valida y no escribe
py -3.14 -m uv run qgen-export <manual_id> --run <run_id>     # una sola corrida (repetible)
py -3.14 -m uv run qgen-export <manual_id> --include-raw      # + respuesta cruda de Gemini
py -3.14 -m uv run qgen-export <manual_id> --revision 3       # fija el v{n} del nombre
```

Sin `--run`, exporta todas las corridas del manual con sus preguntas. Escribe el
`.json` (o `.json.gz`) y su `.sha256`, e imprime un resumen: nodos, chunks,
preguntas por `validation_status` y costo de las corridas incluidas.

### Del otro lado — `import_bundle.py`

Vive en el repo de la webapp; aquí solo importa lo que hace con lo que
entregamos, porque explica por qué el contrato es como es:

- **Nunca trunca.** La unidad de trabajo es el manual.
- Un manual ya cargado **se salta**; recargarlo exige `--replace`, y si de sus
  preguntas cuelgan respuestas de alumnos, avisa y se niega salvo `--force`.
- Al terminar crea o actualiza el examen del manual y lo cuelga de su materia.
  Por debajo de 20 preguntas el examen se crea **sin publicar**.
- Acepta varios bundles de una vez y los valida todos **antes** de abrir la
  conexión: si uno viene roto, no se importa ninguno.

---

## 7. Versionado del contrato

`bundle_version` es un entero, no semver.

- **Añadir un campo opcional** no sube la versión: el importador ignora lo que no
  conoce y el exportador no puede asumir que se lea.
- **Quitar o renombrar un campo, o cambiar su significado**, sube la versión. El
  importador rechaza de entrada una versión que no conozca.
- Los cambios se acuerdan editando **este documento** antes de tocar código, y
  ambos lados actualizan a la vez. Este fichero existe en los dos repos: si se
  cambia aquí, hay que cambiarlo allá.

### Historial

- **v2 (2026-09-23)** — generación por ventanas: la identidad de una pregunta pasa a
  `(run_ref, generation_order)`, así que un nodo puede tener varias preguntas por
  corrida; cada pregunta trae `question_type` y `source_quote` (obligatorios). El
  importador acepta v1 y v2. En Postgres: el índice único de `questions` cambia de
  (corrida, nodo) a (corrida, `generation_order`) y se añaden las dos columnas.

### Pendiente conocido: importación incremental

La v1 importa con granularidad de **manual**: recargar uno borra sus preguntas y,
con ellas, las respuestas que los alumnos hubieran dado. Sirve mientras el
contenido esté en construcción y nadie haya estudiado todavía.

En cuanto haya alumnos de verdad hará falta importación por pregunta: comparar
`(run_ref, generation_order)` contra lo que ya está cargado, insertar las nuevas,
actualizar las que cambiaron y marcar como `rejected` las que desaparecieron, sin
borrar nunca una fila de la que cuelgue una respuesta. **El formato ya lo
soporta** — para eso las claves del §4 son estables. Falta escribir el importador.
