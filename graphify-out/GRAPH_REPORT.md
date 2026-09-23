# Graph Report - onmy-military-library-contenido  (2026-09-23)

## Corpus Check
- 149 files · ~52,178 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 6, .example 1, .lock 1)

## Summary
- 1090 nodes · 2800 edges · 53 communities (43 shown, 10 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 303 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2ce67bfa`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- 1_📄_Manual.py
- test_bundle_spec.py
- session_scope
- qgen/pipeline.py
- Contrato: bundle de contenido v1
- profile.py
- 6_❓_Preguntas.py
- init_question_tables
- components/__init__.py
- types.py
- toc_parser.py
- data_access.py
- RawElement
- test_patterns.py
- bundle/__init__.py
- BaldorExerciseExtractor
- etl/pipeline.py
- import_reference_questions
- sqlite3
- get_profile
- debug_pymupdf.py
- test_questions_access.py
- export.py
- etl/models/schema.py
- smoke_imports.py
- temario.py
- test_export_page.py
- consolidator.py
- ElementKind
- test_baldor_patterns.py
- GenerationRun
- _bundle
- test_algebra_trigonometria_geometria_analitica.py
- estimate_cost.py
- `explorer/` — revisor visual del pipeline
- run_ref
- match_titulo
- test_calculo_una_variable.py
- _normalize
- etl
- workflows/graphify.md
- CLAUDE.md
- spec.py
- pydantic
- session.py
- hierarchy_tree.py
- validation/__init__.py
- typing

## God Nodes (most connected - your core abstractions)
1. `session_scope()` - 65 edges
2. `RawElement` - 40 edges
3. `init_question_tables()` - 34 edges
4. `Chunk` - 32 edges
5. `Node` - 30 edges
6. `ElementKind` - 29 edges
7. `HierarchyAssembler` - 29 edges
8. `Manual` - 29 edges
9. `build_bundle()` - 28 edges
10. `run_pipeline()` - 27 edges

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

## Communities (53 total, 10 thin omitted)

### Community 0 - "1_📄_Manual.py"
Cohesion: 0.17
Nodes (17): dotenv, get_manual(), get_int(), link_to(), Helpers for query-param navigation between pages. Streamlit's `st.query_params`…, Replace current query params with the given mapping (None values dropped)., Build an internal Streamlit link. `page_url` is the relative path Streamlit…, set_params() (+9 more)

### Community 1 - "test_bundle_spec.py"
Cohesion: 0.14
Nodes (25): copy, _errors(), El contrato del bundle: lo que se acepta y, sobre todo, lo que no. Cada caso de…, test_api_key_en_metadata_bloquea_la_entrega(), test_arbol_sin_raiz(), test_cadena_de_conexion_en_metadata_bloquea_la_entrega(), test_ciclo_en_el_arbol(), mutate() (+17 more)

### Community 2 - "session_scope"
Cohesion: 0.10
Nodes (45): Session, session_scope(), Exception, main(), _model_option(), _print_estimate(), _print_summary(), _progress_cb() (+37 more)

### Community 3 - "qgen/pipeline.py"
Cohesion: 0.05
Nodes (67): concurrent_futures, qgen_reference_repository, actual_cost_usd(), CostEstimate, doc_token_estimate(), estimate_run(), Cost accounting: predictions before a run + actual after. Pricing (USD per 1M…, `draft_calls` son las llamadas del creador (una por nodo): leen el mismo… (+59 more)

### Community 4 - "Contrato: bundle de contenido v1"
Cohesion: 0.05
Nodes (42): 1. Por qué existe, 2. Forma del fichero, 3. Estructura, 4. Identidad: las claves estables, 5. Las validaciones, 6. Los dos comandos, 7. Versionado del contrato, Aquí — `qgen-export` (+34 more)

### Community 5 - "profile.py"
Cohesion: 0.14
Nodes (28): HeadingCandidate, match_anexo(), match_baldor_capitulo(), match_baldor_caso(), match_baldor_inciso(), match_baldor_subseccion_romana(), match_baldor_tema_mayusculas(), match_bloque() (+20 more)

### Community 6 - "6_❓_Preguntas.py"
Cohesion: 0.10
Nodes (31): get_node_ancestors(), get_node_children(), get_node_siblings(), get_tree(), NodeSummary, Siblings = nodes sharing the same parent_id (or root nodes if parent is None)., Preguntas generadas — revisión visual, cobertura y corridas. Es la vista de la…, _render_question() (+23 more)

### Community 7 - "init_question_tables"
Cohesion: 0.05
Nodes (82): Inserta preguntas generadas directamente en el chat para el manual 11 (Álgebra…, seed_questions(), datetime, _isolate_data_dir(), fixture, Cada test obtiene un directorio de datos limpio y un SQLite aislado., _isolate_data_dir(), fixture (+74 more)

### Community 8 - "components/__init__.py"
Cohesion: 0.24
Nodes (8): kpi_row(), Render a row of `st.metric` cards. items is a list of (label, value,…, cache_data, Render a single PDF page to PNG bytes via PyMuPDF., Return PNG bytes of the given page (1-based), or None if unavailable. Cached so…, Convenience: render and display in one call., render_page(), render_page_widget()

### Community 9 - "types.py"
Cohesion: 0.12
Nodes (19): ABC, enum, ExtractorBase, Path, Common interface for layout extractors. Adapters (Docling, Unstructured, etc.)…, Run the extractor on a PDF and return normalized elements., DoclingAdapter, elements_from_document() (+11 more)

### Community 10 - "toc_parser.py"
Cohesion: 0.12
Nodes (23): detect_toc_pages(), _infer_depth(), _is_roman_only(), _lookback_marker(), _parse_page_number(), parse_toc(), _peek_parte_title(), BaseModel (+15 more)

### Community 11 - "data_access.py"
Cohesion: 0.16
Nodes (22): graphify, Chunk, _chunk_to_summary(), ChunkSummary, deserialize_extraction(), get_chunks_for_manual(), get_chunks_for_node(), get_extraction_cache() (+14 more)

### Community 12 - "RawElement"
Cohesion: 0.12
Nodes (19): TocResult, One layout element extracted from a PDF page. Both Docling and Unstructured…, RawElement, _Builder, HierarchyAssembler, HierarchyNode, _label_for_depth(), _peek_next_title() (+11 more)

### Community 13 - "test_patterns.py"
Cohesion: 0.13
Nodes (25): classify_heading(), match_articulo(), match_libro(), Compatibility shim: classify using the default 'manual' profile. New code…, Default classify_heading uses 'manual' profile — articles are not its concern…, test_anexo(), test_articulo_quater(), test_articulo_septimus() (+17 more)

### Community 14 - "bundle/__init__.py"
Cohesion: 0.18
Nodes (17): Bundle de contenido: la interfaz entre la generación de preguntas y la webapp., dumps(), Path, Serialización canónica: UTF-8, indentado a 2, sin escapar acentos., Escribe el bundle (comprimiendo si es grande) y su `.sha256`. Devuelve `(ruta…, Comprueba el `.sha256` que acompaña al bundle. Lanza si no cuadra., Lee un bundle `.json` o `.json.gz`. No valida: para eso está `validate`., read_bundle() (+9 more)

### Community 15 - "BaldorExerciseExtractor"
Cohesion: 0.12
Nodes (17): BaldorExercise, BaldorExerciseExtractor, flush_current(), Genera el texto estructurado del ejercicio para el prompt de generación de…, Analizador para extraer problemas numerados, procedimientos y soluciones., Extrae la lista de ejercicios presentes en un bloque de texto., Parsea el bloque de texto de un ejercicio individual extrayendo enunciado,…, Representa un ejercicio o problema extraído de Álgebra de Baldor. (+9 more)

### Community 16 - "etl/pipeline.py"
Cohesion: 0.10
Nodes (21): Inspect a cached docling extraction to find LIBRO/TITULO lines and Latin-suffix…, main(), _print_table(), command, Path, Run both extractors with persistence disabled and emit a comparison., _render_markdown(), cache_extraction() (+13 more)

### Community 17 - "import_reference_questions"
Cohesion: 0.18
Nodes (13): main(), command, Path, Carga un archivo de preguntas de ejemplo y las guarda en la base de datos., import_reference_questions(), load_reference_file(), Any, Path (+5 more)

### Community 19 - "get_profile"
Cohesion: 0.08
Nodes (37): auto_detect_profile(), get_profile(), Heuristic profile pick based on the first few elements' text. Looks for genre-…, Verifica que el perfil 'algebra_baldor' solo clasifica capítulos a nivel 0 y no…, En Álgebra de Baldor los únicos nodos son los 16 capítulos ('I. Suma' … 'XXXII.…, test_perfil_algebra_baldor_clasificacion(), test_perfil_algebra_baldor_solo_tiene_capitulos(), Perfil `geografia_moderna_mexico`: el temario de la imagen, como Capítulo ›… (+29 more)

### Community 20 - "debug_pymupdf.py"
Cohesion: 0.15
Nodes (10): collections, One-off debug script: inspect characters used as TOC leaders., main(), Path, Quick visual inspection of an in-memory hierarchy without persisting., fitz, pymupdf, rapidocr (+2 more)

### Community 21 - "test_questions_access.py"
Cohesion: 0.16
Nodes (13): Engine, main(), command, Path, init_db(), Create all tables. Idempotent — safe to run on existing DBs., _default_db_url(), get_engine() (+5 more)

### Community 22 - "export.py"
Cohesion: 0.22
Nodes (12): date, SHA-256 del PDF de origen, si sigue estando donde dice el manual., source_digest(), bundle_filename(), next_version(), Siguiente `v{n}` libre para este manual en `out_dir`. Se cuenta por manual y no…, slug(), main() (+4 more)

### Community 23 - "etl/models/schema.py"
Cohesion: 0.11
Nodes (26): DeclarativeBase, node(), command, Print the hierarchy of a manual as a tree., Show a node's breadcrumb plus its chunks (truncated)., tree(), Base, Manual (+18 more)

### Community 25 - "temario.py"
Cohesion: 0.16
Nodes (13): dataclasses, Extractor de ejercicios resueltos y problemas prácticos de Álgebra de Baldor., match_parte_temario(), Parte numerada de un temario ('1.1 Los elementos del proceso comunicativo').…, CapitulosConTemas, _norm(), _numero_de_tema(), Selección por temario: qué bloques, partes, capítulos o temas de un libro… (+5 more)

### Community 26 - "test_export_page.py"
Cohesion: 0.38
Nodes (6): AppTest, _open_page(), Pestaña "Exportar Bundle" de la página de preguntas, ejecutada con AppTest. La…, test_un_bundle_con_errores_no_se_ofrece_y_se_explica_por_que(), test_un_bundle_que_cumple_el_contrato_se_puede_descargar(), streamlit_testing_v1

### Community 27 - "consolidator.py"
Cohesion: 0.13
Nodes (18): Prueba unitaria del reordenamiento de fracciones romanas., ChunkConsolidator, ConsolidatedChunk, BaseModel, Consolida los elementos del cuerpo de cada nodo hoja en fragmentos con límite…, Convierte un número romano a entero, o None si no es válido., Reordena fracciones romanas que docling extrajo en orden incorrecto. Docling a…, persist_manual() (+10 more)

### Community 28 - "ElementKind"
Cohesion: 0.16
Nodes (20): docling_core_types_doc, DoclingDocument, ElementKind, StrEnum, Manual profile builds PARTE → Capítulo → Sección hierarchy from body., Legal-code profile builds Libro → Título → Capítulo → Artículo., Drop filters silence Cámara/DOF noise without losing real content., Reform annotations get attached as metadata on the relevant node. (+12 more)

### Community 29 - "test_baldor_patterns.py"
Cohesion: 0.17
Nodes (11): Pruebas unitarias para los patrones y jerarquía de Álgebra de Baldor., Verifica subcasos con letras tipo a) o b)., Verifica que los capítulos con numeración romana se reconocen con su ordinal y…, Verifica las subsecciones con números romanos en mayúsculas., Verifica el reconocimiento de los casos clásicos de factorización., Verifica encabezados conceptuales y reglas generales en mayúsculas sostenidas., test_match_baldor_capitulo_romanos(), test_match_baldor_casos() (+3 more)

