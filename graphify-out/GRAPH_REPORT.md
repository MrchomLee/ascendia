# Graph Report - onmy-military-library-contenido  (2026-09-23)

## Corpus Check
- 155 files · ~73,427 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 6, .example 1, .lock 1)

## Summary
- 1311 nodes · 3481 edges · 72 communities (63 shown, 9 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 426 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8692b843`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- 6_❓_Preguntas.py
- test_bundle_spec.py
- test_pipeline.py
- DocumentRules
- Contrato: bundle de contenido v2
- profile.py
- questions_access.py
- session_scope
- render_page
- types.py
- toc_parser.py
- data_access.py
- RawElement
- test_patterns.py
- bundle/__init__.py
- BaldorExerciseExtractor
- etl/pipeline.py
- get_default_rules
- json
- get_profile
- seed_questions_manual_11.py
- session.py
- build_windows
- etl/models/schema.py
- smoke_imports.py
- dataclasses
- _seed
- consolidator.py
- ElementKind
- test_baldor_patterns.py
- batch_status.py
- _bundle
- test_algebra_trigonometria_geometria_analitica.py
- qgen/pipeline.py
- schemas.py
- test_checks.py
- `explorer/` — revisor visual del pipeline
- run_ref
- families.py
- _run_immediate
- test_calculo_una_variable.py
- _normalize
- etl
- workflows/graphify.md
- CLAUDE.md
- spec.py
- GeminiClient
- Question
- hierarchy_tree.py
- validation/__init__.py
- run_generation
- DuplicateIndex
- importer.py
- persist_question
- Generación de preguntas por ventanas (qgen v2)
- WindowQuestion
- checks.py
- test_plan_windows.py
- 5_🔍_Search.py
- os
- test_geografia_moderna_mexico.py
- test_temario.py
- test_historia_universal.py
- test_cost.py
- OptionExemplarInput
- match_libro
- to_generated

## God Nodes (most connected - your core abstractions)
1. `session_scope()` - 67 edges
2. `init_question_tables()` - 43 edges
3. `RawElement` - 40 edges
4. `build_bundle()` - 32 edges
5. `Manual` - 31 edges
6. `Chunk` - 31 edges
7. `_run_immediate()` - 31 edges
8. `FakeGemini` - 31 edges
9. `get_default_rules()` - 30 edges
10. `_errors()` - 30 edges

## Surprising Connections (you probably didn't know these)
- `4. Identidad: las claves estables` --references--> `manuals()`  [INFERRED]
  CONTRATO-BUNDLE.md → etl/src/etl/cli/inspect_cli.py
- `Notas por bloque` --references--> `manuals()`  [INFERRED]
  CONTRATO-BUNDLE.md → etl/src/etl/cli/inspect_cli.py
- `Task 3: Esquemas de salida de la llamada por ventana` --references--> `QuestionType`  [INFERRED]
  docs/superpowers/plans/2026-09-23-qgen-ventanas.md → question_generator/src/qgen/prompts/schemas.py
- `6. La llamada por ventana` --references--> `WindowResponse`  [INFERRED]
  docs/superpowers/specs/2026-09-23-qgen-ventanas-design.md → question_generator/src/qgen/prompts/schemas.py
- `Task 2: Ventanas` --references--> `Chunk`  [INFERRED]
  docs/superpowers/plans/2026-09-23-qgen-ventanas.md → etl/src/etl/models/schema.py

## Import Cycles
- None detected.

## Communities (72 total, 9 thin omitted)

### Community 0 - "6_❓_Preguntas.py"
Cohesion: 0.16
Nodes (20): dotenv, kpi_row(), Render a row of `st.metric` cards. items is a list of (label, value,…, Render a single PDF page to PNG bytes via PyMuPDF., list_manuals(), Home page — list of ingested manuals + global KPIs., get_int(), link_to() (+12 more)

### Community 1 - "test_bundle_spec.py"
Cohesion: 0.11
Nodes (35): copy, _errors(), _options(), El contrato del bundle: lo que se acepta y, sobre todo, lo que no. Cada caso de…, test_api_key_en_metadata_bloquea_la_entrega(), test_arbol_sin_raiz(), test_cadena_de_conexion_en_metadata_bloquea_la_entrega(), test_ciclo_en_el_arbol() (+27 more)

### Community 2 - "test_pipeline.py"
Cohesion: 0.17
Nodes (41): Las preguntas crudas de una ventana (sin validar) y lo que costó pedirlas., VerificationOutcome, WindowOutcome, _ejercicio_nuevo(), _estimate(), FakeGemini, _item(), _letra() (+33 more)

### Community 3 - "DocumentRules"
Cohesion: 0.17
Nodes (19): Task 1: Familia y tipos en las reglas, 5. Familias y tipos, _resolve_rules(), DocumentRules, merge_rules(), Any, Per-archetype question-generation rules + per-document override mechanism. The…, Knobs that shape question generation for a class of documents. (+11 more)

### Community 4 - "Contrato: bundle de contenido v2"
Cohesion: 0.05
Nodes (41): 1. Por qué existe, 2. Forma del fichero, 3. Estructura, 4. Identidad: las claves estables, 5. Las validaciones, 6. Los dos comandos, 7. Versionado del contrato, Aquí — `qgen-export` (+33 more)

### Community 5 - "profile.py"
Cohesion: 0.14
Nodes (28): HeadingCandidate, match_anexo(), match_baldor_capitulo(), match_baldor_caso(), match_baldor_inciso(), match_baldor_subseccion_romana(), match_baldor_tema_mayusculas(), match_bloque() (+20 more)

### Community 6 - "questions_access.py"
Cohesion: 0.10
Nodes (30): datetime, Task 11: Explorador: tipo, cita y motivos, _render_question(), get_question_kpis(), list_questions(), list_runs(), OptionView, BaseModel (+22 more)

### Community 7 - "session_scope"
Cohesion: 0.25
Nodes (23): session_scope(), build_bundle(), Any, Session, Construye el bundle v2 de un manual. `run_ids` limita a esas corridas (y a sus…, main(), command, init_question_tables() (+15 more)

### Community 8 - "render_page"
Cohesion: 0.40
Nodes (5): cache_data, Return PNG bytes of the given page (1-based), or None if unavailable. Cached so…, Convenience: render and display in one call., render_page(), render_page_widget()

### Community 9 - "types.py"
Cohesion: 0.12
Nodes (19): ABC, enum, ExtractorBase, Path, Common interface for layout extractors. Adapters (Docling, Unstructured, etc.)…, Run the extractor on a PDF and return normalized elements., DoclingAdapter, elements_from_document() (+11 more)

### Community 10 - "toc_parser.py"
Cohesion: 0.07
Nodes (33): detect_toc_pages(), _infer_depth(), _is_roman_only(), _lookback_marker(), _parse_page_number(), parse_toc(), _peek_parte_title(), BaseModel (+25 more)

### Community 11 - "data_access.py"
Cohesion: 0.12
Nodes (31): graphify, _chunk_to_summary(), ChunkSummary, deserialize_extraction(), get_chunks_for_manual(), get_chunks_for_node(), get_extraction_cache(), get_global_kpis() (+23 more)

### Community 12 - "RawElement"
Cohesion: 0.12
Nodes (17): TocResult, One layout element extracted from a PDF page. Both Docling and Unstructured…, RawElement, _Builder, HierarchyAssembler, HierarchyNode, _label_for_depth(), _peek_next_title() (+9 more)

### Community 13 - "test_patterns.py"
Cohesion: 0.12
Nodes (27): classify_heading(), match_articulo(), match_titulo(), Compatibility shim: classify using the default 'manual' profile. New code…, Default classify_heading uses 'manual' profile — articles are not its concern…, test_anexo(), test_articulo_quater(), test_articulo_septimus() (+19 more)

### Community 14 - "bundle/__init__.py"
Cohesion: 0.17
Nodes (19): date, Bundle de contenido: la interfaz entre la generación de preguntas y la webapp., bundle_filename(), next_version(), Path, Siguiente `v{n}` libre para este manual en `out_dir`. Se cuenta por manual y no…, Escribe el bundle (comprimiendo si es grande) y su `.sha256`. Devuelve `(ruta…, Comprueba el `.sha256` que acompaña al bundle. Lanza si no cuadra. (+11 more)

### Community 15 - "BaldorExerciseExtractor"
Cohesion: 0.11
Nodes (18): BaldorExercise, BaldorExerciseExtractor, flush_current(), Extractor de ejercicios resueltos y problemas prácticos de Álgebra de Baldor., Genera el texto estructurado del ejercicio para el prompt de generación de…, Analizador para extraer problemas numerados, procedimientos y soluciones., Extrae la lista de ejercicios presentes en un bloque de texto., Parsea el bloque de texto de un ejercicio individual extrayendo enunciado,… (+10 more)

### Community 16 - "etl/pipeline.py"
Cohesion: 0.12
Nodes (24): main(), _print_table(), command, Path, Run both extractors with persistence disabled and emit a comparison., _render_markdown(), main(), command (+16 more)

### Community 17 - "get_default_rules"
Cohesion: 0.11
Nodes (29): build_window_instruction(), Instrucción del sistema para la llamada por ventana: plantilla de la familia +…, get_default_rules(), Profile-default rules. Edit here to change defaults globally. Per-document…, Pruebas unitarias para las reglas y prompts de generación de preguntas de…, La instrucción por ventana lleva las reglas de Baldor y pide ejercicios., Verifica que el perfil 'algebra_baldor' está registrado en el catálogo de…, test_algebra_baldor_prompt_rendering() (+21 more)

### Community 18 - "json"
Cohesion: 0.13
Nodes (4): Inspect a cached docling extraction to find LIBRO/TITULO lines and Latin-suffix…, json, pickle, sqlite3

### Community 19 - "get_profile"
Cohesion: 0.15
Nodes (20): auto_detect_profile(), get_profile(), Heuristic profile pick based on the first few elements' text. Looks for genre-…, Verifica que el perfil 'algebra_baldor' solo clasifica capítulos a nivel 0 y no…, En Álgebra de Baldor los únicos nodos son los 16 capítulos ('I. Suma' … 'XXXII.…, test_perfil_algebra_baldor_clasificacion(), test_perfil_algebra_baldor_solo_tiene_capitulos(), _el() (+12 more)

### Community 20 - "seed_questions_manual_11.py"
Cohesion: 0.13
Nodes (11): collections, Inserta preguntas generadas directamente en el chat para el manual 11 (Álgebra…, One-off debug script: inspect characters used as TOC leaders., main(), Path, Quick visual inspection of an in-memory hierarchy without persisting., fitz, pymupdf (+3 more)

### Community 21 - "session.py"
Cohesion: 0.15
Nodes (15): contextlib, Engine, init_db(), Create all tables. Idempotent — safe to run on existing DBs., _default_db_url(), get_engine(), get_session_factory(), Session (+7 more)

### Community 22 - "build_windows"
Cohesion: 0.20
Nodes (24): Protocol, build_windows(), ChunkLike, Ventanas de texto para generar preguntas (spec §4). Una ventana es un grupo de…, Quita del inicio de `text` lo que repite del final de `prev` (y el salto que lo…, Agrupa los chunks de un nodo en ventanas. Puro y determinista., strip_overlap(), _unir() (+16 more)

### Community 23 - "etl/models/schema.py"
Cohesion: 0.10
Nodes (33): DeclarativeBase, estimate_doc(), main(), Compute approximate Gemini cost for question generation across ingested…, manuals(), node(), command, List every ingested manual. (+25 more)

### Community 25 - "dataclasses"
Cohesion: 0.18
Nodes (12): dataclasses, match_parte_temario(), Parte numerada de un temario ('1.1 Los elementos del proceso comunicativo').…, CapitulosConTemas, _norm(), _numero_de_tema(), Selección por temario: qué bloques, partes, capítulos o temas de un libro…, (número, resto del encabezado) si el encabezado abre un capítulo. (+4 more)

### Community 26 - "_seed"
Cohesion: 0.38
Nodes (9): AppTest, _open_page(), Pestaña "Exportar Bundle" de la página de preguntas, ejecutada con AppTest. La…, _seed(), test_la_cita_se_muestra_tal_cual(), test_la_pregunta_muestra_su_tipo_y_sus_motivos(), test_un_bundle_con_errores_no_se_ofrece_y_se_explica_por_que(), test_un_bundle_que_cumple_el_contrato_se_puede_descargar() (+1 more)

### Community 27 - "consolidator.py"
Cohesion: 0.17
Nodes (12): Prueba unitaria del reordenamiento de fracciones romanas., ChunkConsolidator, ConsolidatedChunk, BaseModel, Consolida los elementos del cuerpo de cada nodo hoja en fragmentos con límite…, Convierte un número romano a entero, o None si no es válido., Reordena fracciones romanas que docling extrajo en orden incorrecto. Docling a…, HierarchyTree (+4 more)

### Community 28 - "ElementKind"
Cohesion: 0.16
Nodes (20): docling_core_types_doc, DoclingDocument, ElementKind, StrEnum, Manual profile builds PARTE → Capítulo → Sección hierarchy from body., Legal-code profile builds Libro → Título → Capítulo → Artículo., Drop filters silence Cámara/DOF noise without losing real content., Reform annotations get attached as metadata on the relevant node. (+12 more)

### Community 29 - "test_baldor_patterns.py"
Cohesion: 0.17
Nodes (11): Pruebas unitarias para los patrones y jerarquía de Álgebra de Baldor., Verifica subcasos con letras tipo a) o b)., Verifica que los capítulos con numeración romana se reconocen con su ordinal y…, Verifica las subsecciones con números romanos en mayúsculas., Verifica el reconocimiento de los casos clásicos de factorización., Verifica encabezados conceptuales y reglas generales en mayúsculas sostenidas., test_match_baldor_capitulo_romanos(), test_match_baldor_casos() (+3 more)

### Community 30 - "batch_status.py"
Cohesion: 0.06
Nodes (61): Exception, functools, logging, _check_once(), main(), _print_run_card(), _print_running(), command (+53 more)

### Community 31 - "_bundle"
Cohesion: 0.18
Nodes (11): dumps(), Serialización canónica: UTF-8, indentado a 2, sin escapar acentos., _bundle(), `cost_input_tokens` contiene 'token': el detector no debe morder ahí., Un bundle mínimo pero completo y válido., test_bundle_valido_pasa_sin_errores(), test_corrida_con_nodos_fallidos_avisa(), test_los_acentos_no_se_escapan() (+3 more)

### Community 32 - "test_algebra_trigonometria_geometria_analitica.py"
Cohesion: 0.53
Nodes (5): Perfil `algebra_trigonometria_geometria_analitica`: los cuatro capítulos de la…, test_el_arbol_son_los_cuatro_capitulos_de_la_imagen(), test_la_portada_queda_fuera(), test_secciones_ejemplos_y_teoremas_quedan_en_el_cuerpo_de_su_capitulo(), _tree()

### Community 33 - "qgen/pipeline.py"
Cohesion: 0.14
Nodes (22): concurrent_futures, _model_option(), doc_token_estimate(), estimate_windows(), Cost accounting: predictions before a run + actual after. Pricing (USD per 1M…, Una llamada por ventana (instrucción + texto de la ventana + documento…, WindowEstimate, Accept short aliases ('flash', 'pro') or full names; return canonical model id. (+14 more)

### Community 34 - "schemas.py"
Cohesion: 0.18
Nodes (23): Task 4: Revisiones de cada pregunta, Task 6: Llamadas a Gemini: ventana y verificación, 12. Organización del código, GeneratedOption, GeneratedQuestion, OptionRole, BaseModel, StrEnum (+15 more)

### Community 35 - "test_checks.py"
Cohesion: 0.17
Nodes (22): Revisión por tipo contra el texto de la ventana (spec §7, tabla de revisiones)., review(), Verdict, _item(), _q(), Revisiones de cada pregunta de una ventana (spec §7)., test_ejercicio_del_libro_con_su_resultado_pasa(), test_ejercicio_del_libro_sin_su_resultado_va_a_revision() (+14 more)

### Community 36 - "`explorer/` — revisor visual del pipeline"
Cohesion: 0.29
Nodes (6): Cómo correr, El árbol y la cobertura, `explorer/` — revisor visual del pipeline, La revisión, Navegación, Vistas

### Community 37 - "run_ref"
Cohesion: 0.29
Nodes (8): 10. Contrato v2 del bundle, iso(), datetime, Clave estable de una corrida: `{model}--{mode}--{inicio compacto UTC}`., Fecha en el formato del contrato: ISO 8601 UTC con `Z`. SQLite devuelve los…, run_ref(), test_fecha_ingenua_se_lee_como_utc(), test_ref_de_corrida_es_estable()

### Community 38 - "families.py"
Cohesion: 0.09
Nodes (21): Generación de preguntas por ventanas (qgen v2) — Plan de implementación, Global Constraints, Review Focus, Task 10: Contrato v2 del bundle, Task 12: Verificación final y prueba real, Task 2: Ventanas, Task 3: Esquemas de salida de la llamada por ventana, Task 5: Instrucciones por familia (+13 more)

### Community 39 - "_run_immediate"
Cohesion: 0.13
Nodes (21): actual_cost_usd(), Compute actual cost from observed usage_metadata totals. `cache_create_tokens`…, finalize_run(), Mapea GeneratedQuestion de Pydantic + metadatos de corrida a filas del ORM., GenerationRun, Una corrida = N preguntas para un manual con un set de reglas y un modelo…, _Accepted, _run_immediate() (+13 more)

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
Cohesion: 0.22
Nodes (17): gzip, hashlib, _bool(), _dict(), find_secrets(), walk(), _int(), _is_iso() (+9 more)

### Community 46 - "GeminiClient"
Cohesion: 0.16
Nodes (8): GeminiClient, Thin wrapper around google-genai with explicit context caching. We keep this…, ClassifiedHeading, GeminiHeadingClassifier, HeadingClassificationBatch, BaseModel, Gemini-based fallback classifier for ambiguous headings. Used only when the…, T

### Community 47 - "Question"
Cohesion: 0.08
Nodes (33): DuplicateNodeRef, DuplicateRunRef, _materia_hint(), _pipeline_commit(), _qgen_version(), Arma el bundle a partir del SQLite del pipeline. Separado del CLI para poder…, SHA-256 del PDF de origen, si sigue estando donde dice el manual., Commit del repo de contenido, para poder reproducir una entrega vieja. (+25 more)

### Community 48 - "hierarchy_tree.py"
Cohesion: 0.36
Nodes (7): collections_abc, _icon_for(), _indent(), Hierarchy tree rendered as nested expanders with optional click-to-navigate., Render the manual's tree. `on_select` is a function that takes a NodeSummary…, _render_node(), render_tree()

### Community 55 - "run_generation"
Cohesion: 0.14
Nodes (17): Task 7: Columnas nuevas, migración y persistencia, Task 9: Corrida por ventanas, estimación y CLI (retira el flujo viejo), main(), _print_estimate(), _print_summary(), _progress_cb(), command, --regenerate: borra las preguntas de las ventanas que se van a rehacer y las… (+9 more)

### Community 56 - "DuplicateIndex"
Cohesion: 0.12
Nodes (14): DuplicateIndex, norm_text(), _nucleo(), Enunciados ya aceptados, por nodo, para descartar duplicadas (spec §7). En…, El enunciado desde el primer «¿»: sin el prefijo común de la familia militar., Similitud simétrica: `SequenceMatcher` da valores distintos según el orden., Para comparar texto literal: NFC, espacios colapsados, comillas y guiones…, _similitud() (+6 more)

### Community 57 - "importer.py"
Cohesion: 0.09
Nodes (28): csv, qgen_reference_importer, qgen_reference_repository, main(), command, Path, Comando CLI para importar un banco de preguntas de referencia (ejemplos oro) a…, Carga un archivo de preguntas de ejemplo y las guarda en la base de datos. (+20 more)

### Community 58 - "persist_question"
Cohesion: 0.32
Nodes (14): seed_questions(), create_run(), load_manual(), persist_question(), Any, Session, _make_question(), Two different GenerationRuns for the same node are allowed (re-generation). (+6 more)

### Community 59 - "Generación de preguntas por ventanas (qgen v2)"
Cohesion: 0.15
Nodes (13): 11. Trabajo en la webapp (lo hace el usuario), 13. Errores, 14. Pruebas (TDD), 15. Riesgos, 1. Contexto, 2. Decisiones del usuario, 3. Alcance, 4. Ventanas (+5 more)

### Community 60 - "WindowQuestion"
Cohesion: 0.25
Nodes (11): model_validator, Una pregunta completa tal como la devuelve la llamada por ventana., WindowQuestion, test_la_respuesta_de_ventana_es_una_lista_de_preguntas(), test_una_pregunta_de_ventana_valida(), test_ventana_rechaza_cita_vacia(), test_ventana_rechaza_opciones_repetidas(), test_ventana_rechaza_reparto_de_roles_incorrecto() (+3 more)

### Community 61 - "checks.py"
Cohesion: 0.17
Nodes (12): difflib, pydantic, _literal(), norm_math(), parse_items(), Revisiones de cada pregunta generada por ventana (spec §7). Todo es…, ¿Está `fragmento` literal en `texto`? Se acepta también con la notación…, Como `norm_text`, pero además iguala la notación: 𝑥² y x^2 quedan como x2 (así… (+4 more)

### Community 62 - "test_plan_windows.py"
Cohesion: 0.39
Nodes (11): _keys(), Qué ventanas procesa una corrida (spec §4): selección, reanudación y --limit., _seed(), test_gana_el_ultimo_estado_de_cada_ventana(), test_las_introducciones_quedan_fuera(), test_limit_cuenta_ventanas(), test_regenerate_ignora_el_historial(), test_se_saltan_las_ventanas_ok_y_se_reintentan_las_fallidas() (+3 more)

### Community 63 - "5_🔍_Search.py"
Cohesion: 0.25
Nodes (9): Full-text search across chunks via SQLite FTS5., init_fts(), BaseModel, query(), Full-text search over chunks using SQLite FTS5. We create a virtual table…, FTS5 has reserved chars; we wrap free-form input as a phrase if needed., Create FTS5 virtual table + triggers if missing, then backfill any chunks that…, _sanitize() (+1 more)

### Community 64 - "os"
Cohesion: 0.29
Nodes (4): google, os, requests, urllib_request

### Community 65 - "test_geografia_moderna_mexico.py"
Cohesion: 0.48
Nodes (6): Perfil `geografia_moderna_mexico`: el temario de la imagen, como Capítulo ›…, test_cada_tema_cuelga_de_su_capitulo(), test_el_arbol_es_el_de_la_imagen(), test_lo_que_no_esta_en_la_imagen_queda_fuera(), test_los_subtitulos_y_los_capitulos_completos_quedan_como_texto(), _tree()

### Community 66 - "test_temario.py"
Cohesion: 0.48
Nodes (6): Perfil `taller_lectura_redaccion`: solo el temario pedido, como Bloque › Parte.…, test_cada_parte_cuelga_de_su_bloque(), test_cada_parte_lleva_solo_su_texto(), test_lo_que_no_esta_en_la_imagen_no_queda_en_ningun_nodo(), test_solo_quedan_los_bloques_y_partes_de_la_imagen(), _tree()

### Community 67 - "test_historia_universal.py"
Cohesion: 0.53
Nodes (5): Perfil `historia_universal`: el temario de la imagen, como Capítulo › Tema.…, test_cada_tema_cuelga_del_capitulo(), test_el_arbol_es_el_capitulo_y_sus_cuatro_temas(), test_los_subtitulos_quedan_en_el_cuerpo_de_su_tema(), _tree()

### Community 68 - "test_cost.py"
Cohesion: 0.53
Nodes (5): _estimate(), Estimación de costo por ventanas (spec §9)., test_cuenta_preguntas_y_verificaciones_por_caracteres(), test_sin_ejercicios_no_hay_verificaciones(), test_sin_ventanas_no_cuesta_nada()

### Community 69 - "OptionExemplarInput"
Cohesion: 0.40
Nodes (5): OptionExemplarInput, BaseModel, QuestionExemplarInput, Modelo Pydantic para validar una opción de respuesta de ejemplo., Modelo Pydantic para validar una pregunta de ejemplo completa.

### Community 70 - "match_libro"
Cohesion: 0.50
Nodes (4): match_libro(), test_libro_with_trailing_title(), test_match_libro(), test_match_libro_with_accents()

### Community 71 - "to_generated"
Cohesion: 0.50
Nodes (4): _barajadas(), La pregunta lista para guardar, con las opciones barajadas de forma…, to_generated(), test_la_correcta_no_queda_siempre_primera()

## Knowledge Gaps
- **47 isolated node(s):** `Workflow: graphify`, `graphify`, `graphify en Windows`, `1. Por qué existe`, `2. Forma del fichero` (+42 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 419 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `session_scope()` connect `session_scope` to `6_❓_Preguntas.py`, `test_pipeline.py`, `_seed`, `questions_access.py`, `data_access.py`, `Question`, `etl/pipeline.py`, `session.py`, `run_generation`, `etl/models/schema.py`, `test_plan_windows.py`, `importer.py`, `persist_question`, `batch_status.py`, `5_🔍_Search.py`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Why does `manuals()` connect `etl/models/schema.py` to `Contrato: bundle de contenido v2`, `session_scope`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `init_question_tables()` (e.g. with `seed_questions()` and `Task 7: Columnas nuevas, migración y persistencia`) actually correct?**
  _`init_question_tables()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `RawElement` (e.g. with `ChunkConsolidator` and `UnstructuredAdapter`) actually correct?**
  _`RawElement` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `build_bundle()` (e.g. with `Task 10: Contrato v2 del bundle` and `Chunk`) actually correct?**
  _`build_bundle()` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `Manual` (e.g. with `estimate_doc()` and `main()`) actually correct?**
  _`Manual` has 24 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Workflow: graphify`, `graphify`, `graphify en Windows` to the rest of the system?**
  _47 weakly-connected nodes found - possible documentation gaps or missing edges._