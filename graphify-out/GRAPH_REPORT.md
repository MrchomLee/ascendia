# Graph Report - onmy-military-library-contenido  (2026-09-07)

## Corpus Check
- 127 files · ~39,038 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 812 nodes · 1984 edges · 54 communities (29 shown, 7 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 235 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fd3c1ad9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- 1_📄_Manual.py
- test_bundle_spec.py
- GeneratedQuestion
- qgen/pipeline.py
- session_scope
- profile.py
- Contrato: bundle de contenido v1
- RawElement
- ExtractionResult
- ChunkConsolidator
- toc_parser.py
- 5_🔍_Search.py
- GeminiClient
- etl/pipeline.py
- 6_❓_Preguntas.py
- ElementKind
- main
- _isolate_data_dir
- _isolate_data_dir
- etl
- debug_libros.py
- debug_pymupdf.py
- smoke_imports.py
- validation/__init__.py
- data_access.py
- build_bundle
- bundle/__init__.py
- spec.py
- assembler.py
- export.py
- get_tree
- `explorer/` — revisor visual del pipeline
- _isolate_data_dir
- rules/graphify.md
- workflows/graphify.md
- _compose_title

## God Nodes (most connected - your core abstractions)
1. `session_scope()` - 46 edges
2. `Chunk` - 30 edges
3. `build_bundle()` - 29 edges
4. `RawElement` - 28 edges
5. `init_question_tables()` - 28 edges
6. `Manual` - 27 edges
7. `Node` - 27 edges
8. `run_pipeline()` - 27 edges
9. `GenerationRun` - 24 edges
10. `_errors()` - 24 edges

## Surprising Connections (you probably didn't know these)
- `_parse()` --uses--> `TocResult`  [INFERRED]
  explorer/src/explorer/pages/3_📑_TOC.py → etl/src/etl/extraction/toc_parser.py
- `deserialize_extraction()` --uses--> `ExtractionResult`  [INFERRED]
  explorer/src/explorer/data_access.py → etl/src/etl/extraction/types.py
- `get_manual()` --uses--> `Manual`  [INFERRED]
  explorer/src/explorer/data_access.py → etl/src/etl/models/schema.py
- `list_manuals()` --uses--> `Manual`  [INFERRED]
  explorer/src/explorer/data_access.py → etl/src/etl/models/schema.py
- `build_bundle()` --uses--> `Manual`  [INFERRED]
  question_generator/src/qgen/bundle/build.py → etl/src/etl/models/schema.py

## Import Cycles
- None detected.

## Communities (54 total, 7 thin omitted)

### Community 0 - "1_📄_Manual.py"
Cohesion: 0.12
Nodes (23): kpi_row(), Render a row of `st.metric` cards. items is a list of (label, value,…, cache_data, Render a single PDF page to PNG bytes via PyMuPDF., Return PNG bytes of the given page (1-based), or None if unavailable. Cached so…, Convenience: render and display in one call., render_page(), render_page_widget() (+15 more)

### Community 1 - "test_bundle_spec.py"
Cohesion: 0.11
Nodes (32): _bundle(), _errors(), _options(), El contrato del bundle: lo que se acepta y, sobre todo, lo que no. Cada caso de…, `cost_input_tokens` contiene 'token': el detector no debe morder ahí., Un bundle mínimo pero completo y válido., test_api_key_en_metadata_bloquea_la_entrega(), test_arbol_sin_raiz() (+24 more)

### Community 2 - "GeneratedQuestion"
Cohesion: 0.06
Nodes (65): model_validator, _check_once(), main(), _print_run_card(), _print_running(), command, CLI for monitoring + finalizing batch runs. Usage patterns -------------- 1)…, _state_name() (+57 more)

### Community 3 - "qgen/pipeline.py"
Cohesion: 0.07
Nodes (54): main(), _print_estimate(), _print_summary(), _progress_cb(), command, actual_cost_usd(), CostEstimate, doc_token_estimate() (+46 more)

### Community 4 - "session_scope"
Cohesion: 0.05
Nodes (91): DeclarativeBase, Engine, estimate_doc(), main(), Compute approximate Gemini cost for question generation across ingested…, main(), command, Path (+83 more)

### Community 5 - "profile.py"
Cohesion: 0.06
Nodes (63): classify_heading(), HeadingCandidate, HeadingMatch, match_anexo(), match_articulo(), match_capitulo(), match_ejercicio(), match_libro() (+55 more)

### Community 6 - "Contrato: bundle de contenido v1"
Cohesion: 0.05
Nodes (40): 1. Por qué existe, 2. Forma del fichero, 3. Estructura, 4. Identidad: las claves estables, 5. Las validaciones, 6. Los dos comandos, 7. Versionado del contrato, Aquí — `qgen-export` (+32 more)

### Community 7 - "RawElement"
Cohesion: 0.30
Nodes (8): TocResult, One layout element extracted from a PDF page. Both Docling and Unstructured…, RawElement, _Builder, HierarchyAssembler, _peek_next_title(), Assembles a tree from raw elements, optionally guided by a TOC. Parameters…, Look ahead up to 3 elements for something that acts as the heading title.

### Community 8 - "ExtractionResult"
Cohesion: 0.14
Nodes (16): ABC, ExtractorBase, Path, Common interface for layout extractors. Adapters (Docling, Unstructured, etc.)…, Run the extractor on a PDF and return normalized elements., DoclingAdapter, _first_bbox(), _first_page() (+8 more)

### Community 9 - "ChunkConsolidator"
Cohesion: 0.12
Nodes (20): Prueba unitaria del reordenamiento de fracciones romanas., ChunkConsolidator, ConsolidatedChunk, BaseModel, Consolida los elementos del cuerpo de cada nodo hoja en fragmentos con límite…, Convierte un número romano a entero, o None si no es válido., Reordena fracciones romanas que docling extrajo en orden incorrecto. Docling a…, persist_manual() (+12 more)

### Community 10 - "toc_parser.py"
Cohesion: 0.12
Nodes (23): detect_toc_pages(), _infer_depth(), _is_roman_only(), _lookback_marker(), _parse_page_number(), parse_toc(), _peek_parte_title(), BaseModel (+15 more)

### Community 11 - "5_🔍_Search.py"
Cohesion: 0.25
Nodes (9): Full-text search across chunks via SQLite FTS5., init_fts(), BaseModel, query(), Full-text search over chunks using SQLite FTS5. We create a virtual table…, FTS5 has reserved chars; we wrap free-form input as a phrase if needed., Create FTS5 virtual table + triggers if missing, then backfill any chunks that…, _sanitize() (+1 more)

### Community 12 - "GeminiClient"
Cohesion: 0.15
Nodes (9): GeminiClient, Thin wrapper around google-genai with explicit context caching. We keep this…, ClassifiedHeading, GeminiHeadingClassifier, HeadingClassificationBatch, BaseModel, GeminiClient, Gemini-based fallback classifier for ambiguous headings. Used only when the… (+1 more)

### Community 13 - "etl/pipeline.py"
Cohesion: 0.21
Nodes (15): main(), Path, Quick visual inspection of an in-memory hierarchy without persisting., cache_extraction(), get_extractor(), _guess_code(), _guess_title(), load_cached_extraction() (+7 more)

### Community 14 - "6_❓_Preguntas.py"
Cohesion: 0.13
Nodes (23): Preguntas generadas — revisión visual, cobertura y corridas. Es la vista de la…, _render_question(), get_question_kpis(), list_questions(), list_runs(), nodes_missing_questions(), OptionView, BaseModel (+15 more)

### Community 15 - "ElementKind"
Cohesion: 0.29
Nodes (11): ElementKind, StrEnum, Manual profile builds PARTE → Capítulo → Sección hierarchy from body., Legal-code profile builds Libro → Título → Capítulo → Artículo., Drop filters silence Cámara/DOF noise without losing real content., Reform annotations get attached as metadata on the relevant node., _t(), test_assemble_codigo_legal_basic() (+3 more)

### Community 16 - "main"
Cohesion: 0.43
Nodes (6): main(), _print_table(), command, Path, Run both extractors with persistence disabled and emit a comparison., _render_markdown()

### Community 17 - "_isolate_data_dir"
Cohesion: 0.50
Nodes (3): _isolate_data_dir(), fixture, Each test gets a clean data dir + in-memory-equivalent SQLite file.

### Community 18 - "_isolate_data_dir"
Cohesion: 0.50
Nodes (3): _isolate_data_dir(), fixture, Each test gets a fresh DB. Clear etl's lru_cache so a new engine binds to it.

### Community 19 - "etl"
Cohesion: 1.00
Nodes (3): etl, explorer, question_generator

### Community 39 - "data_access.py"
Cohesion: 0.17
Nodes (20): _chunk_to_summary(), ChunkSummary, deserialize_extraction(), get_chunks_for_manual(), get_chunks_for_node(), get_extraction_cache(), get_manual(), get_node() (+12 more)

### Community 43 - "build_bundle"
Cohesion: 0.14
Nodes (20): build_bundle(), DuplicateNodeRef, DuplicateRunRef, _materia_hint(), _pipeline_commit(), Any, Session, _qgen_version() (+12 more)

### Community 44 - "bundle/__init__.py"
Cohesion: 0.18
Nodes (17): Bundle de contenido: la interfaz entre la generación de preguntas y la webapp., dumps(), Path, Serialización canónica: UTF-8, indentado a 2, sin escapar acentos., Escribe el bundle (comprimiendo si es grande) y su `.sha256`. Devuelve `(ruta…, Comprueba el `.sha256` que acompaña al bundle. Lanza si no cuadra., Lee un bundle `.json` o `.json.gz`. No valida: para eso está `validate`., read_bundle() (+9 more)

### Community 45 - "spec.py"
Cohesion: 0.26
Nodes (14): _bool(), _dict(), find_secrets(), _int(), _is_iso(), Any, Formato del bundle de contenido v1. La especificación en prosa vive en los dos…, Resultado de validar un bundle. `errors` bloquea (no se exporta, no se… (+6 more)

### Community 46 - "assembler.py"
Cohesion: 0.13
Nodes (6): _label_for_depth(), Build a manual's hierarchy tree from extracted elements + optional TOC.…, _strip_known_prefix(), DocumentProfile, Run metadata extractors over `text` and return any captures., Configuration of one document archetype. Parameters ---------- name Stable…

### Community 47 - "export.py"
Cohesion: 0.22
Nodes (12): date, SHA-256 del PDF de origen, si sigue estando donde dice el manual., source_digest(), bundle_filename(), next_version(), Siguiente `v{n}` libre para este manual en `out_dir`. Se cuenta por manual y no…, slug(), main() (+4 more)

### Community 48 - "get_tree"
Cohesion: 0.27
Nodes (12): _icon_for(), _indent(), Hierarchy tree rendered as nested expanders with optional click-to-navigate., Render the manual's tree. `on_select` is a function that takes a NodeSummary…, _render_node(), render_tree(), get_node_ancestors(), get_node_children() (+4 more)

### Community 49 - "`explorer/` — revisor visual del pipeline"
Cohesion: 0.29
Nodes (6): Cómo correr, El árbol y la cobertura, `explorer/` — revisor visual del pipeline, La revisión, Navegación, Vistas

### Community 50 - "_isolate_data_dir"
Cohesion: 0.50
Nodes (3): _isolate_data_dir(), fixture, Cada prueba obtiene una base de datos limpia y aislada. Limpia el lru_cache de…

## Knowledge Gaps
- **37 isolated node(s):** `graphify`, `Workflow: graphify`, `1. Por qué existe`, `2. Forma del fichero`, `Notas por bloque` (+32 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 282 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `session_scope()` connect `session_scope` to `1_📄_Manual.py`, `GeneratedQuestion`, `qgen/pipeline.py`, `data_access.py`, `ChunkConsolidator`, `5_🔍_Search.py`, `etl/pipeline.py`, `6_❓_Preguntas.py`, `export.py`, `get_tree`?**
  _High betweenness centrality (0.127) - this node is a cross-community bridge._
- **Why does `get_profile()` connect `profile.py` to `GeneratedQuestion`, `etl/pipeline.py`, `assembler.py`, `ElementKind`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Why does `run_pipeline()` connect `etl/pipeline.py` to `session_scope`, `profile.py`, `RawElement`, `ExtractionResult`, `ChunkConsolidator`, `toc_parser.py`, `assembler.py`, `main`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `Chunk` (e.g. with `main()` and `node()`) actually correct?**
  _`Chunk` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `build_bundle()` (e.g. with `Chunk` and `Manual`) actually correct?**
  _`build_bundle()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `RawElement` (e.g. with `ChunkConsolidator` and `DoclingAdapter`) actually correct?**
  _`RawElement` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `graphify`, `Workflow: graphify`, `1. Por qué existe` to the rest of the system?**
  _37 weakly-connected nodes found - possible documentation gaps or missing edges._