### Community 30 - "GenerationRun"
Cohesion: 0.06
Nodes (54): functools, google, logging, os, _check_once(), main(), _print_run_card(), _print_running() (+46 more)

### Community 31 - "_bundle"
Cohesion: 0.20
Nodes (10): _bundle(), _options(), `cost_input_tokens` contiene 'token': el detector no debe morder ahí., Un bundle mínimo pero completo y válido., test_bundle_valido_pasa_sin_errores(), test_corrida_con_nodos_fallidos_avisa(), mutate(), test_los_contadores_de_tokens_no_son_un_secreto() (+2 more)

### Community 32 - "test_algebra_trigonometria_geometria_analitica.py"
Cohesion: 0.53
Nodes (5): Perfil `algebra_trigonometria_geometria_analitica`: los cuatro capítulos de la…, test_el_arbol_son_los_cuatro_capitulos_de_la_imagen(), test_la_portada_queda_fuera(), test_secciones_ejemplos_y_teoremas_quedan_en_el_cuerpo_de_su_capitulo(), _tree()

### Community 33 - "estimate_cost.py"
Cohesion: 0.67
Nodes (3): estimate_doc(), main(), Compute approximate Gemini cost for question generation across ingested…

### Community 36 - "`explorer/` — revisor visual del pipeline"
Cohesion: 0.29
Nodes (6): Cómo correr, El árbol y la cobertura, `explorer/` — revisor visual del pipeline, La revisión, Navegación, Vistas

