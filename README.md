# Ruta al Ascenso — generación de contenido

Este repositorio es la **mitad de contenido** del proyecto: convierte manuales
militares en PDF en preguntas de examen. La otra mitad —la webapp que se las
sirve a los alumnos— es un proyecto aparte y no hace falta para nada de lo que
se hace aquí.

| | Aquí | La webapp |
|---|---|---|
| Qué hace | PDF → jerarquía → preguntas | catálogo, exámenes, alumnos, pagos |
| Lenguaje | Python 3.14 + uv | TypeScript (NestJS + Next.js) |
| Base de datos | `data/manuals.sqlite`, un fichero local | Postgres |
| Salida | un **bundle JSON** por manual | lo importa quien opera la webapp |

La frontera entre las dos es el bundle descrito en
[CONTRATO-BUNDLE.md](CONTRATO-BUNDLE.md). Nada de lo que se hace aquí toca la
base de datos de la webapp: el trabajo se entrega como fichero y alguien del
otro lado lo importa cuando lo da por bueno.

---

## 1. Puesta en marcha

Hace falta **Python 3.14** y **uv**. Todos los comandos se corren desde la raíz
del repo.

```bash
py -3.14 -m uv sync
```

Luego, la configuración:

```bash
cp .env.example .env
```

y en `.env` poner tu propia `GEMINI_API_KEY`, sacada de
[Google AI Studio](https://aistudio.google.com/apikey) con tu cuenta y tu
facturación. **La clave es personal y no se comparte ni se commitea**: `.env`
está en `.gitignore` y ahí se queda.

Las demás variables del `.env.example` ya vienen bien por defecto; solo dicen
dónde están los PDFs y dónde se escribe el SQLite.

Comprobación de que todo quedó en pie:

```bash
py -3.14 -m uv run pytest etl/tests
py -3.14 -m uv run pytest question_generator/tests
```

> Los dos `pytest` van por separado a propósito: cada paquete trae su propio
> `conftest.py` y pytest se atraganta si se le pasan los dos a la vez.

Los PDFs no viajan en git (pesan y no son públicos): se dejan a mano en
`data/raw_pdfs/`.

---

## 2. Cómo funciona el pipeline

Dos fases encadenadas, cada una con su CLI. Las dos escriben al mismo SQLite.

```
data/raw_pdfs/*.pdf
      │
      │  FASE 1 — etl/     (sin IA para el grueso; Gemini solo desempata dudas)
      │  ─────────────────────────────────────────────────────
      ├─► detección y parseo del índice        extraction/toc_parser.py
      ├─► extracción de layout con Docling     extraction/docling_adapter.py
      ├─► ensamblado del árbol                 hierarchy/assembler.py
      │      PARTE → Capítulo → Sección → Subsección
      ├─► consolidación de chunks de texto     chunking/consolidator.py
      └─► persistencia                         → manuals · nodes · chunks
      │
      │  FASE 2 — question_generator/   (Gemini, una llamada por nodo-hoja)
      │  ─────────────────────────────────────────────────────
      ├─► por cada nodo-hoja con texto: 1 pregunta + 4 opciones + justificación
      │      1 correcta · 1 confusa · 2 distractores
      ├─► validación de forma antes de guardar (roles, duplicados, longitudes)
      └─► persistencia          → generation_runs · questions · question_options
      │
      │  REVISIÓN — explorer/   (Streamlit local sobre este mismo SQLite)
      ├─► árbol jerárquico, chunks, TOC, elementos crudos del extractor
      ├─► preguntas con sus 6 opciones, cobertura por nodo, corridas y costo
      └─► marcar el validation_status de cada pregunta
      │
      │  FASE 3 — la entrega
      └─► qgen-export → bundle JSON + .sha256  ──►  lo importa la webapp
      │
      ▼
data/manuals.sqlite
```

**Nodo-hoja** es una sección del manual sin subsecciones por debajo: la unidad
sobre la que se genera cada pregunta. **Chunk** es el texto de esa sección ya
consolidado. **Corrida** (`generation_run`) es una invocación de `qgen-generate`
con un modelo y unas reglas fijas; un manual puede acumular varias.

---

## 3. Trabajar un manual, de principio a fin

### 3.1 Ingestar el PDF

```bash
py -3.14 -m uv run etl-ingest data/raw_pdfs/mi_manual.pdf
```

Con un PDF nuevo del que no se sabe cómo se porta, primero el bake-off entre los
dos extractores:

```bash
py -3.14 -m uv run etl-bakeoff data/raw_pdfs/mi_manual.pdf
```

### 3.2 Revisar el árbol ANTES de gastar tokens

Lo cómodo es abrir el revisor visual y mirar el manual entero:

```bash
py -3.14 -m uv run streamlit run explorer/src/explorer/Home.py
```

En **📄 Manual** están el reporte de calidad (cobertura de páginas, nodos
huérfanos, distribución por nivel), el **árbol jerárquico** expandible y los
chunks crudos. En **📑 TOC** se ve el índice parseado y qué entradas no
encontraron nodo —y al revés—, que es donde se nota que la extracción salió
torcida. En **🧱 Raw Elements** está lo que devolvió el extractor sin procesar.

Lo mismo por CLI, si prefieres:

```bash
py -3.14 -m uv run etl-inspect manuals          # ids y metadatos
py -3.14 -m uv run etl-inspect tree <manual_id> # la jerarquía completa
py -3.14 -m uv run etl-inspect node <node_id>   # un nodo con su texto
```

Si el árbol sale mal —índice mal detectado, capítulos colapsados en uno,
secciones que se comieron el texto de la siguiente— **el problema es de
extracción y se arregla ahí**. Generar preguntas sobre una jerarquía rota
produce preguntas rotas, y encima cuesta dinero.

### 3.3 Estimar el costo

```bash
py -3.14 -m uv run qgen-generate <manual_id> --dry-run
```

No llama a Gemini: solo cuenta nodos y tokens y saca el precio estimado.

### 3.4 Generar una muestra

```bash
py -3.14 -m uv run qgen-generate <manual_id> --limit 5
py -3.14 -m uv run qgen-stats <manual_id>
py -3.14 -m uv run qgen-inspect <question_id>
```

Cinco preguntas revisadas a mano revelan casi todos los problemas de prompt, y
cuestan lo que cuestan cinco preguntas. Saltarse este paso es la forma más cara
de descubrir que las justificaciones citan artículos que no existen.

### 3.5 Generar el manual completo

```bash
py -3.14 -m uv run qgen-generate <manual_id>              # modo inmediato
py -3.14 -m uv run qgen-generate <manual_id> --batch      # ~50% más barato
py -3.14 -m uv run qgen-generate <manual_id> --model pro  # modelo grande
```

- **immediate** (por defecto): cada llamada espera respuesta y persiste. Se ve
  el avance en vivo y se puede cortar a medias.
- **batch**: se manda un trabajo único y se recoge después. Cuesta la mitad pero
  puede tardar hasta 24 h.

```bash
py -3.14 -m uv run qgen-batch-status            # todos los batches en curso
py -3.14 -m uv run qgen-batch-status <run_id>   # uno concreto
```

Los dos modos comparten el mismo cache por documento (PDF + instrucciones +
reglas), así que el manual entero solo se paga completo en la primera llamada.

Otras opciones útiles:

```bash
py -3.14 -m uv run qgen-generate <manual_id> --node-id <id>   # un solo nodo
py -3.14 -m uv run qgen-generate <manual_id> --regenerate     # rehace las que ya hay
```

Sin `--regenerate`, volver a correr el comando genera **solo lo que falta**: es
la forma de completar un manual que quedó a medias.

#### Sin API: generar desde Claude Code

```bash
py -3.14 -m uv run qgen-claude exportar <manual_id>   # instrucción + ventanas pendientes
# Claude Code escribe data/claude_code/<código>/respuestas/<ventana>.json
py -3.14 -m uv run qgen-claude importar <manual_id>   # mismas revisiones, una corrida más
```

La carpeta `data/claude_code/<código>/` tiene la misma instrucción y los mismos
mensajes que recibiría Gemini. Solo se importan las ventanas pendientes con
respuesta; las demás siguen pendientes. La corrida queda con el modelo
`claude-opus-5-5`, modo `immediate` y costo 0. Los ejercicios nuevos entran
"a revisar": no hay verificación a ciegas.

#### Revisión de calidad desde Claude Code

```bash
py -3.14 -m uv run qgen-claude exportar-revision <manual_id>   # rúbrica + un lote por ventana
# Claude Code escribe data/claude_code/<código>/revision/veredictos/<ventana>.json
py -3.14 -m uv run qgen-claude importar-revision <manual_id>   # aplica los veredictos
```

La rúbrica (`revision/instruccion.md`) rechaza las preguntas sin sentido, fuera
de tema, con respuesta discutible, que no evalúan nada o repetidas en esencia.
`aceptar` → `valid`, `rechazar` → `rejected`, `dudosa` → `needs_review`. Solo se
revisan las preguntas sin decidir: lo que ya aprobó o rechazó una persona no se
toca. El veredicto, la calificación (1–5) y los motivos quedan en
`metadata_json["revision"]` y el explorador los muestra en cada pregunta.

### 3.6 Control de calidad

Cada pregunta lleva un `validation_status`:

| Estado | Qué significa | ¿Se le sirve al alumno? |
|---|---|---|
| ⏳ `pending` | recién generada, sin revisar | **sí** |
| ✅ `valid` | revisada y aprobada | **sí** |
| 🔎 `needs_review` | dudosa, hay que mirarla | no |
| 🚫 `rejected` | mala, descartada | no |

Es la palanca de calidad de este lado: una pregunta marcada `rejected` viaja en
el bundle y se importa, pero la webapp no la mete en ningún examen. Marcar es
preferible a borrar, porque deja constancia de que se revisó.

La revisión se hace en el explorador, en **❓ Preguntas**:

```bash
py -3.14 -m uv run streamlit run explorer/src/explorer/Home.py
```

Cada pregunta sale con su nodo de origen, las 4 opciones coloreadas por rol
—correcta, confusa, dos distractores— y su
justificación, y debajo el control para marcarla. Arriba están los contadores:
cuántas hay, cuántas se servirían, qué porcentaje de los nodos con texto tiene
pregunta y cuánto costaron las corridas. Se puede filtrar por estado, por
corrida o buscando en el enunciado.

Las otras dos pestañas son **Sin pregunta** —los nodos con texto que se
quedaron fuera, o sea lo que falta por generar— y **Corridas**, con el modelo,
el costo y los fallos de cada invocación de `qgen-generate`.

En el árbol de **📄 Manual** cada nodo lleva además un badge: `❓3` si tiene tres
preguntas y las tres se sirven, `❓1/3` si solo una llegaría a un examen, y
`⚠ sin pregunta` si tiene texto y nadie le generó nada.

Marcar el estado es **lo único que el explorador escribe**. No borra preguntas,
no dispara generaciones y no conoce la base de la webapp.

### 3.7 Entregar

```bash
py -3.14 -m uv run qgen-export <manual_id> --check   # valida sin escribir
py -3.14 -m uv run qgen-export <manual_id>           # escribe a data/bundles/
```

Salen **dos ficheros** —`cjm--20260817--v1.json` y su `.sha256`— y se entregan
juntos: sin el checksum, quien importa no puede comprobar que el bundle llegó
entero, y su importador se niega a seguir.

El exportador valida contra el contrato antes de escribir y aborta si algo no
cuadra. Los avisos (preguntas rechazadas, nodos que se quedaron sin pregunta) se
imprimen pero no bloquean: son para mirarlos, no necesariamente para arreglarlos.

Más opciones:

```bash
py -3.14 -m uv run qgen-export <manual_id> --run <run_id>   # una sola corrida
py -3.14 -m uv run qgen-export <manual_id> --revision 3     # fija el v{n}
py -3.14 -m uv run qgen-export <manual_id> --include-raw    # + respuesta cruda
```

El detalle del formato, campo por campo, está en
[CONTRATO-BUNDLE.md](CONTRATO-BUNDLE.md). Vale la pena leerlo una vez: explica
por qué el bundle identifica las cosas como las identifica, y qué se valida.

---

## 4. Dónde queda todo

Todo el pipeline persiste en **`data/manuals.sqlite`**, un único fichero local.

- No hay servidor de base de datos que levantar, ni Docker, ni migraciones.
- Ese fichero **no se versiona** (está en `.gitignore`). Lo que se versiona es
  el código; lo que se entrega es el bundle.
- Borrarlo y volver a correr el pipeline reconstruye todo desde los PDFs.
- Nada de lo que se haga aquí puede afectar a los alumnos: el contenido no
  existe para ellos hasta que alguien importa el bundle del otro lado.

Los bundles se escriben a `data/bundles/`, que tampoco se versiona.

---

## 5. Qué NO hay aquí, a propósito

- **La base de datos de la webapp.** Ningún módulo de este repo conoce su cadena
  de conexión. No hay nada que puedas romper desde aquí.
- **Credenciales de nadie más.** Tu `GEMINI_API_KEY` es tuya. Si alguna vez te
  pasan una clave por chat, no la metas en `metadata` ni en un fichero
  versionado: el exportador aborta si detecta algo con pinta de secreto dentro
  de un bundle, precisamente porque es más fácil de lo que parece.
- **El código de la webapp** y su histórico. Esta rama es huérfana: no comparte
  commits con el repo principal.

---

## 6. Herramientas y problemas conocidos

```bash
py -3.14 -m uv run ruff check etl/src question_generator/src explorer/src   # lint
py -3.14 -m uv run python explorer/scripts/smoke_imports.py   # ¿el explorador arranca?
```

**Unstructured y Python 3.14.** El segundo extractor no declara soporte oficial
para 3.14. Si su instalación falla, va como extra aparte:

```bash
py -3.14 -m uv pip install "unstructured[pdf]"
```

o se corre solo ese adaptador en un sub-entorno 3.12:

```bash
py -3.12 -m uv run --with "unstructured[pdf]" python -m etl.cli.bakeoff data/raw_pdfs/mi_manual.pdf
```

**torch con CUDA.** El workspace fija `torch` al índice `pytorch-cu128` porque
cu124 no publica ruedas para Python 3.14. Si no tienes GPU no pasa nada:
Docling corre en CPU, solo más despacio.

**El bundle salió `.json.gz`.** Es lo esperado por encima de 25 MB. Se entrega
igual, con su `.sha256`; el importador lo lee comprimido.

---

## 7. Los comandos, de un vistazo

| Comando | Para qué |
|---|---|
| `etl-bakeoff <pdf>` | comparar extractores sobre un PDF nuevo |
| `etl-ingest <pdf>` | ingestar el manual: jerarquía + chunks |
| `etl-inspect manuals \| tree <id> \| node <id>` | revisar lo ingestado |
| `qgen-generate <manual_id> --dry-run` | estimar el costo sin llamar a Gemini |
| `qgen-generate <manual_id> [--limit N] [--batch]` | generar preguntas |
| `qgen-batch-status [run_id]` | estado de los trabajos en batch |
| `qgen-stats <manual_id>` | cobertura y corridas del manual |
| `qgen-inspect <question_id>` | ver una pregunta con sus 4 opciones |
| `qgen-export <manual_id> [--check]` | empaquetar la entrega |
| `streamlit run explorer/src/explorer/Home.py` | abrir el revisor visual |

Todos se invocan como `py -3.14 -m uv run <comando>` desde la raíz del repo.
