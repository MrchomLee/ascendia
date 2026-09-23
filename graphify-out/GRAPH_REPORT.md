# Graph Report - onmy-military-library-contenido  (2026-09-23)

## Corpus Check
- 148 files · ~51,452 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 6, .example 1, .lock 1)

## Summary
- 1083 nodes · 2784 edges · 57 communities (48 shown, 9 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 301 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `44c3ce5a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- 1_📄_Manual.py
- test_bundle_spec.py
- session_scope
- build_system_instruction
- Contrato: bundle de contenido v1
- profile.py
- 6_❓_Preguntas.py
- init_question_tables
- ChunkConsolidator
- types.py
- toc_parser.py
- data_access.py
- RawElement
- test_patterns.py
- bundle/__init__.py
- BaldorExerciseExtractor
- run_pipeline
- import_reference_questions
- qgen/pipeline.py
- get_profile
- debug_pymupdf.py
- json
- main
- Chunk
- smoke_imports.py
- temario.py
- get_default_rules
- etl/pipeline.py
- ElementKind
- test_baldor_patterns.py
- GenerationRun
- _bundle
- build_variable_prompt
- DocumentRules
- test_temario.py
- report.py
- `explorer/` — revisor visual del pipeline
- run_ref
- match_titulo
- test_historia_universal.py
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
- test_geografia_moderna_mexico.py
- OptionExemplarInput

## God Nodes (most connected - your core abstractions)
1. `session_scope()` - 65 edges
2. `RawElement` - 39 edges
3. `init_question_tables()` - 34 edges
4. `Chunk` - 32 edges
5. `Node` - 30 edges
6. `ElementKind` - 29 edges
7. `Manual` - 29 edges
8. `HierarchyAssembler` - 28 edges
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

## Communities (57 total, 9 thin omitted)

### Community 0 - "1_📄_Manual.py"
Cohesion: 0.12
Nodes (25): dotenv, kpi_row(), Render a row of `st.metric` cards. items is a list of (label, value,…, cache_data, Render a single PDF page to PNG bytes via PyMuPDF., Return PNG bytes of the given page (1-based), or None if unavailable. Cached so…, Convenience: render and display in one call., render_page() (+17 more)

### Community 1 - "test_bundle_spec.py"
Cohesion: 0.14
Nodes (25): copy, _errors(), El contrato del bundle: lo que se acepta y, sobre todo, lo que no. Cada caso de…, test_api_key_en_metadata_bloquea_la_entrega(), test_arbol_sin_raiz(), test_cadena_de_conexion_en_metadata_bloquea_la_entrega(), test_ciclo_en_el_arbol(), mutate() (+17 more)

### Community 2 - "session_scope"
Cohesion: 0.11
Nodes (41): session_scope(), Exception, main(), _model_option(), _print_estimate(), _print_summary(), _progress_cb(), command (+33 more)

### Community 3 - "build_system_instruction"
Cohesion: 0.11
Nodes (18): build_creator_instruction(), Plantillas de prompt para el agente Creador de Preguntas., Construye las instrucciones del sistema para el generador de preguntas. Args:…, build_system_instruction(), Any, Construcción de la instrucción del sistema (System Instruction Builder).…, Construye las instrucciones del sistema para la estructuración de opciones.…, Pruebas unitarias para las reglas y prompts de generación de preguntas de… (+10 more)

### Community 4 - "Contrato: bundle de contenido v1"
Cohesion: 0.05
Nodes (42): 1. Por qué existe, 2. Forma del fichero, 3. Estructura, 4. Identidad: las claves estables, 5. Las validaciones, 6. Los dos comandos, 7. Versionado del contrato, Aquí — `qgen-export` (+34 more)

### Community 5 - "profile.py"
Cohesion: 0.14
Nodes (28): HeadingCandidate, match_anexo(), match_baldor_capitulo(), match_baldor_caso(), match_baldor_inciso(), match_baldor_subseccion_romana(), match_baldor_tema_mayusculas(), match_bloque() (+20 more)

### Community 6 - "6_❓_Preguntas.py"
Cohesion: 0.11
Nodes (29): datetime, Preguntas generadas — revisión visual, cobertura y corridas. Es la vista de la…, _render_question(), get_question_kpis(), list_questions(), list_runs(), nodes_missing_questions(), OptionView (+21 more)

### Community 7 - "init_question_tables"
Cohesion: 0.06
Nodes (71): AppTest, Inserta preguntas generadas directamente en el chat para el manual 11 (Álgebra…, seed_questions(), _open_page(), Pestaña "Exportar Bundle" de la página de preguntas, ejecutada con AppTest. La…, _seed(), test_un_bundle_con_errores_no_se_ofrece_y_se_explica_por_que(), test_un_bundle_que_cumple_el_contrato_se_puede_descargar() (+63 more)

### Community 8 - "ChunkConsolidator"
Cohesion: 0.24
Nodes (7): ChunkConsolidator, Convierte un número romano a entero, o None si no es válido., Reordena fracciones romanas que docling extrajo en orden incorrecto. Docling a…, _node(), test_chunker_keeps_short_text_in_one_chunk(), test_chunker_splits_long_text(), test_table_marker_is_set()

### Community 9 - "types.py"
Cohesion: 0.12
Nodes (20): ABC, enum, ExtractorBase, Path, Common interface for layout extractors. Adapters (Docling, Unstructured, etc.)…, Run the extractor on a PDF and return normalized elements., DoclingAdapter, elements_from_document() (+12 more)

### Community 10 - "toc_parser.py"
Cohesion: 0.07
Nodes (33): detect_toc_pages(), _infer_depth(), _is_roman_only(), _lookback_marker(), _parse_page_number(), parse_toc(), _peek_parte_title(), BaseModel (+25 more)

### Community 11 - "data_access.py"
Cohesion: 0.16
Nodes (25): graphify, _chunk_to_summary(), ChunkSummary, deserialize_extraction(), get_chunks_for_manual(), get_chunks_for_node(), get_extraction_cache(), get_manual() (+17 more)

### Community 12 - "RawElement"
Cohesion: 0.11
Nodes (18): TocResult, One layout element extracted from a PDF page. Both Docling and Unstructured…, RawElement, _Builder, HierarchyAssembler, HierarchyNode, _label_for_depth(), _peek_next_title() (+10 more)

### Community 13 - "test_patterns.py"
Cohesion: 0.13
Nodes (25): classify_heading(), match_articulo(), match_libro(), Compatibility shim: classify using the default 'manual' profile. New code…, Default classify_heading uses 'manual' profile — articles are not its concern…, test_anexo(), test_articulo_quater(), test_articulo_septimus() (+17 more)

### Community 14 - "bundle/__init__.py"
Cohesion: 0.20
Nodes (16): Bundle de contenido: la interfaz entre la generación de preguntas y la webapp., dumps(), Path, Serialización canónica: UTF-8, indentado a 2, sin escapar acentos., Escribe el bundle (comprimiendo si es grande) y su `.sha256`. Devuelve `(ruta…, Comprueba el `.sha256` que acompaña al bundle. Lanza si no cuadra., Lee un bundle `.json` o `.json.gz`. No valida: para eso está `validate`., read_bundle() (+8 more)

### Community 15 - "BaldorExerciseExtractor"
Cohesion: 0.12
Nodes (17): BaldorExercise, BaldorExerciseExtractor, flush_current(), Genera el texto estructurado del ejercicio para el prompt de generación de…, Analizador para extraer problemas numerados, procedimientos y soluciones., Extrae la lista de ejercicios presentes en un bloque de texto., Parsea el bloque de texto de un ejercicio individual extrayendo enunciado,…, Representa un ejercicio o problema extraído de Álgebra de Baldor. (+9 more)

### Community 16 - "run_pipeline"
Cohesion: 0.17
Nodes (17): main(), _print_table(), command, Path, Run both extractors with persistence disabled and emit a comparison., _render_markdown(), cache_extraction(), get_extractor() (+9 more)

### Community 17 - "import_reference_questions"
Cohesion: 0.17
Nodes (13): main(), command, Path, Carga un archivo de preguntas de ejemplo y las guarda en la base de datos., Modelo de opción de respuesta para una pregunta de referencia., ReferenceOption, import_reference_questions(), load_reference_file() (+5 more)

### Community 18 - "qgen/pipeline.py"
Cohesion: 0.13
Nodes (18): concurrent_futures, actual_cost_usd(), CostEstimate, doc_token_estimate(), estimate_run(), Cost accounting: predictions before a run + actual after. Pricing (USD per 1M…, `draft_calls` son las llamadas del creador (una por nodo): leen el mismo…, Compute actual cost from observed usage_metadata totals. `cache_create_tokens`… (+10 more)

### Community 19 - "get_profile"
Cohesion: 0.15
Nodes (20): auto_detect_profile(), get_profile(), Heuristic profile pick based on the first few elements' text. Looks for genre-…, Verifica que el perfil 'algebra_baldor' solo clasifica capítulos a nivel 0 y no…, En Álgebra de Baldor los únicos nodos son los 16 capítulos ('I. Suma' … 'XXXII.…, test_perfil_algebra_baldor_clasificacion(), test_perfil_algebra_baldor_solo_tiene_capitulos(), _el() (+12 more)

### Community 20 - "debug_pymupdf.py"
Cohesion: 0.15
Nodes (10): collections, One-off debug script: inspect characters used as TOC leaders., main(), Path, Quick visual inspection of an in-memory hierarchy without persisting., fitz, pymupdf, rapidocr (+2 more)

### Community 21 - "json"
Cohesion: 0.07
Nodes (17): Engine, main(), command, Path, init_db(), Create all tables. Idempotent — safe to run on existing DBs., _default_db_url(), get_engine() (+9 more)

### Community 22 - "main"
Cohesion: 0.22
Nodes (10): date, bundle_filename(), next_version(), Siguiente `v{n}` libre para este manual en `out_dir`. Se cuenta por manual y no…, slug(), main(), _print_summary(), command (+2 more)

### Community 23 - "Chunk"
Cohesion: 0.12
Nodes (27): DeclarativeBase, estimate_doc(), main(), node(), command, Print the hierarchy of a manual as a tree., Show a node's breadcrumb plus its chunks (truncated)., tree() (+19 more)

### Community 25 - "temario.py"
Cohesion: 0.16
Nodes (13): dataclasses, Extractor de ejercicios resueltos y problemas prácticos de Álgebra de Baldor., match_parte_temario(), Parte numerada de un temario ('1.1 Los elementos del proceso comunicativo').…, CapitulosConTemas, _norm(), _numero_de_tema(), Selección por temario: qué bloques, partes, capítulos o temas de un libro… (+5 more)

### Community 26 - "get_default_rules"
Cohesion: 0.22
Nodes (15): _resolve_rules(), merge_rules(), Sparse overrides to layer over a profile default. Stored at…, RulesOverride, get_default_rules(), test_calculo_una_variable_tiene_reglas_de_generacion(), test_geografia_moderna_mexico_tiene_reglas_de_generacion(), test_get_default_rules_known() (+7 more)

### Community 27 - "etl/pipeline.py"
Cohesion: 0.15
Nodes (15): Prueba unitaria del reordenamiento de fracciones romanas., Inspect a cached docling extraction to find LIBRO/TITULO lines and Latin-suffix…, ConsolidatedChunk, BaseModel, Consolida los elementos del cuerpo de cada nodo hoja en fragmentos con límite…, persist_manual(), Path, Session (+7 more)

### Community 28 - "ElementKind"
Cohesion: 0.16
Nodes (20): docling_core_types_doc, DoclingDocument, ElementKind, StrEnum, Manual profile builds PARTE → Capítulo → Sección hierarchy from body., Legal-code profile builds Libro → Título → Capítulo → Artículo., Drop filters silence Cámara/DOF noise without losing real content., Reform annotations get attached as metadata on the relevant node. (+12 more)

### Community 29 - "test_baldor_patterns.py"
Cohesion: 0.17
Nodes (11): Pruebas unitarias para los patrones y jerarquía de Álgebra de Baldor., Verifica subcasos con letras tipo a) o b)., Verifica que los capítulos con numeración romana se reconocen con su ordinal y…, Verifica las subsecciones con números romanos en mayúsculas., Verifica el reconocimiento de los casos clásicos de factorización., Verifica encabezados conceptuales y reglas generales en mayúsculas sostenidas., test_match_baldor_capitulo_romanos(), test_match_baldor_casos() (+3 more)

### Community 30 - "GenerationRun"
Cohesion: 0.07
Nodes (52): functools, logging, _check_once(), main(), _print_run_card(), _print_running(), command, CLI for monitoring + finalizing batch runs. Usage patterns -------------- 1)… (+44 more)

