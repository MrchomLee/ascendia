# Graph Report - onmy-military-library-contenido  (2026-09-07)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 735 nodes · 1860 edges · 44 communities (20 shown, 4 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 226 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fd3c1ad9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- data_access.py
- test_bundle_spec.py
- GeneratedQuestion
- qgen/pipeline.py
- session_scope
- profile.py
- Chunk
- RawElement
- ExtractionResult
- ChunkConsolidator
- toc_parser.py
- session.py
- GeminiClient
- etl/pipeline.py
- get_profile
- ElementKind
- main
- _isolate_data_dir
- _isolate_data_dir
- etl
- debug_libros.py
- debug_pymupdf.py
- smoke_imports.py
- validation/__init__.py

## God Nodes (most connected - your core abstractions)
1. `session_scope()` - 44 edges
2. `build_bundle()` - 29 edges
3. `Chunk` - 28 edges
4. `RawElement` - 28 edges
5. `run_pipeline()` - 27 edges
6. `init_question_tables()` - 26 edges
7. `Manual` - 25 edges
8. `Node` - 25 edges
9. `GenerationRun` - 24 edges
10. `_errors()` - 24 edges

## Surprising Connections (you probably didn't know these)
- `GenerationRun` --uses--> `Manual`  [INFERRED]
  question_generator/src/qgen/models/schema.py → etl/src/etl/models/schema.py
- `set_validation_status()` --uses--> `Question`  [INFERRED]
  explorer/src/explorer/questions_access.py → question_generator/src/qgen/models/schema.py
- `status_by_node()` --uses--> `Question`  [INFERRED]
  explorer/src/explorer/questions_access.py → question_generator/src/qgen/models/schema.py
- `Question` --uses--> `Node`  [INFERRED]
  question_generator/src/qgen/models/schema.py → etl/src/etl/models/schema.py
- `init_question_tables()` --uses--> `Base`  [INFERRED]
  question_generator/src/qgen/db/migration.py → etl/src/etl/models/schema.py

## Import Cycles
- None detected.

## Communities (44 total, 4 thin omitted)

### Community 0 - "data_access.py"
Cohesion: 0.05
Nodes (73): _icon_for(), _indent(), Hierarchy tree rendered as nested expanders with optional click-to-navigate., Render the manual's tree. `on_select` is a function that takes a NodeSummary…, _render_node(), render_tree(), kpi_row(), Render a row of `st.metric` cards. items is a list of (label, value,… (+65 more)

### Community 1 - "test_bundle_spec.py"
Cohesion: 0.05
Nodes (82): date, SHA-256 del PDF de origen, si sigue estando donde dice el manual., source_digest(), Bundle de contenido: la interfaz entre la generación de preguntas y la webapp., _bool(), bundle_filename(), _dict(), dumps() (+74 more)

### Community 2 - "GeneratedQuestion"
Cohesion: 0.06
Nodes (65): model_validator, _check_once(), main(), _print_run_card(), _print_running(), command, CLI for monitoring + finalizing batch runs. Usage patterns -------------- 1)…, _state_name() (+57 more)

### Community 3 - "qgen/pipeline.py"
Cohesion: 0.07
Nodes (54): main(), _print_estimate(), _print_summary(), _progress_cb(), command, actual_cost_usd(), CostEstimate, doc_token_estimate() (+46 more)

### Community 4 - "session_scope"
Cohesion: 0.08
Nodes (60): session_scope(), get_question_kpis(), list_questions(), list_runs(), cache_data, Preguntas de un manual, con su nodo y sus opciones ya resueltos., build_bundle(), DuplicateNodeRef (+52 more)

### Community 5 - "profile.py"
Cohesion: 0.08
Nodes (45): classify_heading(), HeadingCandidate, match_anexo(), match_articulo(), match_capitulo(), match_ejercicio(), match_libro(), match_miscelanea() (+37 more)

### Community 6 - "Chunk"
Cohesion: 0.12
Nodes (28): DeclarativeBase, estimate_doc(), main(), Compute approximate Gemini cost for question generation across ingested…, manuals(), node(), command, List every ingested manual. (+20 more)

