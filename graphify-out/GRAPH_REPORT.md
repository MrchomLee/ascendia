# Graph Report - onmy-military-library-contenido  (2026-09-22)

## Corpus Check
- 141 files · ~46,322 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 6, .example 1, .lock 1)

## Summary
- 999 nodes · 2555 edges · 55 communities (46 shown, 9 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 265 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `06c6162a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- 1_📄_Manual.py
- test_bundle_spec.py
- qgen/pipeline.py
- DocumentRules
- Contrato: bundle de contenido v1
- profile.py
- 6_❓_Preguntas.py
- GenerationRun
- consolidator.py
- types.py
- toc_parser.py
- data_access.py
- assembler.py
- test_patterns.py
- bundle/__init__.py
- BaldorExerciseExtractor
- etl/pipeline.py
- typing
- session_scope
- get_profile
- GeneratedQuestion
- json
- cache.py
- etl/models/schema.py
- smoke_imports.py
- gemini/generate.py
- init_db
- init_question_tables
- os
- test_baldor_patterns.py
- batch.py
- _bundle
- ElementKind
- batch_status.py
- cli/generate.py
- test_data_access.py
- `explorer/` — revisor visual del pipeline
- run_ref
- hierarchy/__init__.py
- OptionExemplarInput
- match_libro
- _normalize
- etl
- workflows/graphify.md
- CLAUDE.md
- spec.py
- pydantic
- session.py
- hierarchy_tree.py
- validation/__init__.py

## God Nodes (most connected - your core abstractions)
1. `session_scope()` - 60 edges
2. `init_question_tables()` - 33 edges
3. `Chunk` - 31 edges
4. `RawElement` - 28 edges
5. `Manual` - 28 edges
6. `Node` - 28 edges
7. `build_bundle()` - 28 edges
8. `run_pipeline()` - 27 edges
9. `GenerationRun` - 25 edges
10. `_errors()` - 25 edges

## Surprising Connections (you probably didn't know these)
- `4. Identidad: las claves estables` --references--> `manuals()`  [INFERRED]
  CONTRATO-BUNDLE.md → etl/src/etl/cli/inspect_cli.py
- `Notas por bloque` --references--> `manuals()`  [INFERRED]
  CONTRATO-BUNDLE.md → etl/src/etl/cli/inspect_cli.py
- `graphify` --references--> `get_node()`  [INFERRED]
  .agents/rules/graphify.md → explorer/src/explorer/data_access.py
- `5. Las validaciones` --references--> `run_ref()`  [INFERRED]
  CONTRATO-BUNDLE.md → question_generator/src/qgen/bundle/spec.py
- `seed_questions()` --calls--> `init_question_tables()`  [INFERRED]
  data/scratch/seed_questions_manual_11.py → question_generator/src/qgen/db/migration.py

## Import Cycles
- None detected.

## Communities (55 total, 9 thin omitted)

### Community 0 - "1_📄_Manual.py"
Cohesion: 0.12
Nodes (26): dotenv, kpi_row(), Render a row of `st.metric` cards. items is a list of (label, value,…, cache_data, Render a single PDF page to PNG bytes via PyMuPDF., Return PNG bytes of the given page (1-based), or None if unavailable. Cached so…, Convenience: render and display in one call., render_page() (+18 more)

### Community 1 - "test_bundle_spec.py"
Cohesion: 0.14
Nodes (25): copy, _errors(), El contrato del bundle: lo que se acepta y, sobre todo, lo que no. Cada caso de…, test_api_key_en_metadata_bloquea_la_entrega(), test_arbol_sin_raiz(), test_cadena_de_conexion_en_metadata_bloquea_la_entrega(), test_ciclo_en_el_arbol(), mutate() (+17 more)

### Community 2 - "qgen/pipeline.py"
Cohesion: 0.14
Nodes (21): concurrent_futures, dataclasses, logging, actual_cost_usd(), CostEstimate, doc_token_estimate(), estimate_run(), Cost accounting: predictions before a run + actual after. Pricing (USD per 1M… (+13 more)

### Community 3 - "DocumentRules"
Cohesion: 0.07
Nodes (46): _resolve_rules(), build_creator_instruction(), Plantillas de prompt para el agente Creador de Preguntas., Construye las instrucciones del sistema para el generador de preguntas. Args:…, build_variable_prompt(), _node_text(), Render the per-node variable prompt that goes alongside the cached context., Build the user message for a single node. The cached context already gave… (+38 more)

### Community 4 - "Contrato: bundle de contenido v1"
Cohesion: 0.05
Nodes (42): 1. Por qué existe, 2. Forma del fichero, 3. Estructura, 4. Identidad: las claves estables, 5. Las validaciones, 6. Los dos comandos, 7. Versionado del contrato, Aquí — `qgen-export` (+34 more)

### Community 5 - "profile.py"
Cohesion: 0.17
Nodes (24): HeadingCandidate, match_anexo(), match_baldor_capitulo(), match_baldor_caso(), match_baldor_inciso(), match_baldor_subseccion_romana(), match_baldor_tema_mayusculas(), match_capitulo() (+16 more)

### Community 6 - "6_❓_Preguntas.py"
Cohesion: 0.11
Nodes (28): Preguntas generadas — revisión visual, cobertura y corridas. Es la vista de la…, _render_question(), get_question_kpis(), list_questions(), list_runs(), nodes_missing_questions(), OptionView, BaseModel (+20 more)

### Community 7 - "GenerationRun"
Cohesion: 0.14
Nodes (29): seed_questions(), Siembra manual, nodo, corrida y preguntas para pruebas., _seed_questions_data(), main(), command, main(), command, create_run() (+21 more)

### Community 8 - "consolidator.py"
Cohesion: 0.12
Nodes (20): Prueba unitaria del reordenamiento de fracciones romanas., ChunkConsolidator, ConsolidatedChunk, BaseModel, Consolida los elementos del cuerpo de cada nodo hoja en fragmentos con límite…, Convierte un número romano a entero, o None si no es válido., Reordena fracciones romanas que docling extrajo en orden incorrecto. Docling a…, persist_manual() (+12 more)

### Community 9 - "types.py"
Cohesion: 0.13
Nodes (18): ABC, ExtractorBase, Path, Common interface for layout extractors. Adapters (Docling, Unstructured, etc.)…, Run the extractor on a PDF and return normalized elements., DoclingAdapter, _first_bbox(), _first_page() (+10 more)

### Community 10 - "toc_parser.py"
Cohesion: 0.07
Nodes (33): detect_toc_pages(), _infer_depth(), _is_roman_only(), _lookback_marker(), _parse_page_number(), parse_toc(), _peek_parte_title(), BaseModel (+25 more)

### Community 11 - "data_access.py"
Cohesion: 0.14
Nodes (28): graphify, Chunk, _chunk_to_summary(), ChunkSummary, get_chunks_for_manual(), get_chunks_for_node(), get_extraction_cache(), get_manual() (+20 more)

### Community 12 - "assembler.py"
Cohesion: 0.15
Nodes (14): TocResult, One layout element extracted from a PDF page. Both Docling and Unstructured…, RawElement, _Builder, HierarchyAssembler, _label_for_depth(), _peek_next_title(), Build a manual's hierarchy tree from extracted elements + optional TOC.… (+6 more)

### Community 13 - "test_patterns.py"
Cohesion: 0.12
Nodes (28): classify_heading(), match_articulo(), match_titulo(), Compatibility shim: classify using the default 'manual' profile. New code…, Default classify_heading uses 'manual' profile — articles are not its concern…, test_anexo(), test_articulo_quater(), test_articulo_septimus() (+20 more)

### Community 14 - "bundle/__init__.py"
Cohesion: 0.13
Nodes (25): date, SHA-256 del PDF de origen, si sigue estando donde dice el manual., source_digest(), Bundle de contenido: la interfaz entre la generación de preguntas y la webapp., bundle_filename(), next_version(), Path, Siguiente `v{n}` libre para este manual en `out_dir`. Se cuenta por manual y no… (+17 more)

### Community 15 - "BaldorExerciseExtractor"
Cohesion: 0.11
Nodes (18): BaldorExercise, BaldorExerciseExtractor, flush_current(), Extractor de ejercicios resueltos y problemas prácticos de Álgebra de Baldor., Genera el texto estructurado del ejercicio para el prompt de generación de…, Analizador para extraer problemas numerados, procedimientos y soluciones., Extrae la lista de ejercicios presentes en un bloque de texto., Parsea el bloque de texto de un ejercicio individual extrayendo enunciado,… (+10 more)

### Community 16 - "etl/pipeline.py"
Cohesion: 0.17
Nodes (17): main(), _print_table(), command, Path, Run both extractors with persistence disabled and emit a comparison., _render_markdown(), cache_extraction(), _guess_code() (+9 more)

### Community 17 - "typing"
Cohesion: 0.09
Nodes (30): csv, main(), command, Path, Carga un archivo de preguntas de ejemplo y las guarda en la base de datos., datetime, Esquema SQLAlchemy para preguntas de referencia (banco de ejemplos/exemplars).…, Retorna la fecha y hora actual en UTC. (+22 more)

### Community 18 - "session_scope"
Cohesion: 0.31
Nodes (17): session_scope(), run_generation(), FakeGemini, _question(), _question_count(), Orquestación de `qgen-generate` de principio a fin, con Gemini simulado. Aquí…, Sustituye cache, creador y generador de opciones del pipeline., _runs() (+9 more)

### Community 19 - "get_profile"
Cohesion: 0.20
Nodes (16): auto_detect_profile(), get_profile(), Heuristic profile pick based on the first few elements' text. Looks for genre-…, _el(), test_autodetect_algebra_baldor(), test_autodetect_codigo_legal(), test_autodetect_falls_back_to_manual_for_empty(), test_autodetect_manual() (+8 more)

### Community 20 - "GeneratedQuestion"
Cohesion: 0.09
Nodes (29): collections, Inserta preguntas generadas directamente en el chat para el manual 11 (Álgebra…, enum, One-off debug script: inspect characters used as TOC leaders., main(), Path, Quick visual inspection of an in-memory hierarchy without persisting., fitz (+21 more)

### Community 21 - "json"
Cohesion: 0.12
Nodes (4): Inspect a cached docling extraction to find LIBRO/TITULO lines and Latin-suffix…, json, pickle, sqlite3

### Community 22 - "cache.py"
Cohesion: 0.20
Nodes (12): build_or_get_cache(), delete_cache(), DocumentCache, Path, Explicit-cache management for question generation. We cache once per (manual,…, Upload the PDF (Files API) and create an explicit cache. Returns a…, Best-effort cleanup. Used after a run to avoid storage costs., _wait_file_active() (+4 more)

### Community 23 - "etl/models/schema.py"
Cohesion: 0.14
Nodes (21): DeclarativeBase, estimate_doc(), main(), Compute approximate Gemini cost for question generation across ingested…, node(), command, Print the hierarchy of a manual as a tree., Show a node's breadcrumb plus its chunks (truncated). (+13 more)

### Community 25 - "gemini/generate.py"
Cohesion: 0.21
Nodes (14): DraftOutcome, _extract_usage(), generate_draft_questions(), generate_one(), _generate_with_retry(), GenerationOutcome, Immediate-mode generation: one call → one parsed GeneratedQuestion., Enunciados propuestos por el creador, con los tokens que costó pedirlos. (+6 more)

### Community 26 - "init_db"
Cohesion: 0.19
Nodes (11): Engine, main(), command, Path, init_db(), Create all tables. Idempotent — safe to run on existing DBs., _default_db_url(), get_engine() (+3 more)

### Community 27 - "init_question_tables"
Cohesion: 0.14
Nodes (29): datetime, build_bundle(), DuplicateNodeRef, DuplicateRunRef, _materia_hint(), _pipeline_commit(), Any, Session (+21 more)

### Community 28 - "os"
Cohesion: 0.29
Nodes (4): google, os, requests, urllib_request

### Community 29 - "test_baldor_patterns.py"
Cohesion: 0.14
Nodes (13): Pruebas unitarias para los patrones y jerarquía de Álgebra de Baldor., Verifica subcasos con letras tipo a) o b)., Verifica que el perfil 'algebra_baldor' solo clasifica capítulos a nivel 0 y no…, Verifica que los capítulos con numeración romana se reconocen con su ordinal y…, Verifica las subsecciones con números romanos en mayúsculas., Verifica el reconocimiento de los casos clásicos de factorización., Verifica encabezados conceptuales y reglas generales en mayúsculas sostenidas., test_match_baldor_capitulo_romanos() (+5 more)

### Community 30 - "batch.py"
Cohesion: 0.22
Nodes (12): BatchItemResult, BatchRequest, BatchSubmitResult, _build_inline_request(), parse_batch_results(), Batch-mode generation: submit one job for all nodes, poll, parse later. Trade-…, Yield BatchItemResult entries. Prefers matching by…, One request to include in the batch. ``key`` ties it back to a node id. (+4 more)

### Community 31 - "_bundle"
Cohesion: 0.15
Nodes (13): dumps(), Serialización canónica: UTF-8, indentado a 2, sin escapar acentos., _bundle(), _options(), `cost_input_tokens` contiene 'token': el detector no debe morder ahí., Un bundle mínimo pero completo y válido., test_bundle_valido_pasa_sin_errores(), test_corrida_con_nodos_fallidos_avisa() (+5 more)

### Community 32 - "ElementKind"
Cohesion: 0.29
Nodes (11): ElementKind, StrEnum, Manual profile builds PARTE → Capítulo → Sección hierarchy from body., Legal-code profile builds Libro → Título → Capítulo → Artículo., Drop filters silence Cámara/DOF noise without losing real content., Reform annotations get attached as metadata on the relevant node., _t(), test_assemble_codigo_legal_basic() (+3 more)

### Community 33 - "batch_status.py"
Cohesion: 0.38
Nodes (11): _check_once(), main(), _print_run_card(), _print_running(), command, CLI for monitoring + finalizing batch runs. Usage patterns -------------- 1)…, _state_name(), _wait_loop() (+3 more)

### Community 34 - "cli/generate.py"
Cohesion: 0.29
Nodes (10): main(), _model_option(), _print_estimate(), _print_summary(), _progress_cb(), command, Accept short aliases ('flash', 'pro') or full names; return canonical model id., resolve_model() (+2 more)

### Community 35 - "test_data_access.py"
Cohesion: 0.28
Nodes (8): get_global_kpis(), Pruebas unitarias para la capa de acceso a datos del explorador…, Verifica la consulta de detalles de un manual específico., Siembra datos de prueba para manuales, nodos y chunks., Verifica el listado de manuales y los KPIs globales del explorador., _seed_sample_data(), test_get_manual_detail(), test_list_manuals_y_global_kpis()

### Community 36 - "`explorer/` — revisor visual del pipeline"
Cohesion: 0.29
Nodes (6): Cómo correr, El árbol y la cobertura, `explorer/` — revisor visual del pipeline, La revisión, Navegación, Vistas

### Community 37 - "run_ref"
Cohesion: 0.33
Nodes (7): iso(), datetime, Clave estable de una corrida: `{model}--{mode}--{inicio compacto UTC}`., Fecha en el formato del contrato: ISO 8601 UTC con `Z`. SQLite devuelve los…, run_ref(), test_fecha_ingenua_se_lee_como_utc(), test_ref_de_corrida_es_estable()

### Community 38 - "hierarchy/__init__.py"
Cohesion: 0.40
Nodes (3): HeadingMatch, Profile-resolved heading match: kind + numeric depth., Return a profile-resolved HeadingMatch, or None if not a heading.

### Community 39 - "OptionExemplarInput"
Cohesion: 0.40
Nodes (5): OptionExemplarInput, BaseModel, QuestionExemplarInput, Modelo Pydantic para validar una opción de respuesta de ejemplo., Modelo Pydantic para validar una pregunta de ejemplo completa.

### Community 40 - "match_libro"
Cohesion: 0.50
Nodes (4): match_libro(), test_libro_with_trailing_title(), test_match_libro(), test_match_libro_with_accents()

### Community 41 - "_normalize"
Cohesion: 0.67
Nodes (3): _normalize(), Loose match: strip accents, lowercase, collapse whitespace., Título comparable: sin acentos, sin puntuación y en minúsculas. El TOC y los…

### Community 42 - "etl"
Cohesion: 1.00
Nodes (3): etl, explorer, question_generator

### Community 45 - "spec.py"
Cohesion: 0.21
Nodes (17): gzip, hashlib, _bool(), _dict(), find_secrets(), walk(), _int(), _is_iso() (+9 more)

### Community 46 - "pydantic"
Cohesion: 0.10
Nodes (17): GeminiClient, Thin wrapper around google-genai with explicit context caching. We keep this…, ClassifiedHeading, GeminiHeadingClassifier, HeadingClassificationBatch, BaseModel, Gemini-based fallback classifier for ambiguous headings. Used only when the…, init_fts() (+9 more)

### Community 47 - "session.py"
Cohesion: 0.17
Nodes (13): contextlib, functools, qgen_reference_importer, qgen_reference_repository, `qgen-export` — empaqueta un manual en un bundle JSON para entregarlo. Es la…, Comando CLI para importar un banco de preguntas de referencia (ejemplos oro) a…, Idempotent creation of the question-generation tables. Importing…, Pruebas unitarias para la importación y consulta de preguntas de referencia… (+5 more)

### Community 48 - "hierarchy_tree.py"
Cohesion: 0.36
Nodes (7): collections_abc, _icon_for(), _indent(), Hierarchy tree rendered as nested expanders with optional click-to-navigate., Render the manual's tree. `on_select` is a function that takes a NodeSummary…, _render_node(), render_tree()

## Knowledge Gaps
- **35 isolated node(s):** `Workflow: graphify`, `graphify`, `1. Por qué existe`, `2. Forma del fichero`, `Lo que queda fuera del bundle a propósito` (+30 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 354 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `session_scope()` connect `session_scope` to `1_📄_Manual.py`, `batch_status.py`, `cli/generate.py`, `test_data_access.py`, `Contrato: bundle de contenido v1`, `6_❓_Preguntas.py`, `GenerationRun`, `consolidator.py`, `data_access.py`, `pydantic`, `session.py`, `etl/pipeline.py`, `bundle/__init__.py`, `typing`, `etl/models/schema.py`, `init_db`, `init_question_tables`?**
  _High betweenness centrality (0.118) - this node is a cross-community bridge._
- **Why does `manuals()` connect `Contrato: bundle de contenido v1` to `session_scope`, `etl/models/schema.py`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `init_question_tables()` (e.g. with `seed_questions()` and `Base`) actually correct?**
  _`init_question_tables()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `Chunk` (e.g. with `main()` and `node()`) actually correct?**
  _`Chunk` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `RawElement` (e.g. with `ChunkConsolidator` and `DoclingAdapter`) actually correct?**
  _`RawElement` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Workflow: graphify`, `graphify`, `1. Por qué existe` to the rest of the system?**
  _35 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `1_📄_Manual.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11587301587301588 - nodes in this community are weakly interconnected._