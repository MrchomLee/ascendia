# Graph Report - wt-escaneo  (2026-11-23)

## Corpus Check
- 182 files · ~115,353 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 7, .example 1, .lock 1)

## Summary
- 1917 nodes · 5346 edges · 109 communities (95 shown, 14 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 609 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `981281fd`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- batch_status.py
- test_bundle_spec.py
- test_pipeline.py
- test_claude_code.py
- Contrato: bundle de contenido v2
- profile.py
- 6_❓_Preguntas.py
- session_scope
- DocumentRules
- types.py
- toc_parser.py
- data_access.py
- RawElement
- test_patterns.py
- main
- BaldorExerciseExtractor
- claude_correccion.py
- json
- test_claude_review.py
- get_profile
- debug_pymupdf.py
- get_default_rules
- qgen/claude_code.py
- Manual
- smoke_imports.py
- test_escaneo.py
- session.py
- consolidator.py
- ElementKind
- test_baldor_patterns.py
- batch.py
- _bundle
- test_algebra_trigonometria_geometria_analitica.py
- claude_review.py
- checks.py
- test_checks.py
- `explorer/` — revisor visual del pipeline
- run_ref
- Question
- dudas.py
- test_calculo_una_variable.py
- build_windows
- etl
- workflows/graphify.md
- CLAUDE.md
- spec.py
- GeminiClient
- etl/pipeline.py
- Window
- validation/__init__.py
- ocr.py
- norm_text
- import_reference_questions
- persist_question
- Generación de preguntas por ventanas (qgen v2)
- WindowQuestion
- Niveles cognitivos en la generación de preguntas (qgen v3)
- test_plan_windows.py
- bundle_min
- get_tree
- test_geografia_moderna_mexico.py
- test_temario.py
- test_historia_universal.py
- cli/claude_code.py
- Review Focus
- 1_📄_Manual.py
- os
- importer.py
- get_level_exemplars
- qgen/pipeline.py
- _seed
- 5_🔍_Search.py
- test_reference_importer.py
- test_niveles.py
- _normalize
- QuestionExemplarInput
- cli/generate.py
- test_rules.py
- escanear.py
- gemini/generate.py
- bancos.py
- maquetacion.py
- test_generate_window.py
- escribir_indice
- _toca
- test_bancos_juego.py
- Carpeta
- borrador.py
- families.py
- _preguntas_del_mundo
- Ruta al Ascenso — generación de contenido
- 3. Trabajar un manual, de principio a fin
- `etl/` — Fase 1: extracción estructurada de manuales PDF
- `question_generator/` — Fase 2: generación de preguntas con Gemini
- DuplicateNodeRef
- parse_items
- 3.5 Generar el manual completo
- mundo_id
- escaneo/__init__.py
- _compose_title
- juego/__init__.py
- urllib_request

## God Nodes (most connected - your core abstractions)
1. `session_scope()` - 106 edges
2. `init_question_tables()` - 63 edges
3. `Question` - 62 edges
4. `get_default_rules()` - 44 edges
5. `Manual` - 42 edges
6. `RawElement` - 41 edges
7. `build_bundle()` - 41 edges
8. `Carpeta` - 37 edges
9. `_run_immediate()` - 37 edges
10. `review()` - 35 edges

## Surprising Connections (you probably didn't know these)
- `4. Identidad: las claves estables` --references--> `manuals()`  [INFERRED]
  CONTRATO-BUNDLE.md → etl/src/etl/cli/inspect_cli.py
- `Notas por bloque` --references--> `manuals()`  [INFERRED]
  CONTRATO-BUNDLE.md → etl/src/etl/cli/inspect_cli.py
- `1.2 Trabajar con Claude Code` --references--> `importar()`  [INFERRED]
  README.md → question_generator/src/qgen/claude_code.py
- `Task 10: Prueba piloto con Geografía (manual 11)` --references--> `plan_windows()`  [INFERRED]
  docs/superpowers/plans/2026-09-25-qgen-niveles-cognitivos.md → question_generator/src/qgen/pipeline.py
- `Task 3: Esquemas de salida de la llamada por ventana` --references--> `QuestionType`  [INFERRED]
  docs/superpowers/plans/2026-09-23-qgen-ventanas.md → question_generator/src/qgen/prompts/schemas.py

## Import Cycles
- None detected.

## Communities (109 total, 14 thin omitted)

### Community 0 - "batch_status.py"
Cohesion: 0.38
Nodes (11): _check_once(), main(), _print_run_card(), _print_running(), command, CLI for monitoring + finalizing batch runs. Usage patterns -------------- 1)…, _state_name(), _wait_loop() (+3 more)

### Community 1 - "test_bundle_spec.py"
Cohesion: 0.10
Nodes (39): copy, _errors(), _options(), El contrato del bundle: lo que se acepta y, sobre todo, lo que no. Cada caso de…, test_api_key_en_metadata_bloquea_la_entrega(), test_arbol_sin_raiz(), test_cadena_de_conexion_en_metadata_bloquea_la_entrega(), test_ciclo_en_el_arbol() (+31 more)