### Community 37 - "run_ref"
Cohesion: 0.33
Nodes (7): iso(), datetime, Clave estable de una corrida: `{model}--{mode}--{inicio compacto UTC}`., Fecha en el formato del contrato: ISO 8601 UTC con `Z`. SQLite devuelve los…, run_ref(), test_fecha_ingenua_se_lee_como_utc(), test_ref_de_corrida_es_estable()

### Community 38 - "match_titulo"
Cohesion: 0.33
Nodes (6): match_titulo(), test_match_titulo(), test_titulo_compound_decimoprimero(), test_titulo_compound_decimotercero(), test_titulo_preliminar(), test_titulo_with_trailing_title()

### Community 40 - "test_calculo_una_variable.py"
Cohesion: 0.53
Nodes (5): Perfil `calculo_una_variable`: los tres capítulos completos de la imagen.…, test_el_arbol_son_los_tres_capitulos_de_la_imagen(), test_la_portada_queda_fuera(), test_secciones_y_subtitulos_quedan_en_el_cuerpo_de_su_capitulo(), _tree()

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
Nodes (14): contextlib, qgen_reference_importer, Comando CLI para importar un banco de preguntas de referencia (ejemplos oro) a…, Idempotent creation of the question-generation tables. Importing…, datetime, SQLAlchemy schema for generated questions. Hereda del mismo `Base` que…, _utcnow(), Pruebas unitarias para la importación y consulta de preguntas de referencia… (+6 more)

