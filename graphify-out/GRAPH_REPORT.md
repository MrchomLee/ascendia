# Graph Report - onmy-military-library-contenido  (2026-09-23)

## Corpus Check
- 145 files · ~49,208 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 6, .example 1, .lock 1)

## Summary
- 1053 nodes · 2708 edges · 55 communities (46 shown, 9 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 288 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `88d1b2b5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- 1_📄_Manual.py
- test_bundle_spec.py
- session_scope
- DocumentRules
- Contrato: bundle de contenido v1
- patterns.py
- 6_❓_Preguntas.py
- init_question_tables
- consolidator.py
- types.py
- toc_parser.py
- data_access.py
- RawElement
- test_patterns.py
- bundle/__init__.py
- BaldorExerciseExtractor
- etl/pipeline.py
- importer.py
- pytest
- get_profile
- debug_pymupdf.py
- import_examples.py
- export.py
- etl/models/schema.py
- smoke_imports.py
- temario.py
- session.py
- pathlib
- search.py
- test_baldor_patterns.py
- batch_status.py
- _bundle
- ElementKind
- report.py
- test_temario.py
- pdf_preview.py
- `explorer/` — revisor visual del pipeline
- run_ref
- profile.py
- test_historia_universal.py
- match_baldor_tema_mayusculas
- _normalize
- etl
- workflows/graphify.md
- CLAUDE.md
- spec.py
- json
- migration.py
- 2_🌳_Node.py
- validation/__init__.py

## God Nodes (most connected - your core abstractions)
1. `session_scope()` - 65 edges
2. `RawElement` - 37 edges
3. `init_question_tables()` - 34 edges
4. `Chunk` - 32 edges
5. `Node` - 30 edges
6. `Manual` - 29 edges
7. `build_bundle()` - 28 edges
8. `run_pipeline()` - 27 edges
9. `run_generation()` - 26 edges
10. `GenerationRun` - 25 edges

## Surprising Connections (you probably didn't know these)
- `4. Identidad: las claves estables` --references--> `manuals()`  [INFERRED]
  CONTRATO-BUNDLE.md → etl/src/etl/cli/inspect_cli.py
- `Notas por bloque` --references--> `manuals()`  [INFERRED]
  CONTRATO-BUNDLE.md → etl/src/etl/cli/inspect_cli.py
- `graphify` --references--> `get_node()`  [INFERRED]
  .agents/rules/graphify.md → explorer/src/explorer/data_access.py
- `5. Las validaciones` --references--> `run_ref()`  [INFERRED]
  CONTRATO-BUNDLE.md → question_generator/src/qgen/bundle/spec.py
- `_parse()` --uses--> `TocResult`  [INFERRED]
  explorer/src/explorer/pages/3_📑_TOC.py → etl/src/etl/extraction/toc_parser.py

## Import Cycles
- None detected.

## Communities (55 total, 9 thin omitted)

### Community 0 - "1_📄_Manual.py"
Cohesion: 0.15
Nodes (20): dotenv, kpi_row(), Render a row of `st.metric` cards. items is a list of (label, value,…, get_extraction_cache(), get_manual(), Reads `data/processed/<code>.<extractor>.json` for a manual. Returns the raw…, get_int(), link_to() (+12 more)

### Community 1 - "test_bundle_spec.py"
Cohesion: 0.14
Nodes (25): copy, _errors(), El contrato del bundle: lo que se acepta y, sobre todo, lo que no. Cada caso de…, test_api_key_en_metadata_bloquea_la_entrega(), test_arbol_sin_raiz(), test_cadena_de_conexion_en_metadata_bloquea_la_entrega(), test_ciclo_en_el_arbol(), mutate() (+17 more)

### Community 2 - "session_scope"
Cohesion: 0.05
Nodes (83): concurrent_futures, session_scope(), Exception, logging, main(), _model_option(), _print_estimate(), _print_summary() (+75 more)

### Community 3 - "DocumentRules"
Cohesion: 0.07
Nodes (49): _resolve_rules(), build_creator_instruction(), Plantillas de prompt para el agente Creador de Preguntas., Construye las instrucciones del sistema para el generador de preguntas. Args:…, build_variable_prompt(), _node_text(), Render the per-node variable prompt that goes alongside the cached context., Build the user message for a single node. The cached context already gave… (+41 more)

### Community 4 - "Contrato: bundle de contenido v1"
Cohesion: 0.05
Nodes (42): 1. Por qué existe, 2. Forma del fichero, 3. Estructura, 4. Identidad: las claves estables, 5. Las validaciones, 6. Los dos comandos, 7. Versionado del contrato, Aquí — `qgen-export` (+34 more)

### Community 5 - "patterns.py"
Cohesion: 0.16
Nodes (21): HeadingCandidate, match_anexo(), match_bloque(), match_capitulo(), match_ejercicio(), match_libro(), match_miscelanea(), match_parte() (+13 more)

### Community 6 - "6_❓_Preguntas.py"
Cohesion: 0.11
Nodes (29): datetime, Preguntas generadas — revisión visual, cobertura y corridas. Es la vista de la…, _render_question(), get_question_kpis(), list_questions(), list_runs(), nodes_missing_questions(), OptionView (+21 more)

### Community 7 - "init_question_tables"
Cohesion: 0.05
Nodes (84): AppTest, Inserta preguntas generadas directamente en el chat para el manual 11 (Álgebra…, seed_questions(), enum, _open_page(), Pestaña "Exportar Bundle" de la página de preguntas, ejecutada con AppTest. La…, _seed(), test_un_bundle_con_errores_no_se_ofrece_y_se_explica_por_que() (+76 more)

### Community 8 - "consolidator.py"
Cohesion: 0.15
Nodes (14): Prueba unitaria del reordenamiento de fracciones romanas., ChunkConsolidator, ConsolidatedChunk, BaseModel, Consolida los elementos del cuerpo de cada nodo hoja en fragmentos con límite…, Convierte un número romano a entero, o None si no es válido., Reordena fracciones romanas que docling extrajo en orden incorrecto. Docling a…, HierarchyNode (+6 more)

### Community 9 - "types.py"
Cohesion: 0.14
Nodes (16): ABC, ExtractorBase, Path, Common interface for layout extractors. Adapters (Docling, Unstructured, etc.)…, Run the extractor on a PDF and return normalized elements., DoclingAdapter, _first_bbox(), _first_page() (+8 more)

### Community 10 - "toc_parser.py"
Cohesion: 0.17
Nodes (18): detect_toc_pages(), _infer_depth(), _is_roman_only(), _lookback_marker(), _parse_page_number(), parse_toc(), _peek_parte_title(), BaseModel (+10 more)

### Community 11 - "data_access.py"
Cohesion: 0.12
Nodes (29): graphify, Chunk, _chunk_to_summary(), ChunkSummary, deserialize_extraction(), get_chunks_for_manual(), get_chunks_for_node(), get_global_kpis() (+21 more)

### Community 12 - "RawElement"
Cohesion: 0.13
Nodes (14): TocResult, One layout element extracted from a PDF page. Both Docling and Unstructured…, RawElement, _Builder, HierarchyAssembler, _label_for_depth(), _peek_next_title(), Assembles a tree from raw elements, optionally guided by a TOC. Parameters… (+6 more)

### Community 13 - "test_patterns.py"
Cohesion: 0.12
Nodes (27): classify_heading(), match_articulo(), match_titulo(), Compatibility shim: classify using the default 'manual' profile. New code…, Default classify_heading uses 'manual' profile — articles are not its concern…, test_anexo(), test_articulo_quater(), test_articulo_septimus() (+19 more)

### Community 14 - "bundle/__init__.py"
Cohesion: 0.18
Nodes (17): Bundle de contenido: la interfaz entre la generación de preguntas y la webapp., dumps(), Path, Serialización canónica: UTF-8, indentado a 2, sin escapar acentos., Escribe el bundle (comprimiendo si es grande) y su `.sha256`. Devuelve `(ruta…, Comprueba el `.sha256` que acompaña al bundle. Lanza si no cuadra., Lee un bundle `.json` o `.json.gz`. No valida: para eso está `validate`., read_bundle() (+9 more)

### Community 15 - "BaldorExerciseExtractor"
Cohesion: 0.12
Nodes (17): BaldorExercise, BaldorExerciseExtractor, flush_current(), Genera el texto estructurado del ejercicio para el prompt de generación de…, Analizador para extraer problemas numerados, procedimientos y soluciones., Extrae la lista de ejercicios presentes en un bloque de texto., Parsea el bloque de texto de un ejercicio individual extrayendo enunciado,…, Representa un ejercicio o problema extraído de Álgebra de Baldor. (+9 more)

### Community 16 - "etl/pipeline.py"
Cohesion: 0.29
Nodes (12): cache_extraction(), get_extractor(), _guess_code(), _guess_title(), load_cached_extraction(), PipelineResult, BaseModel, Path (+4 more)

### Community 17 - "importer.py"
Cohesion: 0.11
Nodes (21): csv, datetime, Esquema SQLAlchemy para preguntas de referencia (banco de ejemplos/exemplars).…, Retorna la fecha y hora actual en UTC., Modelo de base de datos para una pregunta de referencia u oro., Modelo de opción de respuesta para una pregunta de referencia., ReferenceOption, ReferenceQuestion (+13 more)

### Community 18 - "pytest"
Cohesion: 0.11
Nodes (15): _isolate_data_dir(), fixture, Cada test obtiene un directorio de datos limpio y un SQLite aislado., _find_sample(), Path, Smoke test for the TOC parser using the real DN M 1455 sample PDF. The test is…, test_dn_m_1455_toc_extraction(), _isolate_data_dir() (+7 more)

### Community 19 - "get_profile"
Cohesion: 0.15
Nodes (20): auto_detect_profile(), get_profile(), Heuristic profile pick based on the first few elements' text. Looks for genre-…, Verifica que el perfil 'algebra_baldor' solo clasifica capítulos a nivel 0 y no…, En Álgebra de Baldor los únicos nodos son los 16 capítulos ('I. Suma' … 'XXXII.…, test_perfil_algebra_baldor_clasificacion(), test_perfil_algebra_baldor_solo_tiene_capitulos(), _el() (+12 more)

### Community 20 - "debug_pymupdf.py"
Cohesion: 0.15
Nodes (10): collections, One-off debug script: inspect characters used as TOC leaders., main(), Path, Quick visual inspection of an in-memory hierarchy without persisting., fitz, pymupdf, rapidocr (+2 more)

### Community 21 - "import_examples.py"
Cohesion: 0.13
Nodes (17): qgen_reference_importer, qgen_reference_repository, main(), command, Path, Comando CLI para importar un banco de preguntas de referencia (ejemplos oro) a…, Carga un archivo de preguntas de ejemplo y las guarda en la base de datos., import_reference_questions() (+9 more)

### Community 22 - "export.py"
Cohesion: 0.22
Nodes (12): date, SHA-256 del PDF de origen, si sigue estando donde dice el manual., source_digest(), bundle_filename(), next_version(), Siguiente `v{n}` libre para este manual en `out_dir`. Se cuenta por manual y no…, slug(), main() (+4 more)

### Community 23 - "etl/models/schema.py"
Cohesion: 0.18
Nodes (17): DeclarativeBase, estimate_doc(), main(), Compute approximate Gemini cost for question generation across ingested…, node(), command, Print the hierarchy of a manual as a tree., Show a node's breadcrumb plus its chunks (truncated). (+9 more)

### Community 25 - "temario.py"
Cohesion: 0.24
Nodes (8): match_parte_temario(), Parte numerada de un temario ('1.1 Los elementos del proceso comunicativo').…, _norm(), Selección por temario: qué bloques, partes o temas de un libro entran al árbol.…, Devuelve los elementos (con su índice original) que entran al árbol. - El…, Reescribe como "TEMA n. Título" el encabezado de cada tema; el resto pasa tal…, Temario, TemasPorTitulo

### Community 26 - "session.py"
Cohesion: 0.18
Nodes (13): contextlib, Engine, main(), command, Path, init_db(), Create all tables. Idempotent — safe to run on existing DBs., _default_db_url() (+5 more)

### Community 27 - "pathlib"
Cohesion: 0.28
Nodes (7): persist_manual(), Path, Session, Maps in-memory pipeline objects (HierarchyTree, ConsolidatedChunk) to ORM rows., Persist a fully-processed manual. The whole transaction commits at…, test_persist_round_trip(), pathlib

### Community 28 - "search.py"
Cohesion: 0.28
Nodes (8): init_fts(), BaseModel, query(), Full-text search over chunks using SQLite FTS5. We create a virtual table…, FTS5 has reserved chars; we wrap free-form input as a phrase if needed., Create FTS5 virtual table + triggers if missing, then backfill any chunks that…, _sanitize(), SearchHit

### Community 29 - "test_baldor_patterns.py"
Cohesion: 0.11
Nodes (17): match_baldor_capitulo(), match_baldor_caso(), match_baldor_inciso(), match_baldor_subseccion_romana(), Reconoce subsecciones con números romanos y título en mayúsculas (ej. 'I. SUMA…, Reconoce capítulos con número romano directo (ej. 'I. Suma', 'IV.…, Reconoce casos clásicos de factorización (ej. 'CASO I: CUANDO TODOS...')., Reconoce subcasos con inciso alfabético (ej. 'a) Factor común monomio.'). (+9 more)

### Community 30 - "batch_status.py"
Cohesion: 0.15
Nodes (23): _check_once(), main(), _print_run_card(), _print_running(), command, CLI for monitoring + finalizing batch runs. Usage patterns -------------- 1)…, _state_name(), _wait_loop() (+15 more)

### Community 31 - "_bundle"
Cohesion: 0.20
Nodes (10): _bundle(), _options(), `cost_input_tokens` contiene 'token': el detector no debe morder ahí., Un bundle mínimo pero completo y válido., test_bundle_valido_pasa_sin_errores(), test_corrida_con_nodos_fallidos_avisa(), mutate(), test_los_contadores_de_tokens_no_son_un_secreto() (+2 more)

### Community 32 - "ElementKind"
Cohesion: 0.29
Nodes (11): ElementKind, StrEnum, Manual profile builds PARTE → Capítulo → Sección hierarchy from body., Legal-code profile builds Libro → Título → Capítulo → Artículo., Drop filters silence Cámara/DOF noise without losing real content., Reform annotations get attached as metadata on the relevant node., _t(), test_assemble_codigo_legal_basic() (+3 more)

### Community 33 - "report.py"
Cohesion: 0.43
Nodes (5): build_report(), BaseModel, Session, QualityReport, Quality report for an ingested manual. Computes: - TOC coverage: % of TOC…

### Community 34 - "test_temario.py"
Cohesion: 0.48
Nodes (6): Perfil `taller_lectura_redaccion`: solo el temario pedido, como Bloque › Parte.…, test_cada_parte_cuelga_de_su_bloque(), test_cada_parte_lleva_solo_su_texto(), test_lo_que_no_esta_en_la_imagen_no_queda_en_ningun_nodo(), test_solo_quedan_los_bloques_y_partes_de_la_imagen(), _tree()

### Community 35 - "pdf_preview.py"
Cohesion: 0.33
Nodes (6): cache_data, Render a single PDF page to PNG bytes via PyMuPDF., Return PNG bytes of the given page (1-based), or None if unavailable. Cached so…, Convenience: render and display in one call., render_page(), render_page_widget()

### Community 36 - "`explorer/` — revisor visual del pipeline"
Cohesion: 0.29
Nodes (6): Cómo correr, El árbol y la cobertura, `explorer/` — revisor visual del pipeline, La revisión, Navegación, Vistas

### Community 37 - "run_ref"
Cohesion: 0.33
Nodes (7): iso(), datetime, Clave estable de una corrida: `{model}--{mode}--{inicio compacto UTC}`., Fecha en el formato del contrato: ISO 8601 UTC con `Z`. SQLite devuelve los…, run_ref(), test_fecha_ingenua_se_lee_como_utc(), test_ref_de_corrida_es_estable()

### Community 38 - "profile.py"
Cohesion: 0.22
Nodes (7): dataclasses, Extractor de ejercicios resueltos y problemas prácticos de Álgebra de Baldor., Build a manual's hierarchy tree from extracted elements + optional TOC.…, HeadingMatch, Profile-resolved heading match: kind + numeric depth., Document profiles: which heading kinds and filters apply to which doc type.…, re

### Community 39 - "test_historia_universal.py"
Cohesion: 0.53
Nodes (5): Perfil `historia_universal`: el temario de la imagen, como Capítulo › Tema.…, test_cada_tema_cuelga_del_capitulo(), test_el_arbol_es_el_capitulo_y_sus_cuatro_temas(), test_los_subtitulos_quedan_en_el_cuerpo_de_su_tema(), _tree()

### Community 40 - "match_baldor_tema_mayusculas"
Cohesion: 0.50
Nodes (4): match_baldor_tema_mayusculas(), Reconoce encabezados conceptuales y reglas generales de Baldor en mayúsculas., Verifica encabezados conceptuales y reglas generales en mayúsculas sostenidas., test_match_baldor_temas_mayusculas()

### Community 41 - "_normalize"
Cohesion: 0.67
Nodes (3): _normalize(), Loose match: strip accents, lowercase, collapse whitespace., Título comparable: sin acentos, sin puntuación y en minúsculas. El TOC y los…

### Community 42 - "etl"
Cohesion: 1.00
Nodes (3): etl, explorer, question_generator

### Community 45 - "spec.py"
Cohesion: 0.21
Nodes (17): gzip, hashlib, _bool(), _dict(), find_secrets(), walk(), _int(), _is_iso() (+9 more)

### Community 46 - "json"
Cohesion: 0.06
Nodes (16): Inspect a cached docling extraction to find LIBRO/TITULO lines and Latin-suffix…, GeminiClient, Thin wrapper around google-genai with explicit context caching. We keep this…, ClassifiedHeading, GeminiHeadingClassifier, HeadingClassificationBatch, BaseModel, Gemini-based fallback classifier for ambiguous headings. Used only when the… (+8 more)

### Community 47 - "migration.py"
Cohesion: 0.20
Nodes (11): main(), _print_table(), command, Path, Run both extractors with persistence disabled and emit a comparison., _render_markdown(), Idempotent creation of the question-generation tables. Importing…, rich_console (+3 more)

### Community 48 - "2_🌳_Node.py"
Cohesion: 0.22
Nodes (14): collections_abc, _icon_for(), _indent(), Hierarchy tree rendered as nested expanders with optional click-to-navigate., Render the manual's tree. `on_select` is a function that takes a NodeSummary…, _render_node(), render_tree(), get_node_ancestors() (+6 more)

## Knowledge Gaps
- **36 isolated node(s):** `Workflow: graphify`, `graphify`, `graphify en Windows`, `1. Por qué existe`, `2. Forma del fichero` (+31 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 371 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `session_scope()` connect `session_scope` to `1_📄_Manual.py`, `Contrato: bundle de contenido v1`, `6_❓_Preguntas.py`, `init_question_tables`, `data_access.py`, `etl/pipeline.py`, `2_🌳_Node.py`, `import_examples.py`, `export.py`, `etl/models/schema.py`, `session.py`, `pathlib`, `search.py`, `batch_status.py`?**
  _High betweenness centrality (0.117) - this node is a cross-community bridge._
- **Why does `RawElement` connect `RawElement` to `ElementKind`, `test_temario.py`, `profile.py`, `test_historia_universal.py`, `consolidator.py`, `types.py`, `get_profile`, `temario.py`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `RawElement` (e.g. with `ChunkConsolidator` and `DoclingAdapter`) actually correct?**
  _`RawElement` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `init_question_tables()` (e.g. with `seed_questions()` and `Base`) actually correct?**
  _`init_question_tables()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `Chunk` (e.g. with `main()` and `node()`) actually correct?**
  _`Chunk` has 25 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Workflow: graphify`, `graphify`, `graphify en Windows` to the rest of the system?**
  _36 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `1_📄_Manual.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1455026455026455 - nodes in this community are weakly interconnected._