### Community 2 - "test_pipeline.py"
Cohesion: 0.20
Nodes (37): Las preguntas crudas de una ventana (sin validar) y lo que costó pedirlas., WindowOutcome, _ejercicio_nuevo(), _estimate(), FakeGemini, _item(), _questions(), Orquestación de `qgen-generate` por ventanas (spec §4–§8), con Gemini simulado.… (+29 more)

### Community 3 - "test_claude_code.py"
Cohesion: 0.22
Nodes (29): nombre_de(), La clave `nodo:desde-hasta` como nombre de archivo (Windows no admite `:`)., _exportar(), _importar(), _item(), _pendientes(), fixture, _questions() (+21 more)

### Community 4 - "Contrato: bundle de contenido v2"
Cohesion: 0.14
Nodes (14): 1. Por qué existe, 2. Forma del fichero, 3. Estructura, 4. Identidad: las claves estables, 5. Las validaciones, 6. Los dos comandos, 7. Versionado del contrato, Aquí — `qgen-export` (+6 more)

### Community 5 - "profile.py"
Cohesion: 0.08
Nodes (43): dataclasses, La carpeta de trabajo de un escaneo y los nombres de sus archivos., HeadingCandidate, HeadingMatch, match_anexo(), match_baldor_capitulo(), match_baldor_caso(), match_baldor_inciso() (+35 more)

### Community 6 - "6_❓_Preguntas.py"
Cohesion: 0.12
Nodes (30): Task 11: Explorador: tipo, cita y motivos, Task 8: Explorador: nivel, filtro e indicadores, Preguntas generadas — revisión visual, cobertura y corridas. Es la vista de la…, _render_question(), get_question_kpis(), level_label(), list_questions(), list_runs() (+22 more)