### Community 31 - "_bundle"
Cohesion: 0.20
Nodes (10): _bundle(), _options(), `cost_input_tokens` contiene 'token': el detector no debe morder ahí., Un bundle mínimo pero completo y válido., test_bundle_valido_pasa_sin_errores(), test_corrida_con_nodos_fallidos_avisa(), mutate(), test_los_contadores_de_tokens_no_son_un_secreto() (+2 more)

### Community 32 - "build_variable_prompt"
Cohesion: 0.30
Nodes (10): build_variable_prompt(), _node_text(), Render the per-node variable prompt that goes alongside the cached context., Build the user message for a single node. The cached context already gave…, Concatenate the node's chunks in order; empty string if none., _chunk(), _node(), test_variable_prompt_concatenates_multiple_chunks_in_order() (+2 more)

### Community 33 - "DocumentRules"
Cohesion: 0.33
Nodes (7): DocumentRules, Any, Per-archetype question-generation rules + per-document override mechanism. The…, Knobs that shape question generation for a class of documents., rules_from_dict(), rules_to_dict(), Profile-default rules. Edit here to change defaults globally. Per-document…

### Community 34 - "test_temario.py"
Cohesion: 0.48
Nodes (6): Perfil `taller_lectura_redaccion`: solo el temario pedido, como Bloque › Parte.…, test_cada_parte_cuelga_de_su_bloque(), test_cada_parte_lleva_solo_su_texto(), test_lo_que_no_esta_en_la_imagen_no_queda_en_ningun_nodo(), test_solo_quedan_los_bloques_y_partes_de_la_imagen(), _tree()