### Community 48 - "hierarchy_tree.py"
Cohesion: 0.36
Nodes (7): collections_abc, _icon_for(), _indent(), Hierarchy tree rendered as nested expanders with optional click-to-navigate., Render the manual's tree. `on_select` is a function that takes a NodeSummary…, _render_node(), render_tree()

### Community 57 - "typing"
Cohesion: 0.11
Nodes (22): csv, datetime, Esquema SQLAlchemy para preguntas de referencia (banco de ejemplos/exemplars).…, Retorna la fecha y hora actual en UTC., Modelo de base de datos para una pregunta de referencia u oro., Modelo de opción de respuesta para una pregunta de referencia., ReferenceOption, ReferenceQuestion (+14 more)

## Knowledge Gaps
- **36 isolated node(s):** `Workflow: graphify`, `graphify`, `graphify en Windows`, `1. Por qué existe`, `2. Forma del fichero` (+31 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 379 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `session_scope()` connect `session_scope` to `1_📄_Manual.py`, `estimate_cost.py`, `Contrato: bundle de contenido v1`, `6_❓_Preguntas.py`, `init_question_tables`, `data_access.py`, `pydantic`, `session.py`, `etl/pipeline.py`, `import_reference_questions`, `test_questions_access.py`, `export.py`, `etl/models/schema.py`, `consolidator.py`, `GenerationRun`?**
  _High betweenness centrality (0.128) - this node is a cross-community bridge._
- **Why does `RawElement` connect `RawElement` to `test_algebra_trigonometria_geometria_analitica.py`, `profile.py`, `test_calculo_una_variable.py`, `types.py`, `get_profile`, `temario.py`, `consolidator.py`, `ElementKind`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `RawElement` (e.g. with `ChunkConsolidator` and `UnstructuredAdapter`) actually correct?**
  _`RawElement` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `init_question_tables()` (e.g. with `seed_questions()` and `Base`) actually correct?**
  _`init_question_tables()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `Chunk` (e.g. with `main()` and `node()`) actually correct?**
  _`Chunk` has 25 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Workflow: graphify`, `graphify`, `graphify en Windows` to the rest of the system?**
  _36 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_bundle_spec.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13756613756613756 - nodes in this community are weakly interconnected._