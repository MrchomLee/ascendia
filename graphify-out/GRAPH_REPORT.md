# Graph Report - onmy-military-library-contenido  (2026-09-25)

## Corpus Check
- 164 files · ~93,573 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 6, .example 1, .lock 1)

## Summary
- 1531 nodes · 4244 edges · 83 communities (74 shown, 9 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 551 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c83468fb`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_generate_window.py
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
- build_windows
- Manual
- smoke_imports.py
- temario.py
- _seed
- ChunkConsolidator
- ElementKind
- test_baldor_patterns.py
- cache.py
- _bundle
- test_algebra_trigonometria_geometria_analitica.py
- claude_review.py
- checks.py
- test_checks.py
- `explorer/` — revisor visual del pipeline
- run_ref
- windows.py
- _run_immediate
- test_calculo_una_variable.py
- export.py
- etl
- workflows/graphify.md
- CLAUDE.md
- spec.py
- GeminiClient
- etl/pipeline.py
- hierarchy_tree.py
- validation/__init__.py
- batch.py
- DuplicateIndex
- import_reference_questions
- persist_question
- Generación de preguntas por ventanas (qgen v2)
- WindowQuestion
- Niveles cognitivos en la generación de preguntas (qgen v3)
- test_plan_windows.py
- 5_🔍_Search.py
- qgen/claude_code.py
- test_geografia_moderna_mexico.py
- test_temario.py
- test_historia_universal.py
- Question
- gemini/generate.py
- 6_❓_Preguntas.py
- os
- cli/claude_code.py
- get_level_exemplars
- qgen/pipeline.py
- batch_status.py
- importer.py
- test_reference_importer.py
- niveles.py
- _normalize
- QuestionExemplarInput
- test_cost.py
- questions_available

## God Nodes (most connected - your core abstractions)
1. `session_scope()` - 90 edges
2. `init_question_tables()` - 53 edges
3. `Question` - 45 edges
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

## Communities (83 total, 9 thin omitted)

### Community 0 - "test_generate_window.py"
Cohesion: 0.23
Nodes (14): _FakeClient, Exception, Las dos llamadas a Gemini del flujo por ventanas, con un cliente falso., Cliente mínimo: devuelve las respuestas en orden, o falla con `raises`., _response(), test_devuelve_las_preguntas_sin_validar_y_los_tokens(), test_dos_respuestas_ilegibles_dejan_la_ventana_fallida(), test_un_error_de_la_api_no_se_reintenta() (+6 more)

### Community 1 - "test_bundle_spec.py"
Cohesion: 0.11
Nodes (34): copy, _errors(), El contrato del bundle: lo que se acepta y, sobre todo, lo que no. Cada caso de…, test_api_key_en_metadata_bloquea_la_entrega(), test_arbol_sin_raiz(), test_cadena_de_conexion_en_metadata_bloquea_la_entrega(), test_ciclo_en_el_arbol(), mutate() (+26 more)

### Community 2 - "test_pipeline.py"
Cohesion: 0.16
Nodes (45): Las preguntas crudas de una ventana (sin validar) y lo que costó pedirlas., VerificationOutcome, WindowOutcome, Lo que devuelve la verificación de un ejercicio nuevo (spec §7)., VerificationResult, _ejercicio_nuevo(), _estimate(), FakeGemini (+37 more)

### Community 3 - "test_claude_code.py"
Cohesion: 0.24
Nodes (25): _exportar(), _importar(), _item(), _pendientes(), fixture, _questions(), Generación sin API desde Claude Code: exportar ventanas, responder, importar.…, Importar respuestas nunca llama a Gemini: ni cache, ni ventana, ni verificación. (+17 more)

### Community 4 - "Contrato: bundle de contenido v2"
Cohesion: 0.04
Nodes (44): 1. Por qué existe, 2. Forma del fichero, 3. Estructura, 4. Identidad: las claves estables, 5. Las validaciones, 6. Los dos comandos, 7. Versionado del contrato, Aquí — `qgen-export` (+36 more)

### Community 5 - "profile.py"
Cohesion: 0.16
Nodes (25): HeadingCandidate, match_anexo(), match_baldor_capitulo(), match_baldor_caso(), match_baldor_subseccion_romana(), match_baldor_tema_mayusculas(), match_bloque(), match_capitulo() (+17 more)

### Community 6 - "questions_access.py"
Cohesion: 0.10
Nodes (36): datetime, Task 11: Explorador: tipo, cita y motivos, Task 8: Explorador: nivel, filtro e indicadores, _render_question(), get_question_kpis(), level_label(), list_questions(), list_runs() (+28 more)

### Community 7 - "session_scope"
Cohesion: 0.16
Nodes (31): session_scope(), build_bundle(), DuplicateNodeRef, DuplicateRunRef, Any, Session, Dos nodos con el mismo `sort_key`: el bundle no tendría identidad., Dos corridas que colapsan en el mismo `ref`. (+23 more)

### Community 8 - "get_default_rules"
Cohesion: 0.06
Nodes (63): Task 1: Familia y tipos en las reglas, Task 5: Prompt de generación con niveles, 5. Familias y tipos, _resolve_rules(), build_window_instruction(), _conforme(), _ejemplos(), Any (+55 more)

### Community 9 - "types.py"
Cohesion: 0.14
Nodes (16): ABC, ExtractorBase, Path, Common interface for layout extractors. Adapters (Docling, Unstructured, etc.)…, Run the extractor on a PDF and return normalized elements., DoclingAdapter, _first_bbox(), Path (+8 more)

### Community 10 - "toc_parser.py"
Cohesion: 0.07
Nodes (33): detect_toc_pages(), _infer_depth(), _is_roman_only(), _lookback_marker(), _parse_page_number(), parse_toc(), _peek_parte_title(), BaseModel (+25 more)

### Community 11 - "data_access.py"
Cohesion: 0.14
Nodes (27): graphify, _chunk_to_summary(), ChunkSummary, deserialize_extraction(), get_chunks_for_manual(), get_chunks_for_node(), get_extraction_cache(), get_global_kpis() (+19 more)

### Community 12 - "RawElement"
Cohesion: 0.15
Nodes (13): TocResult, One layout element extracted from a PDF page. Both Docling and Unstructured…, RawElement, _Builder, HierarchyAssembler, _label_for_depth(), _peek_next_title(), Assembles a tree from raw elements, optionally guided by a TOC. Parameters… (+5 more)

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
Cohesion: 0.32
Nodes (24): _estado(), _exportar_revision(), _generar(), _importar_revision(), _item(), _lotes(), _marcar(), _nivel() (+16 more)

### Community 19 - "get_profile"
Cohesion: 0.20
Nodes (16): auto_detect_profile(), get_profile(), Heuristic profile pick based on the first few elements' text. Looks for genre-…, _el(), test_autodetect_algebra_baldor(), test_autodetect_codigo_legal(), test_autodetect_falls_back_to_manual_for_empty(), test_autodetect_manual() (+8 more)

### Community 20 - "debug_pymupdf.py"
Cohesion: 0.22
Nodes (6): One-off debug script: inspect characters used as TOC leaders., fitz, pymupdf, rapidocr, sys, unicodedata

### Community 21 - "session.py"
Cohesion: 0.14
Nodes (15): contextlib, Inserta preguntas generadas directamente en el chat para el manual 11 (Álgebra…, Engine, main(), command, Path, init_db(), Create all tables. Idempotent — safe to run on existing DBs. (+7 more)

### Community 22 - "build_windows"
Cohesion: 0.26
Nodes (19): build_windows(), Quita del inicio de `text` lo que repite del final de `prev` (y el salto que lo…, Agrupa los chunks de un nodo en ventanas. Puro y determinista., strip_overlap(), C, _keys(), Ventanas de texto (spec §4): grupos de chunks consecutivos de un nodo., test_chunks_vacios_no_generan_ventanas() (+11 more)

### Community 23 - "Manual"
Cohesion: 0.09
Nodes (38): DeclarativeBase, estimate_doc(), main(), Compute approximate Gemini cost for question generation across ingested…, manuals(), node(), command, List every ingested manual. (+30 more)

### Community 25 - "temario.py"
Cohesion: 0.20
Nodes (11): match_parte_temario(), Parte numerada de un temario ('1.1 Los elementos del proceso comunicativo').…, CapitulosConTemas, _norm(), _numero_de_tema(), Selección por temario: qué bloques, partes, capítulos o temas de un libro…, (número, resto del encabezado) si el encabezado abre un capítulo., Devuelve los elementos (con su índice original) que entran al árbol. - El… (+3 more)

### Community 26 - "_seed"
Cohesion: 0.35
Nodes (11): AppTest, _open_page(), Pestaña "Exportar Bundle" de la página de preguntas, ejecutada con AppTest. La…, _seed(), test_la_cita_se_muestra_tal_cual(), test_la_pregunta_muestra_la_revision_de_claude_con_su_calificacion(), test_la_pregunta_muestra_su_nivel_junto_al_tipo(), test_la_pregunta_muestra_su_tipo_y_sus_motivos() (+3 more)

### Community 27 - "ChunkConsolidator"
Cohesion: 0.17
Nodes (13): ChunkConsolidator, ConsolidatedChunk, BaseModel, Convierte un número romano a entero, o None si no es válido., Reordena fracciones romanas que docling extrajo en orden incorrecto. Docling a…, HierarchyNode, HierarchyTree, BaseModel (+5 more)

### Community 28 - "ElementKind"
Cohesion: 0.14
Nodes (23): docling_core_types_doc, DoclingDocument, elements_from_document(), _first_page(), Normalize a DoclingDocument's items to :class:`RawElement`, in reading order., ElementKind, StrEnum, Manual profile builds PARTE → Capítulo → Sección hierarchy from body. (+15 more)

### Community 29 - "test_baldor_patterns.py"
Cohesion: 0.11
Nodes (17): match_baldor_inciso(), Reconoce subcasos con inciso alfabético (ej. 'a) Factor común monomio.')., Pruebas unitarias para los patrones y jerarquía de Álgebra de Baldor., Verifica subcasos con letras tipo a) o b)., Verifica que el perfil 'algebra_baldor' solo clasifica capítulos a nivel 0 y no…, En Álgebra de Baldor los únicos nodos son los 16 capítulos ('I. Suma' … 'XXXII.…, Verifica que los capítulos con numeración romana se reconocen con su ordinal y…, Verifica las subsecciones con números romanos en mayúsculas. (+9 more)

### Community 30 - "cache.py"
Cohesion: 0.17
Nodes (14): functools, build_or_get_cache(), delete_cache(), DocumentCache, Path, Explicit-cache management for question generation. We cache once per (manual,…, Upload the PDF (Files API) and create an explicit cache. Returns a…, Best-effort cleanup. Used after a run to avoid storage costs. (+6 more)

### Community 31 - "_bundle"
Cohesion: 0.12
Nodes (18): Review Focus, Task 10: Prueba piloto con Geografía (manual 11), Task 7: Contrato v3 del bundle, Task 9: Documentación, grafo y verificación completa, _bundle(), _options(), Un bundle mínimo pero completo y válido., `cost_input_tokens` contiene 'token': el detector no debe morder ahí. (+10 more)

### Community 32 - "test_algebra_trigonometria_geometria_analitica.py"
Cohesion: 0.53
Nodes (5): Perfil `algebra_trigonometria_geometria_analitica`: los cuatro capítulos de la…, test_el_arbol_son_los_cuatro_capitulos_de_la_imagen(), test_la_portada_queda_fuera(), test_secciones_ejemplos_y_teoremas_quedan_en_el_cuerpo_de_su_capitulo(), _tree()

### Community 33 - "claude_review.py"
Cohesion: 0.12
Nodes (29): Task 6: Revisión con Claude: nivel, reclasificación y "solo clasificar", _a_revisar(), _aplicar(), _clasificar(), ExportacionRevision, exportar_revision(), importar_revision(), _lote() (+21 more)

### Community 34 - "checks.py"
Cohesion: 0.17
Nodes (23): difflib, Task 4: Revisiones de cada pregunta, GeneratedOption, GeneratedQuestion, OptionRole, BaseModel, StrEnum, QuestionType (+15 more)

### Community 35 - "test_checks.py"
Cohesion: 0.12
Nodes (32): Global Constraints, Niveles cognitivos en qgen (v3) — Plan de implementación, parse_items(), Valida cada pregunta por separado: una mala no tumba a las demás., Revisión por tipo contra el texto de la ventana (spec §7, tabla de revisiones)., review(), Verdict, _item() (+24 more)

### Community 36 - "`explorer/` — revisor visual del pipeline"
Cohesion: 0.29
Nodes (6): Cómo correr, El árbol y la cobertura, `explorer/` — revisor visual del pipeline, La revisión, Navegación, Vistas

### Community 37 - "run_ref"
Cohesion: 0.29
Nodes (8): 10. Contrato v2 del bundle, iso(), datetime, Clave estable de una corrida: `{model}--{mode}--{inicio compacto UTC}`., Fecha en el formato del contrato: ISO 8601 UTC con `Z`. SQLite devuelve los…, run_ref(), test_fecha_ingenua_se_lee_como_utc(), test_ref_de_corrida_es_estable()

### Community 38 - "windows.py"
Cohesion: 0.15
Nodes (15): Generación de preguntas por ventanas (qgen v2) — Plan de implementación, Global Constraints, Review Focus, Task 12: Verificación final y prueba real, Task 2: Ventanas, Task 3: Esquemas de salida de la llamada por ventana, Task 5: Instrucciones por familia, Task 8: Planificación de ventanas y reanudación (+7 more)

### Community 39 - "_run_immediate"
Cohesion: 0.15
Nodes (20): Task 3: Columnas, guardado y conteo por nivel, actual_cost_usd(), Compute actual cost from observed usage_metadata totals. `cache_create_tokens`…, _Accepted, Procesa las ventanas: con `respuestas` las toma de ahí (sin Gemini, sin cache y…, _run_immediate(), finalize(), obtain() (+12 more)

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
Cohesion: 0.16
Nodes (8): GeminiClient, Thin wrapper around google-genai with explicit context caching. We keep this…, ClassifiedHeading, GeminiHeadingClassifier, HeadingClassificationBatch, BaseModel, Gemini-based fallback classifier for ambiguous headings. Used only when the…, T

### Community 47 - "etl/pipeline.py"
Cohesion: 0.10
Nodes (26): Prueba unitaria del reordenamiento de fracciones romanas., main(), Path, Quick visual inspection of an in-memory hierarchy without persisting., Consolida los elementos del cuerpo de cada nodo hoja en fragmentos con límite…, main(), _print_table(), command (+18 more)

### Community 48 - "hierarchy_tree.py"
Cohesion: 0.43
Nodes (6): _icon_for(), _indent(), Hierarchy tree rendered as nested expanders with optional click-to-navigate., Render the manual's tree. `on_select` is a function that takes a NodeSummary…, _render_node(), render_tree()

### Community 55 - "batch.py"
Cohesion: 0.18
Nodes (14): dataclasses, Task 6: Llamadas a Gemini: ventana y verificación, BatchItemResult, BatchRequest, BatchSubmitResult, _build_inline_request(), parse_batch_results(), Batch-mode generation: submit one job for all nodes, poll, parse later. Trade-… (+6 more)

### Community 56 - "DuplicateIndex"
Cohesion: 0.08
Nodes (24): Task 2: Revisión automática por nivel, 7. Revisión automática por nivel, _copiado(), DuplicateIndex, _literal(), norm_math(), norm_text(), _nucleo() (+16 more)

### Community 57 - "import_reference_questions"
Cohesion: 0.20
Nodes (10): main(), command, Path, Carga un archivo de preguntas de ejemplo y las guarda en la base de datos., Modelo de opción de respuesta para una pregunta de referencia., ReferenceOption, import_reference_questions(), Any (+2 more)

### Community 58 - "persist_question"
Cohesion: 0.23
Nodes (18): seed_questions(), Task 10: Contrato v2 del bundle, Task 7: Columnas nuevas, migración y persistencia, create_run(), load_manual(), persist_question(), Any, Session (+10 more)

### Community 59 - "Generación de preguntas por ventanas (qgen v2)"
Cohesion: 0.15
Nodes (13): 11. Trabajo en la webapp (lo hace el usuario), 13. Errores, 14. Pruebas (TDD), 15. Riesgos, 1. Contexto, 2. Decisiones del usuario, 3. Alcance, 4. Ventanas (+5 more)

### Community 60 - "WindowQuestion"
Cohesion: 0.15
Nodes (21): Task 1: Niveles y esquema de la respuesta, model_validator, Una pregunta completa tal como la devuelve la llamada por ventana., WindowQuestion, _make_options(), Build a list of options matching the canonical 1+1+2 distribution., test_el_esquema_para_gemini_declara_los_cuatro_niveles(), test_empty_question_rejected() (+13 more)

### Community 61 - "Niveles cognitivos en la generación de preguntas (qgen v3)"
Cohesion: 0.12
Nodes (15): 10. Trabajo en la webapp (lo hace el usuario), 11. Explorador y CLI, 12. Organización del código, 13. Pruebas (TDD), 14. Prueba piloto, 15. Riesgos, 1. Contexto, 2. Decisiones del usuario (+7 more)

### Community 62 - "test_plan_windows.py"
Cohesion: 0.39
Nodes (11): _keys(), Qué ventanas procesa una corrida (spec §4): selección, reanudación y --limit., _seed(), test_gana_el_ultimo_estado_de_cada_ventana(), test_las_introducciones_quedan_fuera(), test_limit_cuenta_ventanas(), test_regenerate_ignora_el_historial(), test_se_saltan_las_ventanas_ok_y_se_reintentan_las_fallidas() (+3 more)

### Community 63 - "5_🔍_Search.py"
Cohesion: 0.25
Nodes (9): Full-text search across chunks via SQLite FTS5., init_fts(), BaseModel, query(), Full-text search over chunks using SQLite FTS5. We create a virtual table…, FTS5 has reserved chars; we wrap free-form input as a phrase if needed., Create FTS5 virtual table + triggers if missing, then backfill any chunks that…, _sanitize() (+1 more)

### Community 64 - "qgen/claude_code.py"
Cohesion: 0.21
Nodes (17): carpeta_por_defecto(), clave_de(), Exportacion, exportar(), importar(), _instruccion(), leer_respuesta(), _manual() (+9 more)

### Community 65 - "test_geografia_moderna_mexico.py"
Cohesion: 0.48
Nodes (6): Perfil `geografia_moderna_mexico`: el temario de la imagen, como Capítulo ›…, test_cada_tema_cuelga_de_su_capitulo(), test_el_arbol_es_el_de_la_imagen(), test_lo_que_no_esta_en_la_imagen_queda_fuera(), test_los_subtitulos_y_los_capitulos_completos_quedan_como_texto(), _tree()

### Community 66 - "test_temario.py"
Cohesion: 0.48
Nodes (6): Perfil `taller_lectura_redaccion`: solo el temario pedido, como Bloque › Parte.…, test_cada_parte_cuelga_de_su_bloque(), test_cada_parte_lleva_solo_su_texto(), test_lo_que_no_esta_en_la_imagen_no_queda_en_ningun_nodo(), test_solo_quedan_los_bloques_y_partes_de_la_imagen(), _tree()

### Community 67 - "test_historia_universal.py"
Cohesion: 0.53
Nodes (5): Perfil `historia_universal`: el temario de la imagen, como Capítulo › Tema.…, test_cada_tema_cuelga_del_capitulo(), test_el_arbol_es_el_capitulo_y_sus_cuatro_temas(), test_los_subtitulos_quedan_en_el_cuerpo_de_su_tema(), _tree()

### Community 68 - "Question"
Cohesion: 0.09
Nodes (31): _materia_hint(), _pipeline_commit(), _qgen_version(), Arma el bundle a partir del SQLite del pipeline. Separado del CLI para poder…, Commit del repo de contenido, para poder reproducir una entrega vieja., Comando CLI para importar un banco de preguntas de referencia (ejemplos oro) a…, main(), command (+23 more)

### Community 69 - "gemini/generate.py"
Cohesion: 0.26
Nodes (12): 12. Organización del código, logging, _extract_usage(), generate_window(), _generate_with_retry(), Llamadas a Gemini en modo inmediato: una por ventana y la verificación de…, Resuelve un ejercicio nuevo a ciegas y compara su dificultad con la del libro…, Pull token counts from a google-genai response. Names vary by SDK version. (+4 more)

### Community 70 - "6_❓_Preguntas.py"
Cohesion: 0.13
Nodes (25): dotenv, kpi_row(), Render a row of `st.metric` cards. items is a list of (label, value,…, cache_data, Render a single PDF page to PNG bytes via PyMuPDF., Return PNG bytes of the given page (1-based), or None if unavailable. Cached so…, Convenience: render and display in one call., render_page() (+17 more)

### Community 71 - "os"
Cohesion: 0.29
Nodes (4): google, os, requests, urllib_request

### Community 72 - "cli/claude_code.py"
Cohesion: 0.29
Nodes (9): exportar_cmd(), importar_cmd(), importar_revision_cmd(), command, Path, `qgen-claude`: generar preguntas desde Claude Code, sin API (ver…, Escribe la instrucción y las ventanas pendientes para que Claude Code las…, Revisa y guarda las respuestas de las ventanas pendientes, como una corrida más. (+1 more)

### Community 73 - "get_level_exemplars"
Cohesion: 0.30
Nodes (11): Task 4: Ejemplos por nivel (importador xlsx y repositorio), Modelo de base de datos para una pregunta de referencia u oro., ReferenceQuestion, _as_dict(), get_level_exemplars(), get_reference_exemplars(), Any, Session (+3 more)

### Community 74 - "qgen/pipeline.py"
Cohesion: 0.09
Nodes (41): collections, concurrent_futures, Task 9: Corrida por ventanas, estimación y CLI (retira el flujo viejo), main(), _model_option(), _print_estimate(), _print_niveles(), _print_summary() (+33 more)

### Community 75 - "batch_status.py"
Cohesion: 0.38
Nodes (11): _check_once(), main(), _print_run_card(), _print_running(), command, CLI for monitoring + finalizing batch runs. Usage patterns -------------- 1)…, _state_name(), _wait_loop() (+3 more)

### Community 76 - "importer.py"
Cohesion: 0.22
Nodes (10): csv, limpiar_ejemplo(), _load_xlsx(), Path, Importador de preguntas de referencia (banco de ejemplos/exemplars). Lee…, Quita las marcas `[cite: …]` y las referencias al texto ("Según el texto, …"):…, Una hoja por nivel (el nombre de la hoja es el nivel); encabezado con…, _sin_acentos() (+2 more)

### Community 77 - "test_reference_importer.py"
Cohesion: 0.27
Nodes (10): openpyxl, qgen_reference_importer, qgen_reference_repository, load_reference_file(), Carga datos de preguntas desde un archivo JSON, JSONL o CSV., Pruebas unitarias para la importación y consulta de preguntas de referencia…, test_el_xlsx_da_un_ejemplo_por_fila_con_el_nivel_de_su_hoja(), test_una_fila_con_menos_de_cuatro_respuestas_se_rechaza_con_hoja_y_fila() (+2 more)

### Community 78 - "niveles.py"
Cohesion: 0.20
Nodes (6): collections_abc, enum, Niveles cognitivos de las preguntas (spec de niveles, §4). Las definiciones son…, Niveles cognitivos: valores, proporción y definiciones compartidas., test_la_proporcion_es_55_15_15_15(), test_una_ventana_con_3_de_conocimiento_debe_traer_los_otros_niveles()

### Community 79 - "_normalize"
Cohesion: 0.67
Nodes (3): _normalize(), Loose match: strip accents, lowercase, collapse whitespace., Título comparable: sin acentos, sin puntuación y en minúsculas. El TOC y los…

### Community 80 - "QuestionExemplarInput"
Cohesion: 0.29
Nodes (6): field_validator, OptionExemplarInput, BaseModel, QuestionExemplarInput, Modelo Pydantic para validar una opción de respuesta de ejemplo., Modelo Pydantic para validar una pregunta de ejemplo completa.

### Community 81 - "test_cost.py"
Cohesion: 0.53
Nodes (5): _estimate(), Estimación de costo por ventanas (spec §9)., test_cuenta_preguntas_y_verificaciones_por_caracteres(), test_sin_ejercicios_no_hay_verificaciones(), test_sin_ventanas_no_cuesta_nada()

### Community 82 - "questions_available"
Cohesion: 0.50
Nodes (4): questions_available(), ¿Existen ya las tablas de la fase 2 en esta base? Un SQLite recién ingerido…, Verifica que detecta correctamente si las tablas de preguntas existen., test_questions_available()

## Knowledge Gaps
- **62 isolated node(s):** `Workflow: graphify`, `graphify`, `graphify en Windows`, `1. Por qué existe`, `2. Forma del fichero` (+57 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 479 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `session_scope()` connect `session_scope` to `test_pipeline.py`, `test_claude_code.py`, `questions_access.py`, `data_access.py`, `test_claude_review.py`, `session.py`, `Manual`, `_seed`, `ChunkConsolidator`, `claude_review.py`, `export.py`, `etl/pipeline.py`, `import_reference_questions`, `persist_question`, `test_plan_windows.py`, `5_🔍_Search.py`, `Question`, `6_❓_Preguntas.py`, `cli/claude_code.py`, `qgen/pipeline.py`, `batch_status.py`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Why does `RawElement` connect `RawElement` to `test_algebra_trigonometria_geometria_analitica.py`, `test_geografia_moderna_mexico.py`, `test_temario.py`, `test_historia_universal.py`, `profile.py`, `test_calculo_una_variable.py`, `types.py`, `etl/pipeline.py`, `get_profile`, `temario.py`, `ChunkConsolidator`, `ElementKind`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `init_question_tables()` (e.g. with `seed_questions()` and `Task 7: Columnas nuevas, migración y persistencia`) actually correct?**
  _`init_question_tables()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 35 inferred relationships involving `Question` (e.g. with `Task 7: Columnas nuevas, migración y persistencia` and `Task 3: Columnas, guardado y conteo por nivel`) actually correct?**
  _`Question` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `RawElement` (e.g. with `ChunkConsolidator` and `UnstructuredAdapter`) actually correct?**
  _`RawElement` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `Manual` (e.g. with `estimate_doc()` and `main()`) actually correct?**
  _`Manual` has 32 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Workflow: graphify`, `graphify`, `graphify en Windows` to the rest of the system?**
  _62 weakly-connected nodes found - possible documentation gaps or missing edges._