### Community 35 - "report.py"
Cohesion: 0.29
Nodes (8): build_report(), BaseModel, Session, QualityReport, Quality report for an ingested manual. Computes: - TOC coverage: % of TOC…, get_quality_report_dict(), Any, Returns the QualityReport as a plain dict (cache-friendly).

### Community 36 - "`explorer/` — revisor visual del pipeline"
Cohesion: 0.29
Nodes (6): Cómo correr, El árbol y la cobertura, `explorer/` — revisor visual del pipeline, La revisión, Navegación, Vistas

### Community 37 - "run_ref"
Cohesion: 0.33
Nodes (7): iso(), datetime, Clave estable de una corrida: `{model}--{mode}--{inicio compacto UTC}`., Fecha en el formato del contrato: ISO 8601 UTC con `Z`. SQLite devuelve los…, run_ref(), test_fecha_ingenua_se_lee_como_utc(), test_ref_de_corrida_es_estable()

### Community 38 - "match_titulo"
Cohesion: 0.33
Nodes (6): match_titulo(), test_match_titulo(), test_titulo_compound_decimoprimero(), test_titulo_compound_decimotercero(), test_titulo_preliminar(), test_titulo_with_trailing_title()

### Community 39 - "test_historia_universal.py"
Cohesion: 0.53
Nodes (5): Perfil `historia_universal`: el temario de la imagen, como Capítulo › Tema.…, test_cada_tema_cuelga_del_capitulo(), test_el_arbol_es_el_capitulo_y_sus_cuatro_temas(), test_los_subtitulos_quedan_en_el_cuerpo_de_su_tema(), _tree()

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
Cohesion: 0.08
Nodes (21): GeminiClient, Thin wrapper around google-genai with explicit context caching. We keep this…, ClassifiedHeading, GeminiHeadingClassifier, HeadingClassificationBatch, BaseModel, Gemini-based fallback classifier for ambiguous headings. Used only when the…, init_fts() (+13 more)