### Community 7 - "session_scope"
Cohesion: 0.20
Nodes (33): session_scope(), build_bundle(), Any, Session, Construye el bundle v2 de un manual. `run_ids` limita a esas corridas (y a sus…, init_question_tables(), _con_paginas(), parametrize (+25 more)

### Community 8 - "DocumentRules"
Cohesion: 0.17
Nodes (18): Task 1: Familia y tipos en las reglas, 5. Familias y tipos, _resolve_rules(), DocumentRules, merge_rules(), Any, Per-archetype question-generation rules + per-document override mechanism. The…, Knobs that shape question generation for a class of documents. (+10 more)

### Community 9 - "types.py"
Cohesion: 0.10
Nodes (26): ABC, docling_core_types_doc, ExtractorBase, Path, Common interface for layout extractors. Adapters (Docling, Unstructured, etc.)…, Run the extractor on a PDF and return normalized elements., DoclingAdapter, elements_from_document() (+18 more)

### Community 10 - "toc_parser.py"
Cohesion: 0.07
Nodes (34): detect_toc_pages(), _infer_depth(), _is_roman_only(), _lookback_marker(), _parse_page_number(), parse_toc(), _peek_parte_title(), BaseModel (+26 more)

### Community 11 - "data_access.py"
Cohesion: 0.16
Nodes (20): graphify, _chunk_to_summary(), ChunkSummary, deserialize_extraction(), get_chunks_for_manual(), get_chunks_for_node(), get_extraction_cache(), get_global_kpis() (+12 more)

### Community 12 - "RawElement"
Cohesion: 0.15
Nodes (11): One layout element extracted from a PDF page. Both Docling and Unstructured…, RawElement, _Builder, HierarchyAssembler, _peek_next_title(), Assembles a tree from raw elements, optionally guided by a TOC. Parameters…, Look ahead up to 3 elements for something that acts as the heading title., DocumentProfile (+3 more)

### Community 13 - "test_patterns.py"
Cohesion: 0.10
Nodes (31): classify_heading(), match_articulo(), match_titulo(), Compatibility shim: classify using the default 'manual' profile. New code…, Default classify_heading uses 'manual' profile — articles are not its concern…, test_anexo(), test_articulo_quater(), test_articulo_septimus() (+23 more)

### Community 14 - "main"
Cohesion: 0.13
Nodes (24): date, SHA-256 del PDF de origen, si sigue estando donde dice el manual., source_digest(), bundle_filename(), next_version(), Path, Siguiente `v{n}` libre para este manual en `out_dir`. Se cuenta por manual y no…, Escribe el bundle (comprimiendo si es grande) y su `.sha256`. Devuelve `(ruta… (+16 more)

### Community 15 - "BaldorExerciseExtractor"
Cohesion: 0.11
Nodes (18): BaldorExercise, BaldorExerciseExtractor, flush_current(), Extractor de ejercicios resueltos y problemas prácticos de Álgebra de Baldor., Genera el texto estructurado del ejercicio para el prompt de generación de…, Analizador para extraer problemas numerados, procedimientos y soluciones., Extrae la lista de ejercicios presentes en un bloque de texto., Parsea el bloque de texto de un ejercicio individual extrayendo enunciado,… (+10 more)

### Community 16 - "claude_correccion.py"
Cohesion: 0.10
Nodes (32): _manual(), _a_corregir(), aplicar_decision(), _avisos(), cargar_ejemplos(), Decision, _ejemplo(), ExportacionCorreccion (+24 more)

### Community 17 - "json"
Cohesion: 0.13
Nodes (4): Inspect a cached docling extraction to find LIBRO/TITULO lines and Latin-suffix…, json, pickle, sqlite3

### Community 18 - "test_claude_review.py"
Cohesion: 0.20
Nodes (39): _escribir(), _exportar(), _importar(), _pregunta(), Corrección de preguntas desde Claude Code con las observaciones del usuario. Se…, test_corregir_cambia_el_texto_y_guarda_la_version_original(), test_exportar_deja_reglas_ejemplos_y_un_lote_por_ventana(), test_los_comandos_exportan_e_importan() (+31 more)

### Community 19 - "get_profile"
Cohesion: 0.20
Nodes (16): auto_detect_profile(), get_profile(), Heuristic profile pick based on the first few elements' text. Looks for genre-…, _el(), test_autodetect_algebra_baldor(), test_autodetect_codigo_legal(), test_autodetect_falls_back_to_manual_for_empty(), test_autodetect_manual() (+8 more)

### Community 20 - "debug_pymupdf.py"
Cohesion: 0.15
Nodes (10): collections, One-off debug script: inspect characters used as TOC leaders., main(), Path, Quick visual inspection of an in-memory hierarchy without persisting., fitz, pymupdf, rapidocr (+2 more)

### Community 21 - "get_default_rules"
Cohesion: 0.16
Nodes (27): Task 5: Prompt de generación con niveles, build_window_instruction(), _ejemplos(), Any, Instrucción del sistema para la llamada por ventana: plantilla de la familia +…, Ejemplos de referencia; si no hay, los militares de siempre solo en la familia…, get_default_rules(), La instrucción por ventana lleva las reglas de Baldor y pide ejercicios. (+19 more)

### Community 22 - "qgen/claude_code.py"
Cohesion: 0.15
Nodes (22): clave_de(), Exportacion, exportar(), importar(), _instruccion(), leer_respuesta(), Path, Session (+14 more)

### Community 23 - "Manual"
Cohesion: 0.11
Nodes (29): DeclarativeBase, estimate_doc(), main(), Compute approximate Gemini cost for question generation across ingested…, manuals(), node(), command, List every ingested manual. (+21 more)

### Community 25 - "test_escaneo.py"
Cohesion: 0.09
Nodes (31): leer_rango(), nombre_pagina(), Página del PDF (1 = la primera, como la cuenta el visor) → «p0012»., «3-10,15» → [3, …, 10, 15] (páginas del PDF, desde 1). Sin rango, todas., extraer_paginas(), imagen_de_pagina(), Image, Path (+23 more)

### Community 26 - "session.py"
Cohesion: 0.08
Nodes (33): contextlib, Inserta preguntas generadas directamente en el chat para el manual 11 (Álgebra…, datetime, Engine, init_db(), Create all tables. Idempotent — safe to run on existing DBs., _default_db_url(), get_engine() (+25 more)

### Community 27 - "consolidator.py"
Cohesion: 0.15
Nodes (15): Prueba unitaria del reordenamiento de fracciones romanas., ChunkConsolidator, ConsolidatedChunk, BaseModel, Consolida los elementos del cuerpo de cada nodo hoja en fragmentos con límite…, Convierte un número romano a entero, o None si no es válido., Reordena fracciones romanas que docling extrajo en orden incorrecto. Docling a…, HierarchyNode (+7 more)

### Community 28 - "ElementKind"
Cohesion: 0.17
Nodes (19): ElementKind, StrEnum, Manual profile builds PARTE → Capítulo → Sección hierarchy from body., Legal-code profile builds Libro → Título → Capítulo → Artículo., Drop filters silence Cámara/DOF noise without losing real content., Reform annotations get attached as metadata on the relevant node., _t(), test_assemble_codigo_legal_basic() (+11 more)

### Community 29 - "test_baldor_patterns.py"
Cohesion: 0.12
Nodes (15): Pruebas unitarias para los patrones y jerarquía de Álgebra de Baldor., Verifica subcasos con letras tipo a) o b)., Verifica que el perfil 'algebra_baldor' solo clasifica capítulos a nivel 0 y no…, En Álgebra de Baldor los únicos nodos son los 16 capítulos ('I. Suma' … 'XXXII.…, Verifica que los capítulos con numeración romana se reconocen con su ordinal y…, Verifica las subsecciones con números romanos en mayúsculas., Verifica el reconocimiento de los casos clásicos de factorización., Verifica encabezados conceptuales y reglas generales en mayúsculas sostenidas. (+7 more)

### Community 30 - "batch.py"
Cohesion: 0.11
Nodes (27): functools, BatchItemResult, BatchRequest, BatchSubmitResult, _build_inline_request(), parse_batch_results(), Batch-mode generation: submit one job for all nodes, poll, parse later. Trade-…, Yield BatchItemResult entries. Prefers matching by… (+19 more)

### Community 31 - "_bundle"
Cohesion: 0.22
Nodes (9): _bundle(), Un bundle mínimo pero completo y válido., `cost_input_tokens` contiene 'token': el detector no debe morder ahí., test_bundle_valido_pasa_sin_errores(), test_corrida_con_nodos_fallidos_avisa(), test_los_contadores_de_tokens_no_son_un_secreto(), test_nodo_con_texto_sin_pregunta_avisa_pero_no_bloquea(), test_preguntas_rechazadas_avisan() (+1 more)

### Community 32 - "test_algebra_trigonometria_geometria_analitica.py"
Cohesion: 0.53
Nodes (5): Perfil `algebra_trigonometria_geometria_analitica`: los cuatro capítulos de la…, test_el_arbol_son_los_cuatro_capitulos_de_la_imagen(), test_la_portada_queda_fuera(), test_secciones_ejemplos_y_teoremas_quedan_en_el_cuerpo_de_su_capitulo(), _tree()

### Community 33 - "claude_review.py"
Cohesion: 0.12
Nodes (30): Task 6: Revisión con Claude: nivel, reclasificación y "solo clasificar", carpeta_por_defecto(), _a_revisar(), _aplicar(), _clasificar(), ExportacionRevision, exportar_revision(), importar_revision() (+22 more)

### Community 34 - "checks.py"
Cohesion: 0.13
Nodes (30): collections_abc, difflib, Task 4: Revisiones de cada pregunta, enum, pydantic, Niveles cognitivos de las preguntas (spec de niveles, §4). Las definiciones son…, GeneratedOption, GeneratedQuestion (+22 more)

### Community 35 - "test_checks.py"
Cohesion: 0.12
Nodes (31): DuplicateIndex, Enunciados ya aceptados, por nodo, para descartar duplicadas (spec §7). En…, Revisión por tipo contra el texto de la ventana (spec §7, tabla de revisiones)., review(), Verdict, _nivel(), _q(), Revisiones de cada pregunta de una ventana (spec §7). (+23 more)

### Community 36 - "`explorer/` — revisor visual del pipeline"
Cohesion: 0.29
Nodes (6): Cómo correr, El árbol y la cobertura, `explorer/` — revisor visual del pipeline, La revisión, Navegación, Vistas

### Community 37 - "run_ref"
Cohesion: 0.29
Nodes (8): 10. Contrato v2 del bundle, iso(), datetime, Clave estable de una corrida: `{model}--{mode}--{inicio compacto UTC}`., Fecha en el formato del contrato: ISO 8601 UTC con `Z`. SQLite devuelve los…, run_ref(), test_fecha_ingenua_se_lee_como_utc(), test_ref_de_corrida_es_estable()

### Community 38 - "Question"
Cohesion: 0.08
Nodes (37): Task 7: Columnas nuevas, migración y persistencia, _catalog_hint(), _cita_con_referencia(), _materia_hint(), _pipeline_commit(), _qgen_version(), Arma el bundle a partir del SQLite del pipeline. Separado del CLI para poder…, La cita con el libro y la página impresa: «… (Baldor, Álgebra, p. 44)». Solo si… (+29 more)

### Community 39 - "dudas.py"
Cohesion: 0.12
Nodes (26): diccionario(), dudosas_de_pagina(), en_diccionario(), hoja_para_ver(), listar_dudas(), normal(), paginas_del_borrador(), Any (+18 more)

### Community 40 - "test_calculo_una_variable.py"
Cohesion: 0.53
Nodes (5): Perfil `calculo_una_variable`: los tres capítulos completos de la imagen.…, test_el_arbol_son_los_tres_capitulos_de_la_imagen(), test_la_portada_queda_fuera(), test_secciones_y_subtitulos_quedan_en_el_cuerpo_de_su_capitulo(), _tree()

### Community 41 - "build_windows"
Cohesion: 0.26
Nodes (19): build_windows(), Quita del inicio de `text` lo que repite del final de `prev` (y el salto que lo…, Agrupa los chunks de un nodo en ventanas. Puro y determinista., strip_overlap(), C, _keys(), Ventanas de texto (spec §4): grupos de chunks consecutivos de un nodo., test_chunks_vacios_no_generan_ventanas() (+11 more)

### Community 42 - "etl"
Cohesion: 1.00
Nodes (3): etl, explorer, question_generator

### Community 44 - "CLAUDE.md"
Cohesion: 0.40
Nodes (4): El proyecto, graphify en Windows, graphify (opcional), Reglas para Claude en este repo

### Community 45 - "spec.py"
Cohesion: 0.18
Nodes (20): gzip, Bundle de contenido: la interfaz entre la generación de preguntas y la webapp., _bool(), _dict(), dumps(), find_secrets(), walk(), _int() (+12 more)

### Community 46 - "GeminiClient"
Cohesion: 0.16
Nodes (8): GeminiClient, Thin wrapper around google-genai with explicit context caching. We keep this…, ClassifiedHeading, GeminiHeadingClassifier, HeadingClassificationBatch, BaseModel, Gemini-based fallback classifier for ambiguous headings. Used only when the…, T

### Community 47 - "etl/pipeline.py"
Cohesion: 0.11
Nodes (24): main(), _print_table(), command, Path, Run both extractors with persistence disabled and emit a comparison., _render_markdown(), main(), command (+16 more)

### Community 48 - "Window"
Cohesion: 0.14
Nodes (16): Generación de preguntas por ventanas (qgen v2) — Plan de implementación, Global Constraints, Review Focus, Task 10: Contrato v2 del bundle, Task 12: Verificación final y prueba real, Task 2: Ventanas, Task 3: Esquemas de salida de la llamada por ventana, Task 5: Instrucciones por familia (+8 more)

### Community 55 - "ocr.py"
Cohesion: 0.11
Nodes (23): PaddleOCRVL, planear_recortes(), Image, Pasos 3 y 4: leer las regiones con PaddleOCR-VL-1.5 (GPU) y la página entera…, PaddleOCR-VL-1.5 por lotes, en bfloat16 sobre CUDA y con la caché de atención…, Índice {página: {región: [claves]}} y los recortes que todavía no están en la…, clave(), _fraccion_encimada() (+15 more)

### Community 56 - "norm_text"
Cohesion: 0.10
Nodes (20): Task 2: Revisión automática por nivel, 7. Revisión automática por nivel, _copiado(), _literal(), _literal_salvo_arranque(), norm_math(), norm_text(), _nucleo() (+12 more)

### Community 57 - "import_reference_questions"
Cohesion: 0.20
Nodes (10): main(), command, Path, Carga un archivo de preguntas de ejemplo y las guarda en la base de datos., Modelo de opción de respuesta para una pregunta de referencia., ReferenceOption, import_reference_questions(), Any (+2 more)

### Community 58 - "persist_question"
Cohesion: 0.30
Nodes (15): seed_questions(), create_run(), finalize_run(), load_manual(), persist_question(), Any, Session, _make_question() (+7 more)

### Community 59 - "Generación de preguntas por ventanas (qgen v2)"
Cohesion: 0.16
Nodes (12): 11. Trabajo en la webapp (lo hace el usuario), 13. Errores, 14. Pruebas (TDD), 15. Riesgos, 1. Contexto, 2. Decisiones del usuario, 3. Alcance, 4. Ventanas (+4 more)

### Community 60 - "WindowQuestion"
Cohesion: 0.20
Nodes (15): Task 1: Niveles y esquema de la respuesta, model_validator, Una pregunta completa tal como la devuelve la llamada por ventana., WindowQuestion, test_el_esquema_para_gemini_declara_los_cuatro_niveles(), test_la_pregunta_de_ventana_exige_un_nivel_conocido(), test_la_respuesta_de_ventana_es_una_lista_de_preguntas(), test_un_ejercicio_siempre_es_de_aplicacion() (+7 more)

### Community 61 - "Niveles cognitivos en la generación de preguntas (qgen v3)"
Cohesion: 0.12
Nodes (15): 10. Trabajo en la webapp (lo hace el usuario), 11. Explorador y CLI, 12. Organización del código, 13. Pruebas (TDD), 14. Prueba piloto, 15. Riesgos, 1. Contexto, 2. Decisiones del usuario (+7 more)

### Community 62 - "test_plan_windows.py"
Cohesion: 0.35
Nodes (13): _keys(), Qué ventanas procesa una corrida (spec §4): selección, reanudación y --limit., _seed(), test_con_rutas_solo_entran_los_nodos_del_alcance(), test_gana_el_ultimo_estado_de_cada_ventana(), test_las_introducciones_quedan_fuera(), test_limit_cuenta_ventanas(), test_regenerate_ignora_el_historial() (+5 more)

### Community 63 - "bundle_min"
Cohesion: 0.14
Nodes (25): 6. La llamada por ventana, banco_de_escuela(), convertir_pregunta(), «Capítulo · Tema»: el título del nodo de primer nivel y luego el del nodo. Un…, La pregunta en el formato del banco del juego; solo para las que no se…, El banco del juego de una escuela y su resumen, como `(banco, resumen)`. Cada…, tema_de(), bundle_alg() (+17 more)

### Community 64 - "get_tree"
Cohesion: 0.27
Nodes (12): _icon_for(), _indent(), Hierarchy tree rendered as nested expanders with optional click-to-navigate., Render the manual's tree. `on_select` is a function that takes a NodeSummary…, _render_node(), render_tree(), get_node_ancestors(), get_node_children() (+4 more)

### Community 65 - "test_geografia_moderna_mexico.py"
Cohesion: 0.48
Nodes (6): Perfil `geografia_moderna_mexico`: el temario de la imagen, como Capítulo ›…, test_cada_tema_cuelga_de_su_capitulo(), test_el_arbol_es_el_de_la_imagen(), test_lo_que_no_esta_en_la_imagen_queda_fuera(), test_los_subtitulos_y_los_capitulos_completos_quedan_como_texto(), _tree()

### Community 66 - "test_temario.py"
Cohesion: 0.48
Nodes (6): Perfil `taller_lectura_redaccion`: solo el temario pedido, como Bloque › Parte.…, test_cada_parte_cuelga_de_su_bloque(), test_cada_parte_lleva_solo_su_texto(), test_lo_que_no_esta_en_la_imagen_no_queda_en_ningun_nodo(), test_solo_quedan_los_bloques_y_partes_de_la_imagen(), _tree()

### Community 67 - "test_historia_universal.py"
Cohesion: 0.53
Nodes (5): Perfil `historia_universal`: el temario de la imagen, como Capítulo › Tema.…, test_cada_tema_cuelga_del_capitulo(), test_el_arbol_es_el_capitulo_y_sus_cuatro_temas(), test_los_subtitulos_quedan_en_el_cuerpo_de_su_tema(), _tree()

### Community 68 - "cli/claude_code.py"
Cohesion: 0.23
Nodes (13): exportar_cmd(), exportar_correccion_cmd(), exportar_revision_cmd(), importar_correccion_cmd(), importar_revision_cmd(), command, Path, `qgen-claude`: generar preguntas desde Claude Code, sin API (ver… (+5 more)

### Community 69 - "Review Focus"
Cohesion: 0.29
Nodes (6): Global Constraints, Niveles cognitivos en qgen (v3) — Plan de implementación, Review Focus, Task 10: Prueba piloto con Geografía (manual 11), Task 7: Contrato v3 del bundle, Task 9: Documentación, grafo y verificación completa

### Community 70 - "1_📄_Manual.py"
Cohesion: 0.14
Nodes (23): dotenv, kpi_row(), Render a row of `st.metric` cards. items is a list of (label, value,…, cache_data, Render a single PDF page to PNG bytes via PyMuPDF., Return PNG bytes of the given page (1-based), or None if unavailable. Cached so…, Convenience: render and display in one call., render_page() (+15 more)

### Community 71 - "os"
Cohesion: 0.40
Nodes (3): google, os, requests

### Community 72 - "importer.py"
Cohesion: 0.22
Nodes (10): csv, limpiar_ejemplo(), _load_xlsx(), Path, Importador de preguntas de referencia (banco de ejemplos/exemplars). Lee…, Quita las marcas `[cite: …]` y las referencias al texto ("Según el texto, …"):…, Una hoja por nivel (el nombre de la hoja es el nivel); encabezado con…, _sin_acentos() (+2 more)

### Community 73 - "get_level_exemplars"
Cohesion: 0.30
Nodes (11): Task 4: Ejemplos por nivel (importador xlsx y repositorio), Modelo de base de datos para una pregunta de referencia u oro., ReferenceQuestion, _as_dict(), get_level_exemplars(), get_reference_exemplars(), Any, Session (+3 more)

### Community 74 - "qgen/pipeline.py"
Cohesion: 0.09
Nodes (37): concurrent_futures, Task 3: Columnas, guardado y conteo por nivel, actual_cost_usd(), Compute actual cost from observed usage_metadata totals. `cache_create_tokens`…, _add_missing_columns(), _Accepted, _create_run(), Orquestación de principio a fin (spec §4–§8). nodos → ventanas pendientes → una… (+29 more)

### Community 75 - "_seed"
Cohesion: 0.35
Nodes (11): AppTest, _open_page(), Pestaña "Exportar Bundle" de la página de preguntas, ejecutada con AppTest. La…, _seed(), test_la_cita_se_muestra_tal_cual(), test_la_pregunta_muestra_la_revision_de_claude_con_su_calificacion(), test_la_pregunta_muestra_su_nivel_junto_al_tipo(), test_la_pregunta_muestra_su_tipo_y_sus_motivos() (+3 more)

### Community 76 - "5_🔍_Search.py"
Cohesion: 0.25
Nodes (9): Full-text search across chunks via SQLite FTS5., init_fts(), BaseModel, query(), Full-text search over chunks using SQLite FTS5. We create a virtual table…, FTS5 has reserved chars; we wrap free-form input as a phrase if needed., Create FTS5 virtual table + triggers if missing, then backfill any chunks that…, _sanitize() (+1 more)

### Community 77 - "test_reference_importer.py"
Cohesion: 0.23
Nodes (12): openpyxl, qgen_reference_importer, qgen_reference_repository, load_reference_file(), Carga datos de preguntas desde un archivo JSON, JSONL o CSV., Pruebas unitarias para la importación y consulta de preguntas de referencia…, Verifica la carga e importación de preguntas desde un archivo JSON., test_el_xlsx_da_un_ejemplo_por_fila_con_el_nivel_de_su_hoja() (+4 more)

### Community 78 - "test_niveles.py"
Cohesion: 0.33
Nodes (3): Niveles cognitivos: valores, proporción y definiciones compartidas., test_la_proporcion_es_55_15_15_15(), test_una_ventana_con_3_de_conocimiento_debe_traer_los_otros_niveles()

### Community 79 - "_normalize"
Cohesion: 0.67
Nodes (3): _normalize(), Loose match: strip accents, lowercase, collapse whitespace., Título comparable: sin acentos, sin puntuación y en minúsculas. El TOC y los…

### Community 80 - "QuestionExemplarInput"
Cohesion: 0.29
Nodes (6): field_validator, OptionExemplarInput, BaseModel, QuestionExemplarInput, Modelo Pydantic para validar una opción de respuesta de ejemplo., Modelo Pydantic para validar una pregunta de ejemplo completa.

### Community 81 - "cli/generate.py"
Cohesion: 0.12
Nodes (24): Task 9: Corrida por ventanas, estimación y CLI (retira el flujo viejo), importar_cmd(), Revisa y guarda las respuestas de las ventanas pendientes, como una corrida más., main(), _model_option(), _print_estimate(), _print_niveles(), _print_summary() (+16 more)

### Community 82 - "test_rules.py"
Cohesion: 0.09
Nodes (20): parametrize, test_algebra_trig_geo_analitica_tiene_reglas_de_generacion(), test_cada_perfil_tiene_su_familia_y_sus_tipos(), test_calculo_una_variable_tiene_reglas_de_generacion(), test_familia_o_tipo_desconocido_se_rechaza(), test_geografia_moderna_mexico_tiene_reglas_de_generacion(), test_get_default_rules_known(), test_get_default_rules_unknown_raises() (+12 more)

### Community 83 - "escanear.py"
Cohesion: 0.19
Nodes (22): borrador_cmd(), _carpeta(), maquetacion_cmd(), ocr_cmd(), paginas_cmd(), command, Path, `etl-escanear`: leer un libro escaneado (sin capa de texto) con PaddleOCR-VL y… (+14 more)

### Community 84 - "gemini/generate.py"
Cohesion: 0.15
Nodes (19): Task 6: Llamadas a Gemini: ventana y verificación, 12. Organización del código, logging, _extract_usage(), generate_window(), _generate_with_retry(), Llamadas a Gemini en modo inmediato: una por ventana y la verificación de…, Pull token counts from a google-genai response. Names vary by SDK version. (+11 more)

### Community 85 - "bancos.py"
Cohesion: 0.15
Nodes (18): BaseException, _armar(), _imprimir_resumen(), main(), _mensaje(), Any, command, Path (+10 more)

### Community 86 - "maquetacion.py"
Cohesion: 0.17
Nodes (19): escribir_json(), leer_json(), Any, area(), detectar_regiones(), interseccion(), _predictor(), Any (+11 more)

### Community 87 - "test_generate_window.py"
Cohesion: 0.21
Nodes (16): Resuelve un ejercicio nuevo a ciegas y compara su dificultad con la del libro…, verify_exercise(), _FakeClient, Exception, Las dos llamadas a Gemini del flujo por ventanas, con un cliente falso., Cliente mínimo: devuelve las respuestas en orden, o falla con `raises`., _response(), test_devuelve_las_preguntas_sin_validar_y_los_tokens() (+8 more)

### Community 88 - "escribir_indice"
Cohesion: 0.20
Nodes (20): _archivo_de(), _archivo_en(), escribir_banco(), escribir_indice(), _escribir_json(), leer_indice(), Any, Path (+12 more)

### Community 89 - "_toca"
Cohesion: 0.16
Nodes (19): cargar_bundles(), cargar_perfil(), Lee cada bundle y lo indexa por el código real del manual (`manual.code`). Da…, Lee un perfil de escuela (`perfiles/*.json`) tal cual. Solo se entiende el…, El bundle de mayor `v{n}` de cada manual que hay en `carpeta`. La clave es el…, ultimos_bundles(), parametrize, test_cargar_bundles_exige_el_codigo_del_manual() (+11 more)

### Community 90 - "test_bancos_juego.py"
Cohesion: 0.26
Nodes (16): _args(), _carpetas(), _corre(), _indice(), _perfil_ema(), Path, Conversión de bundles y perfiles a los bancos del juego., test_cli_check_no_escribe_y_falla_con_mundo_vacio() (+8 more)

### Community 91 - "Carpeta"
Cohesion: 0.24
Nodes (4): Libros escaneados (sin capa de texto), Carpeta, Path, Rutas de un escaneo. Todo es JSON o PNG dentro de `raiz`.

### Community 92 - "borrador.py"
Cohesion: 0.15
Nodes (11): limpiar(), orden_de_lectura(), Any, Paso 5: el borrador en Markdown con el texto de PaddleOCR-VL, en orden de…, Índices de las regiones en orden de lectura para páginas de una o dos columnas.…, Une los trozos de una región. PaddleOCR-VL pone punto al final de un trozo…, Quita el guion de corte de renglón («neu-\\nrona» → «neurona») y junta los…, unir_trozos() (+3 more)

### Community 93 - "families.py"
Cohesion: 0.17
Nodes (10): build_verification_instruction(), _conforme(), Instrucciones de la llamada por ventana y de la verificación (spec §6 y §7).…, "Conforme al Manual …" pero "Conforme a la Ley …": el artículo concuerda con el…, Reglas de redacción de las preguntas militares (promoción), sacadas de las…, Las reglas con la fórmula de inicio del manual ("Conforme al Código de Justicia…, reglas_redaccion(), Pruebas unitarias para las reglas y prompts de generación de preguntas de… (+2 more)

### Community 94 - "_preguntas_del_mundo"
Cohesion: 0.17
Nodes (12): motivo_de_descarte(), pertenece(), _preguntas_del_mundo(), Los `ref` de los capítulos que pide el temario, en el orden del bundle. Un…, Si el nodo es uno de `refs` o cuelga de alguno (`01.02` cuelga de `01`; `010`,…, Por qué una pregunta del bundle no entra al juego, o `None` si entra. Gana el…, Las preguntas convertidas de `capitulos` y su cuenta para el resumen., refs_de_capitulos() (+4 more)

### Community 95 - "Ruta al Ascenso — generación de contenido"
Cohesion: 0.22
Nodes (9): 1.1 Los datos: qué no trae el clon, 1.2 Trabajar con Claude Code, 1. Puesta en marcha, 2. Cómo funciona el pipeline, 4. Dónde queda todo, 5. Qué NO hay aquí, a propósito, 6. Herramientas y problemas conocidos, 7. Los comandos, de un vistazo (+1 more)

### Community 96 - "3. Trabajar un manual, de principio a fin"
Cohesion: 0.29
Nodes (7): 3.1 Ingestar el PDF, 3.2 Revisar el árbol ANTES de gastar tokens, 3.3 Estimar el costo, 3.4 Generar una muestra, 3.6 Control de calidad, 3.7 Entregar, 3. Trabajar un manual, de principio a fin

### Community 97 - "`etl/` — Fase 1: extracción estructurada de manuales PDF"
Cohesion: 0.33
Nodes (6): Comandos, `etl/` — Fase 1: extracción estructurada de manuales PDF, Notas sobre Unstructured y Python 3.14, Pipeline, Qué pasa después, Tests

### Community 98 - "`question_generator/` — Fase 2: generación de preguntas con Gemini"
Cohesion: 0.33
Nodes (6): Comandos, Configuración, Entregar un manual, Modos de ejecución, `question_generator/` — Fase 2: generación de preguntas con Gemini, Tests

### Community 99 - "DuplicateNodeRef"
Cohesion: 0.40
Nodes (5): DuplicateNodeRef, DuplicateRunRef, Dos nodos con el mismo `sort_key`: el bundle no tendría identidad., Dos corridas que colapsan en el mismo `ref`., ValueError

### Community 100 - "parse_items"
Cohesion: 0.50
Nodes (5): parse_items(), Valida cada pregunta por separado: una mala no tumba a las demás., _item(), test_parse_items_corta_en_el_tope_por_ventana(), test_parse_items_descarta_solo_lo_malo()

### Community 101 - "3.5 Generar el manual completo"
Cohesion: 0.40
Nodes (5): 3.5 Generar el manual completo, Corrección con las observaciones de un revisor, Niveles cognitivos, Revisión de calidad desde Claude Code, Sin API: generar desde Claude Code

### Community 103 - "mundo_id"
Cohesion: 0.67
Nodes (3): mundo_id(), El id del mundo de una materia: su nombre sin acentos, en minúsculas y con `_`.…, test_mundo_id_normaliza_el_nombre_de_la_materia()

## Knowledge Gaps
- **63 isolated node(s):** `Workflow: graphify`, `El proyecto`, `Reglas para Claude en este repo`, `graphify en Windows`, `1. Por qué existe` (+58 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 591 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `session_scope()` connect `session_scope` to `batch_status.py`, `test_pipeline.py`, `test_claude_code.py`, `6_❓_Preguntas.py`, `data_access.py`, `main`, `test_claude_review.py`, `Manual`, `session.py`, `consolidator.py`, `Question`, `etl/pipeline.py`, `import_reference_questions`, `persist_question`, `test_plan_windows.py`, `get_tree`, `cli/claude_code.py`, `1_📄_Manual.py`, `_seed`, `5_🔍_Search.py`, `test_reference_importer.py`, `cli/generate.py`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Why does `Carpeta` connect `Carpeta` to `profile.py`, `dudas.py`, `escanear.py`, `maquetacion.py`, `ocr.py`, `test_escaneo.py`, `borrador.py`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `Contrato: bundle de contenido v2` connect `Contrato: bundle de contenido v2` to `CONTRATO-BUNDLE.md`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `init_question_tables()` (e.g. with `seed_questions()` and `Task 7: Columnas nuevas, migración y persistencia`) actually correct?**
  _`init_question_tables()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 51 inferred relationships involving `Question` (e.g. with `Task 7: Columnas nuevas, migración y persistencia` and `Task 3: Columnas, guardado y conteo por nivel`) actually correct?**
  _`Question` has 51 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Workflow: graphify`, `El proyecto`, `Reglas para Claude en este repo` to the rest of the system?**
  _63 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_bundle_spec.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._