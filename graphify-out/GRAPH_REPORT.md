# Graph Report - onmy-military-library-contenido  (2026-09-25)

## Corpus Check
- 164 files · ~94,006 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 6, .example 1, .lock 1)

## Summary
- 1540 nodes · 4293 edges · 85 communities (75 shown, 10 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 556 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2d06a425`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- DocumentRules
- test_bundle_spec.py
- test_pipeline.py
- test_claude_code.py
- Contrato: bundle de contenido v2
- profile.py
- questions_access.py
- session_scope
- get_default_rules
- types.py
- toc_parser.py
- data_access.py
- RawElement
- test_patterns.py
- bundle/__init__.py
- BaldorExerciseExtractor
- HeadingMatch
- json
- test_claude_review.py
- get_profile
- debug_pymupdf.py
- session.py
- test_rules.py
- Manual
- smoke_imports.py
- temario.py
- _seed
- consolidator.py
- ElementKind
- test_baldor_patterns.py
- gemini/generate.py
- _bundle
- test_algebra_trigonometria_geometria_analitica.py
- claude_review.py
- schemas.py
- test_checks.py
- `explorer/` — revisor visual del pipeline
- run_ref
- Review Focus
- process
- test_calculo_una_variable.py
- export.py
- etl
- workflows/graphify.md
- CLAUDE.md
- spec.py
- GeminiClient
- etl/pipeline.py
- pytest
- validation/__init__.py
- report.py
- checks.py
- importer.py
- Question
- Generación de preguntas por ventanas (qgen v2)
- WindowQuestion
- Niveles cognitivos en la generación de preguntas (qgen v3)
- test_plan_windows.py
- search.py
- pydantic
- test_geografia_moderna_mexico.py
- test_temario.py
- test_historia_universal.py
- init_question_tables
- _resolve_rules
- 6_❓_Preguntas.py
- os
- bakeoff.py
- get_level_exemplars
- qgen/pipeline.py
- test_toc_parser.py
- test_baldor_rules.py
- test_reference_importer.py
- test_niveles.py
- _normalize
- QuestionExemplarInput
- test_cost.py
- reference_schema.py
- main
- _parse

## God Nodes (most connected - your core abstractions)
1. `session_scope()` - 91 edges
2. `init_question_tables()` - 54 edges
3. `Question` - 48 edges
4. `RawElement` - 40 edges
5. `Manual` - 39 edges
6. `_run_immediate()` - 37 edges
7. `get_default_rules()` - 34 edges
8. `Chunk` - 33 edges
9. `build_bundle()` - 33 edges
10. `_errors()` - 33 edges

## Surprising Connections (you probably didn't know these)
- `4. Identidad: las claves estables` --references--> `manuals()`  [INFERRED]
  CONTRATO-BUNDLE.md → etl/src/etl/cli/inspect_cli.py
- `Notas por bloque` --references--> `manuals()`  [INFERRED]
  CONTRATO-BUNDLE.md → etl/src/etl/cli/inspect_cli.py
- `Task 10: Prueba piloto con Geografía (manual 11)` --references--> `plan_windows()`  [INFERRED]
  docs/superpowers/plans/2026-09-25-qgen-niveles-cognitivos.md → question_generator/src/qgen/pipeline.py
- `Task 3: Esquemas de salida de la llamada por ventana` --references--> `QuestionType`  [INFERRED]
  docs/superpowers/plans/2026-09-23-qgen-ventanas.md → question_generator/src/qgen/prompts/schemas.py
- `5. Modelo de datos` --references--> `WindowQuestion`  [INFERRED]
  docs/superpowers/specs/2026-09-25-qgen-niveles-cognitivos-design.md → question_generator/src/qgen/prompts/schemas.py

## Import Cycles
- None detected.

## Communities (85 total, 10 thin omitted)

### Community 0 - "DocumentRules"
Cohesion: 0.19
Nodes (13): Task 1: Familia y tipos en las reglas, 5. Familias y tipos, DocumentRules, Any, Per-archetype question-generation rules + per-document override mechanism. The…, Knobs that shape question generation for a class of documents., rules_from_dict(), rules_to_dict() (+5 more)

### Community 1 - "test_bundle_spec.py"
Cohesion: 0.11
Nodes (34): copy, _errors(), El contrato del bundle: lo que se acepta y, sobre todo, lo que no. Cada caso de…, test_api_key_en_metadata_bloquea_la_entrega(), test_arbol_sin_raiz(), test_cadena_de_conexion_en_metadata_bloquea_la_entrega(), test_ciclo_en_el_arbol(), mutate() (+26 more)

### Community 2 - "test_pipeline.py"
Cohesion: 0.17
Nodes (43): Las preguntas crudas de una ventana (sin validar) y lo que costó pedirlas., VerificationOutcome, WindowOutcome, _ejercicio_nuevo(), _estimate(), FakeGemini, _item(), _letra() (+35 more)

### Community 3 - "test_claude_code.py"
Cohesion: 0.22
Nodes (27): nombre_de(), La clave `nodo:desde-hasta` como nombre de archivo (Windows no admite `:`)., _exportar(), _importar(), _item(), _pendientes(), fixture, _questions() (+19 more)

### Community 4 - "Contrato: bundle de contenido v2"
Cohesion: 0.04
Nodes (44): 1. Por qué existe, 2. Forma del fichero, 3. Estructura, 4. Identidad: las claves estables, 5. Las validaciones, 6. Los dos comandos, 7. Versionado del contrato, Aquí — `qgen-export` (+36 more)

### Community 5 - "profile.py"
Cohesion: 0.16
Nodes (25): HeadingCandidate, match_anexo(), match_baldor_capitulo(), match_baldor_caso(), match_baldor_subseccion_romana(), match_baldor_tema_mayusculas(), match_bloque(), match_capitulo() (+17 more)

### Community 6 - "questions_access.py"
Cohesion: 0.09
Nodes (40): Task 11: Explorador: tipo, cita y motivos, Task 8: Explorador: nivel, filtro e indicadores, _render_question(), get_question_kpis(), level_label(), list_questions(), list_runs(), nodes_missing_questions() (+32 more)

### Community 7 - "session_scope"
Cohesion: 0.14
Nodes (33): session_scope(), build_bundle(), DuplicateNodeRef, DuplicateRunRef, _materia_hint(), _pipeline_commit(), Any, Session (+25 more)

### Community 8 - "get_default_rules"
Cohesion: 0.19
Nodes (21): build_window_instruction(), _conforme(), Instrucción del sistema para la llamada por ventana: plantilla de la familia +…, "Conforme al Manual …" pero "Conforme a la Ley …": el artículo concuerda con el…, get_default_rules(), Instrucciones de la llamada por ventana, por familia (spec §6)., test_con_ejercicios_se_piden_el_del_libro_y_uno_nuevo_sin_subir_la_dificultad(), test_el_mensaje_lleva_ruta_paginas_y_texto() (+13 more)

### Community 9 - "types.py"
Cohesion: 0.14
Nodes (15): ABC, ExtractorBase, Path, Common interface for layout extractors. Adapters (Docling, Unstructured, etc.)…, Run the extractor on a PDF and return normalized elements., DoclingAdapter, _first_bbox(), Path (+7 more)

### Community 10 - "toc_parser.py"
Cohesion: 0.20
Nodes (16): detect_toc_pages(), _infer_depth(), _is_roman_only(), _lookback_marker(), _parse_page_number(), parse_toc(), _peek_parte_title(), BaseModel (+8 more)

### Community 11 - "data_access.py"
Cohesion: 0.12
Nodes (29): graphify, _icon_for(), _indent(), Hierarchy tree rendered as nested expanders with optional click-to-navigate., Render the manual's tree. `on_select` is a function that takes a NodeSummary…, _render_node(), render_tree(), _chunk_to_summary() (+21 more)

### Community 12 - "RawElement"
Cohesion: 0.16
Nodes (11): TocResult, One layout element extracted from a PDF page. Both Docling and Unstructured…, RawElement, _Builder, HierarchyAssembler, _peek_next_title(), Assembles a tree from raw elements, optionally guided by a TOC. Parameters…, Look ahead up to 3 elements for something that acts as the heading title. (+3 more)

### Community 13 - "test_patterns.py"
Cohesion: 0.10
Nodes (32): classify_heading(), match_articulo(), match_libro(), match_titulo(), Compatibility shim: classify using the default 'manual' profile. New code…, Default classify_heading uses 'manual' profile — articles are not its concern…, test_anexo(), test_articulo_quater() (+24 more)

### Community 14 - "bundle/__init__.py"
Cohesion: 0.18
Nodes (17): Bundle de contenido: la interfaz entre la generación de preguntas y la webapp., dumps(), Path, Serialización canónica: UTF-8, indentado a 2, sin escapar acentos., Escribe el bundle (comprimiendo si es grande) y su `.sha256`. Devuelve `(ruta…, Comprueba el `.sha256` que acompaña al bundle. Lanza si no cuadra., Lee un bundle `.json` o `.json.gz`. No valida: para eso está `validate`., read_bundle() (+9 more)

### Community 15 - "BaldorExerciseExtractor"
Cohesion: 0.11
Nodes (18): BaldorExercise, BaldorExerciseExtractor, flush_current(), Extractor de ejercicios resueltos y problemas prácticos de Álgebra de Baldor., Genera el texto estructurado del ejercicio para el prompt de generación de…, Analizador para extraer problemas numerados, procedimientos y soluciones., Extrae la lista de ejercicios presentes en un bloque de texto., Parsea el bloque de texto de un ejercicio individual extrayendo enunciado,… (+10 more)

### Community 16 - "HeadingMatch"
Cohesion: 0.50
Nodes (3): HeadingMatch, Profile-resolved heading match: kind + numeric depth., Return a profile-resolved HeadingMatch, or None if not a heading.

### Community 17 - "json"
Cohesion: 0.13
Nodes (4): Inspect a cached docling extraction to find LIBRO/TITULO lines and Latin-suffix…, json, pickle, sqlite3

### Community 18 - "test_claude_review.py"
Cohesion: 0.31
Nodes (28): _como(), _estado(), _exportar_revision(), _generar(), _importar_revision(), _item(), _lotes(), _marcar() (+20 more)

### Community 19 - "get_profile"
Cohesion: 0.20
Nodes (16): auto_detect_profile(), get_profile(), Heuristic profile pick based on the first few elements' text. Looks for genre-…, _el(), test_autodetect_algebra_baldor(), test_autodetect_codigo_legal(), test_autodetect_falls_back_to_manual_for_empty(), test_autodetect_manual() (+8 more)

### Community 20 - "debug_pymupdf.py"
Cohesion: 0.22
Nodes (6): One-off debug script: inspect characters used as TOC leaders., fitz, pymupdf, rapidocr, sys, unicodedata

### Community 21 - "session.py"
Cohesion: 0.23
Nodes (10): contextlib, Engine, init_db(), Create all tables. Idempotent — safe to run on existing DBs., _default_db_url(), get_engine(), get_session_factory(), Session (+2 more)

### Community 22 - "test_rules.py"
Cohesion: 0.14
Nodes (11): parametrize, test_algebra_trigonometria_geometria_analitica_tiene_reglas_de_generacion(), test_cada_perfil_tiene_su_familia_y_sus_tipos(), test_calculo_una_variable_tiene_reglas_de_generacion(), test_familia_o_tipo_desconocido_se_rechaza(), test_geografia_moderna_mexico_tiene_reglas_de_generacion(), test_get_default_rules_known(), test_get_default_rules_unknown_raises() (+3 more)

### Community 23 - "Manual"
Cohesion: 0.09
Nodes (36): DeclarativeBase, estimate_doc(), main(), Compute approximate Gemini cost for question generation across ingested…, ConsolidatedChunk, BaseModel, manuals(), node() (+28 more)

### Community 25 - "temario.py"
Cohesion: 0.20
Nodes (11): match_parte_temario(), Parte numerada de un temario ('1.1 Los elementos del proceso comunicativo').…, CapitulosConTemas, _norm(), _numero_de_tema(), Selección por temario: qué bloques, partes, capítulos o temas de un libro…, (número, resto del encabezado) si el encabezado abre un capítulo., Devuelve los elementos (con su índice original) que entran al árbol. - El… (+3 more)

### Community 26 - "_seed"
Cohesion: 0.35
Nodes (11): AppTest, _open_page(), Pestaña "Exportar Bundle" de la página de preguntas, ejecutada con AppTest. La…, _seed(), test_la_cita_se_muestra_tal_cual(), test_la_pregunta_muestra_la_revision_de_claude_con_su_calificacion(), test_la_pregunta_muestra_su_nivel_junto_al_tipo(), test_la_pregunta_muestra_su_tipo_y_sus_motivos() (+3 more)

### Community 27 - "consolidator.py"
Cohesion: 0.17
Nodes (12): Prueba unitaria del reordenamiento de fracciones romanas., ChunkConsolidator, Consolida los elementos del cuerpo de cada nodo hoja en fragmentos con límite…, Convierte un número romano a entero, o None si no es válido., Reordena fracciones romanas que docling extrajo en orden incorrecto. Docling a…, HierarchyNode, HierarchyTree, BaseModel (+4 more)

### Community 28 - "ElementKind"
Cohesion: 0.14
Nodes (23): docling_core_types_doc, DoclingDocument, elements_from_document(), _first_page(), Normalize a DoclingDocument's items to :class:`RawElement`, in reading order., ElementKind, StrEnum, Manual profile builds PARTE → Capítulo → Sección hierarchy from body. (+15 more)

### Community 29 - "test_baldor_patterns.py"
Cohesion: 0.11
Nodes (17): match_baldor_inciso(), Reconoce subcasos con inciso alfabético (ej. 'a) Factor común monomio.')., Pruebas unitarias para los patrones y jerarquía de Álgebra de Baldor., Verifica subcasos con letras tipo a) o b)., Verifica que el perfil 'algebra_baldor' solo clasifica capítulos a nivel 0 y no…, En Álgebra de Baldor los únicos nodos son los 16 capítulos ('I. Suma' … 'XXXII.…, Verifica que los capítulos con numeración romana se reconocen con su ordinal y…, Verifica las subsecciones con números romanos en mayúsculas. (+9 more)

### Community 30 - "gemini/generate.py"
Cohesion: 0.06
Nodes (62): dataclasses, functools, logging, _check_once(), main(), _print_run_card(), _print_running(), command (+54 more)

### Community 31 - "_bundle"
Cohesion: 0.12
Nodes (18): Review Focus, Task 10: Prueba piloto con Geografía (manual 11), Task 7: Contrato v3 del bundle, Task 9: Documentación, grafo y verificación completa, _bundle(), _options(), Un bundle mínimo pero completo y válido., `cost_input_tokens` contiene 'token': el detector no debe morder ahí. (+10 more)

### Community 32 - "test_algebra_trigonometria_geometria_analitica.py"
Cohesion: 0.53
Nodes (5): Perfil `algebra_trigonometria_geometria_analitica`: los cuatro capítulos de la…, test_el_arbol_son_los_cuatro_capitulos_de_la_imagen(), test_la_portada_queda_fuera(), test_secciones_ejemplos_y_teoremas_quedan_en_el_cuerpo_de_su_capitulo(), _tree()

### Community 33 - "claude_review.py"
Cohesion: 0.06
Nodes (74): Task 6: Revisión con Claude: nivel, reclasificación y "solo clasificar", Protocol, carpeta_por_defecto(), clave_de(), Exportacion, exportar(), importar(), _instruccion() (+66 more)

### Community 34 - "schemas.py"
Cohesion: 0.13
Nodes (21): collections, collections_abc, Task 6: Llamadas a Gemini: ventana y verificación, 12. Organización del código, enum, obtain(), build_verification_instruction(), build_verification_message() (+13 more)

### Community 35 - "test_checks.py"
Cohesion: 0.11
Nodes (34): Global Constraints, Niveles cognitivos en qgen (v3) — Plan de implementación, DuplicateIndex, Enunciados ya aceptados, por nodo, para descartar duplicadas (spec §7). En…, Revisión por tipo contra el texto de la ventana (spec §7, tabla de revisiones)., review(), Verdict, _nivel() (+26 more)

### Community 36 - "`explorer/` — revisor visual del pipeline"
Cohesion: 0.29
Nodes (6): Cómo correr, El árbol y la cobertura, `explorer/` — revisor visual del pipeline, La revisión, Navegación, Vistas

### Community 37 - "run_ref"
Cohesion: 0.29
Nodes (8): 10. Contrato v2 del bundle, iso(), datetime, Clave estable de una corrida: `{model}--{mode}--{inicio compacto UTC}`., Fecha en el formato del contrato: ISO 8601 UTC con `Z`. SQLite devuelve los…, run_ref(), test_fecha_ingenua_se_lee_como_utc(), test_ref_de_corrida_es_estable()

### Community 38 - "Review Focus"
Cohesion: 0.22
Nodes (8): Generación de preguntas por ventanas (qgen v2) — Plan de implementación, Global Constraints, Review Focus, Task 12: Verificación final y prueba real, Task 2: Ventanas, Task 3: Esquemas de salida de la llamada por ventana, Task 5: Instrucciones por familia, Task 8: Planificación de ventanas y reanudación

### Community 39 - "process"
Cohesion: 0.20
Nodes (11): _Accepted, process(), _WindowResult, parse_items(), Motivos de revisión según la verificación. Nombra las opciones por su texto:…, Valida cada pregunta por separado: una mala no tumba a las demás., tipo_permitido(), verification_motivos() (+3 more)

### Community 40 - "test_calculo_una_variable.py"
Cohesion: 0.53
Nodes (5): Perfil `calculo_una_variable`: los tres capítulos completos de la imagen.…, test_el_arbol_son_los_tres_capitulos_de_la_imagen(), test_la_portada_queda_fuera(), test_secciones_y_subtitulos_quedan_en_el_cuerpo_de_su_capitulo(), _tree()

### Community 41 - "export.py"
Cohesion: 0.22
Nodes (12): date, SHA-256 del PDF de origen, si sigue estando donde dice el manual., source_digest(), bundle_filename(), next_version(), Siguiente `v{n}` libre para este manual en `out_dir`. Se cuenta por manual y no…, slug(), main() (+4 more)

### Community 42 - "etl"
Cohesion: 1.00
Nodes (3): etl, explorer, question_generator

### Community 45 - "spec.py"
Cohesion: 0.22
Nodes (17): gzip, hashlib, _bool(), _dict(), find_secrets(), walk(), _int(), _is_iso() (+9 more)

### Community 46 - "GeminiClient"
Cohesion: 0.29
Nodes (3): GeminiClient, GeminiHeadingClassifier, T

### Community 47 - "etl/pipeline.py"
Cohesion: 0.12
Nodes (22): main(), Path, Quick visual inspection of an in-memory hierarchy without persisting., main(), command, Path, _label_for_depth(), Build a manual's hierarchy tree from extracted elements + optional TOC.… (+14 more)

### Community 48 - "pytest"
Cohesion: 0.15
Nodes (10): _isolate_data_dir(), fixture, Cada test obtiene un directorio de datos limpio y un SQLite aislado., _isolate_data_dir(), fixture, Cada prueba obtiene una base de datos limpia y aislada. Limpia el lru_cache de…, pytest, _isolate_data_dir() (+2 more)

### Community 55 - "report.py"
Cohesion: 0.29
Nodes (8): build_report(), BaseModel, Session, QualityReport, Quality report for an ingested manual. Computes: - TOC coverage: % of TOC…, get_quality_report_dict(), Any, Returns the QualityReport as a plain dict (cache-friendly).

### Community 56 - "checks.py"
Cohesion: 0.10
Nodes (23): difflib, Task 2: Revisión automática por nivel, 7. Revisión automática por nivel, _barajadas(), _copiado(), _literal(), norm_math(), norm_text() (+15 more)

### Community 57 - "importer.py"
Cohesion: 0.19
Nodes (13): csv, Modelo de opción de respuesta para una pregunta de referencia., ReferenceOption, import_reference_questions(), limpiar_ejemplo(), _load_xlsx(), Any, Session (+5 more)

### Community 58 - "Question"
Cohesion: 0.15
Nodes (29): Inserta preguntas generadas directamente en el chat para el manual 11 (Álgebra…, seed_questions(), datetime, Task 10: Contrato v2 del bundle, Task 7: Columnas nuevas, migración y persistencia, 8. Persistencia, create_run(), load_manual() (+21 more)

### Community 59 - "Generación de preguntas por ventanas (qgen v2)"
Cohesion: 0.15
Nodes (12): 11. Trabajo en la webapp (lo hace el usuario), 13. Errores, 14. Pruebas (TDD), 15. Riesgos, 1. Contexto, 2. Decisiones del usuario, 3. Alcance, 4. Ventanas (+4 more)

### Community 60 - "WindowQuestion"
Cohesion: 0.12
Nodes (32): Task 4: Revisiones de cada pregunta, Task 1: Niveles y esquema de la respuesta, GeneratedOption, GeneratedQuestion, OptionRole, model_validator, StrEnum, Una pregunta completa tal como la devuelve la llamada por ventana. (+24 more)

### Community 61 - "Niveles cognitivos en la generación de preguntas (qgen v3)"
Cohesion: 0.12
Nodes (15): 10. Trabajo en la webapp (lo hace el usuario), 11. Explorador y CLI, 12. Organización del código, 13. Pruebas (TDD), 14. Prueba piloto, 15. Riesgos, 1. Contexto, 2. Decisiones del usuario (+7 more)

### Community 62 - "test_plan_windows.py"
Cohesion: 0.39
Nodes (11): _keys(), Qué ventanas procesa una corrida (spec §4): selección, reanudación y --limit., _seed(), test_gana_el_ultimo_estado_de_cada_ventana(), test_las_introducciones_quedan_fuera(), test_limit_cuenta_ventanas(), test_regenerate_ignora_el_historial(), test_se_saltan_las_ventanas_ok_y_se_reintentan_las_fallidas() (+3 more)

### Community 63 - "search.py"
Cohesion: 0.28
Nodes (8): init_fts(), BaseModel, query(), Full-text search over chunks using SQLite FTS5. We create a virtual table…, FTS5 has reserved chars; we wrap free-form input as a phrase if needed., Create FTS5 virtual table + triggers if missing, then backfill any chunks that…, _sanitize(), SearchHit

### Community 64 - "pydantic"
Cohesion: 0.28
Nodes (6): Thin wrapper around google-genai with explicit context caching. We keep this…, ClassifiedHeading, HeadingClassificationBatch, BaseModel, Gemini-based fallback classifier for ambiguous headings. Used only when the…, pydantic

### Community 65 - "test_geografia_moderna_mexico.py"
Cohesion: 0.48
Nodes (6): Perfil `geografia_moderna_mexico`: el temario de la imagen, como Capítulo ›…, test_cada_tema_cuelga_de_su_capitulo(), test_el_arbol_es_el_de_la_imagen(), test_lo_que_no_esta_en_la_imagen_queda_fuera(), test_los_subtitulos_y_los_capitulos_completos_quedan_como_texto(), _tree()

### Community 66 - "test_temario.py"
Cohesion: 0.48
Nodes (6): Perfil `taller_lectura_redaccion`: solo el temario pedido, como Bloque › Parte.…, test_cada_parte_cuelga_de_su_bloque(), test_cada_parte_lleva_solo_su_texto(), test_lo_que_no_esta_en_la_imagen_no_queda_en_ningun_nodo(), test_solo_quedan_los_bloques_y_partes_de_la_imagen(), _tree()

### Community 67 - "test_historia_universal.py"
Cohesion: 0.53
Nodes (5): Perfil `historia_universal`: el temario de la imagen, como Capítulo › Tema.…, test_cada_tema_cuelga_del_capitulo(), test_el_arbol_es_el_capitulo_y_sus_cuatro_temas(), test_los_subtitulos_quedan_en_el_cuerpo_de_su_tema(), _tree()

### Community 68 - "init_question_tables"
Cohesion: 0.09
Nodes (34): Task 9: Corrida por ventanas, estimación y CLI (retira el flujo viejo), exportar_cmd(), exportar_revision_cmd(), importar_cmd(), importar_revision_cmd(), command, Path, `qgen-claude`: generar preguntas desde Claude Code, sin API (ver… (+26 more)

### Community 69 - "_resolve_rules"
Cohesion: 0.39
Nodes (8): _resolve_rules(), merge_rules(), Sparse overrides to layer over a profile default. Stored at…, RulesOverride, test_el_override_no_cambia_familia_ni_tipos(), test_merge_with_none_override_returns_default(), test_override_replaces_only_provided_fields(), test_rules_override_from_empty_dict()

### Community 70 - "6_❓_Preguntas.py"
Cohesion: 0.12
Nodes (28): dotenv, kpi_row(), Render a row of `st.metric` cards. items is a list of (label, value,…, cache_data, Render a single PDF page to PNG bytes via PyMuPDF., Return PNG bytes of the given page (1-based), or None if unavailable. Cached so…, Convenience: render and display in one call., render_page() (+20 more)

### Community 71 - "os"
Cohesion: 0.29
Nodes (4): google, os, requests, urllib_request

### Community 72 - "bakeoff.py"
Cohesion: 0.36
Nodes (7): main(), _print_table(), command, Path, Run both extractors with persistence disabled and emit a comparison., _render_markdown(), rich_table

### Community 73 - "get_level_exemplars"
Cohesion: 0.30
Nodes (11): Task 4: Ejemplos por nivel (importador xlsx y repositorio), Modelo de base de datos para una pregunta de referencia u oro., ReferenceQuestion, _as_dict(), get_level_exemplars(), get_reference_exemplars(), Any, Session (+3 more)

### Community 74 - "qgen/pipeline.py"
Cohesion: 0.09
Nodes (41): concurrent_futures, Task 3: Columnas, guardado y conteo por nivel, _model_option(), actual_cost_usd(), doc_token_estimate(), estimate_windows(), Cost accounting: predictions before a run + actual after. Pricing (USD per 1M…, Compute actual cost from observed usage_metadata totals. `cache_create_tokens`… (+33 more)

### Community 75 - "test_toc_parser.py"
Cohesion: 0.40
Nodes (5): _find_sample(), Path, Smoke test for the TOC parser using the real DN M 1455 sample PDF. The test is…, test_dn_m_1455_toc_extraction(), skipif

### Community 76 - "test_baldor_rules.py"
Cohesion: 0.33
Nodes (5): Pruebas unitarias para las reglas y prompts de generación de preguntas de…, La instrucción por ventana lleva las reglas de Baldor y pide ejercicios., Verifica que el perfil 'algebra_baldor' está registrado en el catálogo de…, test_algebra_baldor_prompt_rendering(), test_algebra_baldor_rules_registered()

### Community 77 - "test_reference_importer.py"
Cohesion: 0.20
Nodes (13): openpyxl, qgen_reference_importer, qgen_reference_repository, load_reference_file(), Path, Carga datos de preguntas desde un archivo JSON, JSONL o CSV., parametrize, Pruebas unitarias para la importación y consulta de preguntas de referencia… (+5 more)

### Community 78 - "test_niveles.py"
Cohesion: 0.33
Nodes (3): Niveles cognitivos: valores, proporción y definiciones compartidas., test_la_proporcion_es_55_15_15_15(), test_una_ventana_con_3_de_conocimiento_debe_traer_los_otros_niveles()

### Community 79 - "_normalize"
Cohesion: 0.67
Nodes (3): _normalize(), Loose match: strip accents, lowercase, collapse whitespace., Título comparable: sin acentos, sin puntuación y en minúsculas. El TOC y los…

### Community 80 - "QuestionExemplarInput"
Cohesion: 0.29
Nodes (6): field_validator, OptionExemplarInput, BaseModel, QuestionExemplarInput, Modelo Pydantic para validar una opción de respuesta de ejemplo., Modelo Pydantic para validar una pregunta de ejemplo completa.

### Community 81 - "test_cost.py"
Cohesion: 0.27
Nodes (9): Task 5: Prompt de generación con niveles, _ejemplos(), Any, Ejemplos de referencia; si no hay, los militares de siempre solo en la familia…, _estimate(), Estimación de costo por ventanas (spec §9)., test_cuenta_preguntas_y_verificaciones_por_caracteres(), test_sin_ejercicios_no_hay_verificaciones() (+1 more)

### Community 82 - "reference_schema.py"
Cohesion: 0.50
Nodes (4): datetime, Esquema SQLAlchemy para preguntas de referencia (banco de ejemplos/exemplars).…, Retorna la fecha y hora actual en UTC., _utcnow()

### Community 83 - "main"
Cohesion: 0.50
Nodes (4): main(), command, Path, Carga un archivo de preguntas de ejemplo y las guarda en la base de datos.

## Knowledge Gaps
- **62 isolated node(s):** `Workflow: graphify`, `graphify`, `graphify en Windows`, `1. Por qué existe`, `2. Forma del fichero` (+57 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 481 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `session_scope()` connect `session_scope` to `test_pipeline.py`, `_seed`, `init_question_tables`, `test_claude_code.py`, `6_❓_Preguntas.py`, `questions_access.py`, `export.py`, `data_access.py`, `etl/pipeline.py`, `test_claude_review.py`, `main`, `session.py`, `report.py`, `Manual`, `test_plan_windows.py`, `Question`, `gemini/generate.py`, `search.py`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Why does `manuals()` connect `Manual` to `Contrato: bundle de contenido v2`, `session_scope`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `init_question_tables()` (e.g. with `seed_questions()` and `Task 7: Columnas nuevas, migración y persistencia`) actually correct?**
  _`init_question_tables()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 38 inferred relationships involving `Question` (e.g. with `Task 7: Columnas nuevas, migración y persistencia` and `Task 3: Columnas, guardado y conteo por nivel`) actually correct?**
  _`Question` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `RawElement` (e.g. with `ChunkConsolidator` and `UnstructuredAdapter`) actually correct?**
  _`RawElement` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `Manual` (e.g. with `estimate_doc()` and `main()`) actually correct?**
  _`Manual` has 32 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Workflow: graphify`, `graphify`, `graphify en Windows` to the rest of the system?**
  _62 weakly-connected nodes found - possible documentation gaps or missing edges._