### Community 47 - "session.py"
Cohesion: 0.09
Nodes (32): contextlib, csv, Compute approximate Gemini cost for question generation across ingested…, datetime, SQLAlchemy 2.0 schema for the manuals corpus. Designed to run on SQLite (MVP)…, _utcnow(), Arma el bundle a partir del SQLite del pipeline. Separado del CLI para poder…, SHA-256 del PDF de origen, si sigue estando donde dice el manual. (+24 more)

### Community 48 - "hierarchy_tree.py"
Cohesion: 0.36
Nodes (7): collections_abc, _icon_for(), _indent(), Hierarchy tree rendered as nested expanders with optional click-to-navigate., Render the manual's tree. `on_select` is a function that takes a NodeSummary…, _render_node(), render_tree()

### Community 56 - "test_geografia_moderna_mexico.py"
Cohesion: 0.48
Nodes (6): Perfil `geografia_moderna_mexico`: el temario de la imagen, como Capítulo ›…, test_cada_tema_cuelga_de_su_capitulo(), test_el_arbol_es_el_de_la_imagen(), test_lo_que_no_esta_en_la_imagen_queda_fuera(), test_los_subtitulos_y_los_capitulos_completos_quedan_como_texto(), _tree()

### Community 57 - "OptionExemplarInput"
Cohesion: 0.40
Nodes (5): OptionExemplarInput, BaseModel, QuestionExemplarInput, Modelo Pydantic para validar una opción de respuesta de ejemplo., Modelo Pydantic para validar una pregunta de ejemplo completa.