### Community 7 - "RawElement"
Cohesion: 0.14
Nodes (16): One layout element extracted from a PDF page. Both Docling and Unstructured…, RawElement, _Builder, HierarchyAssembler, _label_for_depth(), _peek_next_title(), Build a manual's hierarchy tree from extracted elements + optional TOC.…, Assembles a tree from raw elements, optionally guided by a TOC. Parameters… (+8 more)

### Community 8 - "ExtractionResult"
Cohesion: 0.14
Nodes (16): ABC, ExtractorBase, Path, Common interface for layout extractors. Adapters (Docling, Unstructured, etc.)…, Run the extractor on a PDF and return normalized elements., DoclingAdapter, _first_bbox(), _first_page() (+8 more)

### Community 9 - "ChunkConsolidator"
Cohesion: 0.15
Nodes (15): Prueba unitaria del reordenamiento de fracciones romanas., ChunkConsolidator, ConsolidatedChunk, BaseModel, Consolida los elementos del cuerpo de cada nodo hoja en fragmentos con límite…, Convierte un número romano a entero, o None si no es válido., Reordena fracciones romanas que docling extrajo en orden incorrecto. Docling a…, HierarchyNode (+7 more)

### Community 10 - "toc_parser.py"
Cohesion: 0.12
Nodes (24): detect_toc_pages(), _infer_depth(), _is_roman_only(), _lookback_marker(), _parse_page_number(), parse_toc(), _peek_parte_title(), BaseModel (+16 more)

### Community 11 - "session.py"
Cohesion: 0.13
Nodes (19): Engine, main(), command, Path, init_db(), Create all tables. Idempotent — safe to run on existing DBs., _default_db_url(), get_engine() (+11 more)

### Community 12 - "GeminiClient"
Cohesion: 0.15
Nodes (9): GeminiClient, Thin wrapper around google-genai with explicit context caching. We keep this…, ClassifiedHeading, GeminiHeadingClassifier, HeadingClassificationBatch, BaseModel, GeminiClient, Gemini-based fallback classifier for ambiguous headings. Used only when the… (+1 more)

### Community 13 - "etl/pipeline.py"
Cohesion: 0.21
Nodes (15): main(), Path, Quick visual inspection of an in-memory hierarchy without persisting., cache_extraction(), get_extractor(), _guess_code(), _guess_title(), load_cached_extraction() (+7 more)

### Community 14 - "get_profile"
Cohesion: 0.20
Nodes (15): auto_detect_profile(), get_profile(), Heuristic profile pick based on the first few elements' text. Looks for genre-…, _el(), test_autodetect_codigo_legal(), test_autodetect_falls_back_to_manual_for_empty(), test_autodetect_manual(), test_codigo_legal_drop_filters() (+7 more)

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

## Knowledge Gaps
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `session_scope()` connect `session_scope` to `data_access.py`, `test_bundle_spec.py`, `GeneratedQuestion`, `qgen/pipeline.py`, `Chunk`, `ChunkConsolidator`, `session.py`, `etl/pipeline.py`?**
  _High betweenness centrality (0.150) - this node is a cross-community bridge._
- **Why does `get_profile()` connect `get_profile` to `GeneratedQuestion`, `profile.py`, `RawElement`, `etl/pipeline.py`, `ElementKind`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `run_pipeline()` connect `etl/pipeline.py` to `session_scope`, `Chunk`, `RawElement`, `ExtractionResult`, `ChunkConsolidator`, `toc_parser.py`, `session.py`, `get_profile`, `main`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `build_bundle()` (e.g. with `Chunk` and `Manual`) actually correct?**
  _`build_bundle()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `Chunk` (e.g. with `main()` and `node()`) actually correct?**
  _`Chunk` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `RawElement` (e.g. with `ChunkConsolidator` and `DoclingAdapter`) actually correct?**
  _`RawElement` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `run_pipeline()` (e.g. with `ConsolidatedChunk` and `TocResult`) actually correct?**
  _`run_pipeline()` has 5 INFERRED edges - model-reasoned connections that need verification._