## Knowledge Gaps
- **36 isolated node(s):** `Workflow: graphify`, `graphify`, `graphify en Windows`, `1. Por qué existe`, `2. Forma del fichero` (+31 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 378 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `session_scope()` connect `session_scope` to `1_📄_Manual.py`, `report.py`, `Contrato: bundle de contenido v1`, `6_❓_Preguntas.py`, `init_question_tables`, `data_access.py`, `pydantic`, `session.py`, `run_pipeline`, `import_reference_questions`, `json`, `main`, `Chunk`, `etl/pipeline.py`, `GenerationRun`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Why does `RawElement` connect `RawElement` to `test_temario.py`, `profile.py`, `test_historia_universal.py`, `ChunkConsolidator`, `types.py`, `test_calculo_una_variable.py`, `get_profile`, `test_geografia_moderna_mexico.py`, `temario.py`, `etl/pipeline.py`, `ElementKind`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `RawElement` (e.g. with `ChunkConsolidator` and `UnstructuredAdapter`) actually correct?**
  _`RawElement` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `init_question_tables()` (e.g. with `seed_questions()` and `Base`) actually correct?**
  _`init_question_tables()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `Chunk` (e.g. with `main()` and `node()`) actually correct?**
  _`Chunk` has 25 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Workflow: graphify`, `graphify`, `graphify en Windows` to the rest of the system?**
  _36 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `1_📄_Manual.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12100840336134454 - nodes in this community are weakly interconnected._