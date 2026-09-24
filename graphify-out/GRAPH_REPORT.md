# Graph Report - onmy-military-library-contenido  (2026-09-24)

## Corpus Check
- 155 files · ~73,597 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 6, .example 1, .lock 1)

## Summary
- 1314 nodes · 3486 edges · 72 communities (63 shown, 9 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 427 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fa10c35d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- 1_📄_Manual.py
- test_bundle_spec.py
- test_pipeline.py
- rules/base.py
- Contrato: bundle de contenido v2
- profile.py
- 6_❓_Preguntas.py
- session_scope
- get_default_rules
- etl/pipeline.py
- toc_parser.py
- data_access.py
- RawElement
- test_patterns.py
- bundle/__init__.py
- BaldorExerciseExtractor
- assembler.py
- build_window_instruction
- json
- get_profile
- debug_pymupdf.py
- init_db
- build_windows
- etl/models/schema.py
- smoke_imports.py
- temario.py
- _seed
- ChunkConsolidator
- ElementKind
- test_baldor_patterns.py
- batch.py
- _bundle
- test_algebra_trigonometria_geometria_analitica.py
- estimate_only
- schemas.py
- test_checks.py
- `explorer/` — revisor visual del pipeline
- run_ref
- Review Focus
- qgen/pipeline.py
- test_calculo_una_variable.py
- export.py
- etl
- workflows/graphify.md
- CLAUDE.md
- spec.py
- pydantic
- session.py
- hierarchy_tree.py
- validation/__init__.py
- DocumentRules
- DuplicateIndex
- importer.py
- GenerationRun
- Generación de preguntas por ventanas (qgen v2)
- GeneratedQuestion
- checks.py
- test_plan_windows.py
- search.py
- list_manuals
- test_geografia_moderna_mexico.py
- test_temario.py
- test_historia_universal.py
- gemini/generate.py
- defaults.py
- match_libro
- Window

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
- `6. La llamada por ventana` --references--> `WindowResponse`  [INFERRED]
  docs/superpowers/specs/2026-09-23-qgen-ventanas-design.md → question_generator/src/qgen/prompts/schemas.py
- `4. Identidad: las claves estables` --references--> `manuals()`  [INFERRED]
  CONTRATO-BUNDLE.md → etl/src/etl/cli/inspect_cli.py
- `Notas por bloque` --references--> `manuals()`  [INFERRED]
  CONTRATO-BUNDLE.md → etl/src/etl/cli/inspect_cli.py
- `Task 2: Ventanas` --references--> `Chunk`  [INFERRED]
  docs/superpowers/plans/2026-09-23-qgen-ventanas.md → etl/src/etl/models/schema.py
- `graphify` --references--> `get_node()`  [INFERRED]
  .agents/rules/graphify.md → explorer/src/explorer/data_access.py

## Import Cycles
- None detected.

## Communities (72 total, 9 thin omitted)

### Community 0 - "1_📄_Manual.py"
Cohesion: 0.11
Nodes (24): kpi_row(), Render a row of `st.metric` cards. items is a list of (label, value,…, cache_data, Render a single PDF page to PNG bytes via PyMuPDF., Return PNG bytes of the given page (1-based), or None if unavailable. Cached so…, Convenience: render and display in one call., render_page(), render_page_widget() (+16 more)

### Community 1 - "test_bundle_spec.py"
Cohesion: 0.11
Nodes (35): copy, _errors(), _options(), El contrato del bundle: lo que se acepta y, sobre todo, lo que no. Cada caso de…, test_api_key_en_metadata_bloquea_la_entrega(), test_arbol_sin_raiz(), test_cadena_de_conexion_en_metadata_bloquea_la_entrega(), test_ciclo_en_el_arbol() (+27 more)

### Community 2 - "test_pipeline.py"
Cohesion: 0.17
Nodes (41): Las preguntas crudas de una ventana (sin validar) y lo que costó pedirlas., VerificationOutcome, WindowOutcome, _ejercicio_nuevo(), _estimate(), FakeGemini, _item(), _letra() (+33 more)

### Community 3 - "rules/base.py"
Cohesion: 0.32
Nodes (9): _resolve_rules(), merge_rules(), Per-archetype question-generation rules + per-document override mechanism. The…, Sparse overrides to layer over a profile default. Stored at…, rules_to_dict(), RulesOverride, test_el_override_no_cambia_familia_ni_tipos(), test_override_replaces_only_provided_fields() (+1 more)

### Community 4 - "Contrato: bundle de contenido v2"
Cohesion: 0.04
Nodes (43): 1. Por qué existe, 2. Forma del fichero, 3. Estructura, 4. Identidad: las claves estables, 5. Las validaciones, 6. Los dos comandos, 7. Versionado del contrato, Aquí — `qgen-export` (+35 more)

### Community 5 - "profile.py"
Cohesion: 0.14
Nodes (30): dataclasses, HeadingCandidate, match_anexo(), match_baldor_capitulo(), match_baldor_caso(), match_baldor_inciso(), match_baldor_subseccion_romana(), match_baldor_tema_mayusculas() (+22 more)

### Community 6 - "6_❓_Preguntas.py"
Cohesion: 0.10
Nodes (34): Task 11: Explorador: tipo, cita y motivos, link_to(), Build an internal Streamlit link. `page_url` is the relative path Streamlit…, Preguntas generadas — revisión visual, cobertura y corridas. Es la vista de la…, _render_question(), get_question_kpis(), list_questions(), list_runs() (+26 more)

### Community 7 - "session_scope"
Cohesion: 0.12
Nodes (38): session_scope(), build_bundle(), DuplicateNodeRef, DuplicateRunRef, _materia_hint(), _pipeline_commit(), Any, Session (+30 more)

### Community 8 - "get_default_rules"
Cohesion: 0.21
Nodes (13): get_default_rules(), parametrize, test_algebra_trigonometria_geometria_analitica_tiene_reglas_de_generacion(), test_cada_perfil_tiene_su_familia_y_sus_tipos(), test_calculo_una_variable_tiene_reglas_de_generacion(), test_familia_y_tipos_viajan_en_la_foto_de_la_corrida(), test_geografia_moderna_mexico_tiene_reglas_de_generacion(), test_get_default_rules_known() (+5 more)

### Community 9 - "etl/pipeline.py"
Cohesion: 0.11
Nodes (26): ABC, ExtractorBase, Path, Common interface for layout extractors. Adapters (Docling, Unstructured, etc.)…, Run the extractor on a PDF and return normalized elements., DoclingAdapter, Path, Wraps Docling's DocumentConverter with conservative memory settings. Defaults… (+18 more)

### Community 10 - "toc_parser.py"
Cohesion: 0.07
Nodes (33): detect_toc_pages(), _infer_depth(), _is_roman_only(), _lookback_marker(), _parse_page_number(), parse_toc(), _peek_parte_title(), BaseModel (+25 more)

### Community 11 - "data_access.py"
Cohesion: 0.15
Nodes (25): graphify, _chunk_to_summary(), ChunkSummary, get_chunks_for_manual(), get_chunks_for_node(), get_global_kpis(), get_node(), get_node_ancestors() (+17 more)

### Community 12 - "RawElement"
Cohesion: 0.27
Nodes (8): TocResult, One layout element extracted from a PDF page. Both Docling and Unstructured…, RawElement, _Builder, HierarchyAssembler, _peek_next_title(), Assembles a tree from raw elements, optionally guided by a TOC. Parameters…, Look ahead up to 3 elements for something that acts as the heading title.

### Community 13 - "test_patterns.py"
Cohesion: 0.12
Nodes (27): classify_heading(), match_articulo(), match_titulo(), Compatibility shim: classify using the default 'manual' profile. New code…, Default classify_heading uses 'manual' profile — articles are not its concern…, test_anexo(), test_articulo_quater(), test_articulo_septimus() (+19 more)

### Community 14 - "bundle/__init__.py"
Cohesion: 0.20
Nodes (16): Bundle de contenido: la interfaz entre la generación de preguntas y la webapp., dumps(), Path, Serialización canónica: UTF-8, indentado a 2, sin escapar acentos., Escribe el bundle (comprimiendo si es grande) y su `.sha256`. Devuelve `(ruta…, Comprueba el `.sha256` que acompaña al bundle. Lanza si no cuadra., Lee un bundle `.json` o `.json.gz`. No valida: para eso está `validate`., read_bundle() (+8 more)

### Community 15 - "BaldorExerciseExtractor"
Cohesion: 0.11
Nodes (18): BaldorExercise, BaldorExerciseExtractor, flush_current(), Extractor de ejercicios resueltos y problemas prácticos de Álgebra de Baldor., Genera el texto estructurado del ejercicio para el prompt de generación de…, Analizador para extraer problemas numerados, procedimientos y soluciones., Extrae la lista de ejercicios presentes en un bloque de texto., Parsea el bloque de texto de un ejercicio individual extrayendo enunciado,… (+10 more)

### Community 16 - "assembler.py"
Cohesion: 0.13
Nodes (10): _label_for_depth(), Build a manual's hierarchy tree from extracted elements + optional TOC.…, _strip_known_prefix(), HeadingMatch, Profile-resolved heading match: kind + numeric depth., DocumentProfile, Return a profile-resolved HeadingMatch, or None if not a heading., Run metadata extractors over `text` and return any captures. (+2 more)

### Community 17 - "build_window_instruction"
Cohesion: 0.15
Nodes (19): build_window_instruction(), _conforme(), _ejemplos(), Any, Instrucciones de la llamada por ventana y de la verificación (spec §6 y §7).…, Instrucción del sistema para la llamada por ventana: plantilla de la familia +…, "Conforme al Manual …" pero "Conforme a la Ley …": el artículo concuerda con el…, Ejemplos de referencia; si no hay, los militares de siempre solo en la familia… (+11 more)

### Community 18 - "json"
Cohesion: 0.09
Nodes (18): Inspect a cached docling extraction to find LIBRO/TITULO lines and Latin-suffix…, Exception, json, pickle, _FakeClient, Las dos llamadas a Gemini del flujo por ventanas, con un cliente falso., Cliente mínimo: devuelve las respuestas en orden, o falla con `raises`., _response() (+10 more)

### Community 19 - "get_profile"
Cohesion: 0.12
Nodes (25): auto_detect_profile(), get_profile(), Heuristic profile pick based on the first few elements' text. Looks for genre-…, Manual profile builds PARTE → Capítulo → Sección hierarchy from body., Legal-code profile builds Libro → Título → Capítulo → Artículo., Drop filters silence Cámara/DOF noise without losing real content., Reform annotations get attached as metadata on the relevant node., _t() (+17 more)

### Community 20 - "debug_pymupdf.py"
Cohesion: 0.15
Nodes (10): collections, One-off debug script: inspect characters used as TOC leaders., main(), Path, Quick visual inspection of an in-memory hierarchy without persisting., fitz, pymupdf, rapidocr (+2 more)

### Community 21 - "init_db"
Cohesion: 0.17
Nodes (12): Engine, main(), command, Path, init_db(), Create all tables. Idempotent — safe to run on existing DBs., _default_db_url(), get_engine() (+4 more)

### Community 22 - "build_windows"
Cohesion: 0.20
Nodes (24): Protocol, build_windows(), ChunkLike, Ventanas de texto para generar preguntas (spec §4). Una ventana es un grupo de…, Quita del inicio de `text` lo que repite del final de `prev` (y el salto que lo…, Agrupa los chunks de un nodo en ventanas. Puro y determinista., strip_overlap(), _unir() (+16 more)

### Community 23 - "etl/models/schema.py"
Cohesion: 0.11
Nodes (30): DeclarativeBase, estimate_doc(), main(), Compute approximate Gemini cost for question generation across ingested…, node(), command, Print the hierarchy of a manual as a tree., Show a node's breadcrumb plus its chunks (truncated). (+22 more)

### Community 25 - "temario.py"
Cohesion: 0.22
Nodes (10): match_parte_temario(), Parte numerada de un temario ('1.1 Los elementos del proceso comunicativo').…, CapitulosConTemas, _norm(), _numero_de_tema(), Selección por temario: qué bloques, partes, capítulos o temas de un libro…, (número, resto del encabezado) si el encabezado abre un capítulo., Devuelve los elementos (con su índice original) que entran al árbol. - El… (+2 more)

### Community 26 - "_seed"
Cohesion: 0.38
Nodes (9): AppTest, _open_page(), Pestaña "Exportar Bundle" de la página de preguntas, ejecutada con AppTest. La…, _seed(), test_la_cita_se_muestra_tal_cual(), test_la_pregunta_muestra_su_tipo_y_sus_motivos(), test_un_bundle_con_errores_no_se_ofrece_y_se_explica_por_que(), test_un_bundle_que_cumple_el_contrato_se_puede_descargar() (+1 more)

### Community 27 - "ChunkConsolidator"
Cohesion: 0.18
Nodes (12): ChunkConsolidator, ConsolidatedChunk, BaseModel, Convierte un número romano a entero, o None si no es válido., Reordena fracciones romanas que docling extrajo en orden incorrecto. Docling a…, HierarchyNode, HierarchyTree, BaseModel (+4 more)

### Community 28 - "ElementKind"
Cohesion: 0.16
Nodes (18): Prueba unitaria del reordenamiento de fracciones romanas., docling_core_types_doc, DoclingDocument, enum, Consolida los elementos del cuerpo de cada nodo hoja en fragmentos con límite…, elements_from_document(), _first_bbox(), _first_page() (+10 more)

### Community 29 - "test_baldor_patterns.py"
Cohesion: 0.12
Nodes (15): Pruebas unitarias para los patrones y jerarquía de Álgebra de Baldor., Verifica subcasos con letras tipo a) o b)., Verifica que el perfil 'algebra_baldor' solo clasifica capítulos a nivel 0 y no…, En Álgebra de Baldor los únicos nodos son los 16 capítulos ('I. Suma' … 'XXXII.…, Verifica que los capítulos con numeración romana se reconocen con su ordinal y…, Verifica las subsecciones con números romanos en mayúsculas., Verifica el reconocimiento de los casos clásicos de factorización., Verifica encabezados conceptuales y reglas generales en mayúsculas sostenidas. (+7 more)

### Community 30 - "batch.py"
Cohesion: 0.11
Nodes (27): functools, BatchItemResult, BatchRequest, BatchSubmitResult, _build_inline_request(), parse_batch_results(), Batch-mode generation: submit one job for all nodes, poll, parse later. Trade-…, Yield BatchItemResult entries. Prefers matching by… (+19 more)

### Community 31 - "_bundle"
Cohesion: 0.25
Nodes (8): _bundle(), `cost_input_tokens` contiene 'token': el detector no debe morder ahí., Un bundle mínimo pero completo y válido., test_bundle_valido_pasa_sin_errores(), test_corrida_con_nodos_fallidos_avisa(), test_los_contadores_de_tokens_no_son_un_secreto(), test_nodo_con_texto_sin_pregunta_avisa_pero_no_bloquea(), test_preguntas_rechazadas_avisan()

### Community 32 - "test_algebra_trigonometria_geometria_analitica.py"
Cohesion: 0.53
Nodes (5): Perfil `algebra_trigonometria_geometria_analitica`: los cuatro capítulos de la…, test_el_arbol_son_los_cuatro_capitulos_de_la_imagen(), test_la_portada_queda_fuera(), test_secciones_ejemplos_y_teoremas_quedan_en_el_cuerpo_de_su_capitulo(), _tree()

### Community 33 - "estimate_only"
Cohesion: 0.20
Nodes (13): doc_token_estimate(), estimate_windows(), Cost accounting: predictions before a run + actual after. Pricing (USD per 1M…, Una llamada por ventana (instrucción + texto de la ventana + documento…, WindowEstimate, _doc_token_estimate_from_chunks(), estimate_only(), Costo aproximado sin llamar a Gemini; el entero son las ventanas por procesar. (+5 more)

### Community 34 - "schemas.py"
Cohesion: 0.26
Nodes (13): Task 3: Esquemas de salida de la llamada por ventana, Task 4: Revisiones de cada pregunta, Task 6: Llamadas a Gemini: ventana y verificación, 12. Organización del código, GeneratedOption, BaseModel, StrEnum, QuestionType (+5 more)

### Community 35 - "test_checks.py"
Cohesion: 0.15
Nodes (25): parse_items(), Valida cada pregunta por separado: una mala no tumba a las demás., Revisión por tipo contra el texto de la ventana (spec §7, tabla de revisiones)., review(), Verdict, _item(), _q(), Revisiones de cada pregunta de una ventana (spec §7). (+17 more)

### Community 36 - "`explorer/` — revisor visual del pipeline"
Cohesion: 0.29
Nodes (6): Cómo correr, El árbol y la cobertura, `explorer/` — revisor visual del pipeline, La revisión, Navegación, Vistas

### Community 37 - "run_ref"
Cohesion: 0.29
Nodes (8): 10. Contrato v2 del bundle, iso(), datetime, Clave estable de una corrida: `{model}--{mode}--{inicio compacto UTC}`., Fecha en el formato del contrato: ISO 8601 UTC con `Z`. SQLite devuelve los…, run_ref(), test_fecha_ingenua_se_lee_como_utc(), test_ref_de_corrida_es_estable()

### Community 38 - "Review Focus"
Cohesion: 0.25
Nodes (7): Generación de preguntas por ventanas (qgen v2) — Plan de implementación, Global Constraints, Review Focus, Task 12: Verificación final y prueba real, Task 2: Ventanas, Task 5: Instrucciones por familia, Task 8: Planificación de ventanas y reanudación

### Community 39 - "qgen/pipeline.py"
Cohesion: 0.12
Nodes (30): concurrent_futures, actual_cost_usd(), Compute actual cost from observed usage_metadata totals. `cache_create_tokens`…, _Accepted, _chunks_for(), _done_window_keys(), _nodes_with_text(), plan_windows() (+22 more)

### Community 40 - "test_calculo_una_variable.py"
Cohesion: 0.53
Nodes (5): Perfil `calculo_una_variable`: los tres capítulos completos de la imagen.…, test_el_arbol_son_los_tres_capitulos_de_la_imagen(), test_la_portada_queda_fuera(), test_secciones_y_subtitulos_quedan_en_el_cuerpo_de_su_capitulo(), _tree()

### Community 41 - "export.py"
Cohesion: 0.20
Nodes (13): date, SHA-256 del PDF de origen, si sigue estando donde dice el manual., source_digest(), bundle_filename(), next_version(), Siguiente `v{n}` libre para este manual en `out_dir`. Se cuenta por manual y no…, slug(), main() (+5 more)

### Community 42 - "etl"
Cohesion: 1.00
Nodes (3): etl, explorer, question_generator

### Community 45 - "spec.py"
Cohesion: 0.22
Nodes (17): gzip, hashlib, _bool(), _dict(), find_secrets(), walk(), _int(), _is_iso() (+9 more)

### Community 46 - "pydantic"
Cohesion: 0.16
Nodes (9): GeminiClient, Thin wrapper around google-genai with explicit context caching. We keep this…, ClassifiedHeading, GeminiHeadingClassifier, HeadingClassificationBatch, BaseModel, Gemini-based fallback classifier for ambiguous headings. Used only when the…, pydantic (+1 more)

### Community 47 - "session.py"
Cohesion: 0.07
Nodes (42): contextlib, Task 9: Corrida por ventanas, estimación y CLI (retira el flujo viejo), dotenv, main(), _print_table(), command, Path, Run both extractors with persistence disabled and emit a comparison. (+34 more)

### Community 48 - "hierarchy_tree.py"
Cohesion: 0.36
Nodes (7): collections_abc, _icon_for(), _indent(), Hierarchy tree rendered as nested expanders with optional click-to-navigate., Render the manual's tree. `on_select` is a function that takes a NodeSummary…, _render_node(), render_tree()

### Community 55 - "DocumentRules"
Cohesion: 0.23
Nodes (9): Task 1: Familia y tipos en las reglas, DocumentRules, Any, Knobs that shape question generation for a class of documents., rules_from_dict(), test_familia_o_tipo_desconocido_se_rechaza(), test_un_libro_que_no_es_de_matematicas_no_admite_ejercicios(), test_una_foto_antigua_con_ejercicios_se_lee_como_de_matematicas() (+1 more)

### Community 56 - "DuplicateIndex"
Cohesion: 0.12
Nodes (14): DuplicateIndex, norm_text(), _nucleo(), Enunciados ya aceptados, por nodo, para descartar duplicadas (spec §7). En…, El enunciado desde el primer «¿»: sin el prefijo común de la familia militar., Similitud simétrica: `SequenceMatcher` da valores distintos según el orden., Para comparar texto literal: NFC, espacios colapsados, comillas y guiones…, _similitud() (+6 more)

### Community 57 - "importer.py"
Cohesion: 0.08
Nodes (31): csv, main(), command, Path, Carga un archivo de preguntas de ejemplo y las guarda en la base de datos., datetime, Esquema SQLAlchemy para preguntas de referencia (banco de ejemplos/exemplars).…, Retorna la fecha y hora actual en UTC. (+23 more)

### Community 58 - "GenerationRun"
Cohesion: 0.15
Nodes (30): Inserta preguntas generadas directamente en el chat para el manual 11 (Álgebra…, seed_questions(), datetime, Task 10: Contrato v2 del bundle, Task 7: Columnas nuevas, migración y persistencia, 8. Persistencia, create_run(), finalize_run() (+22 more)

### Community 59 - "Generación de preguntas por ventanas (qgen v2)"
Cohesion: 0.14
Nodes (13): 11. Trabajo en la webapp (lo hace el usuario), 13. Errores, 14. Pruebas (TDD), 15. Riesgos, 1. Contexto, 2. Decisiones del usuario, 3. Alcance, 4. Ventanas (+5 more)

### Community 60 - "GeneratedQuestion"
Cohesion: 0.16
Nodes (22): model_validator, GeneratedQuestion, OptionRole, Una pregunta completa tal como la devuelve la llamada por ventana., WindowQuestion, _question(), _make_options(), Build a list of options matching the canonical 1+1+2 distribution. (+14 more)

### Community 61 - "checks.py"
Cohesion: 0.15
Nodes (15): difflib, _barajadas(), _literal(), norm_math(), Revisiones de cada pregunta generada por ventana (spec §7). Todo es…, ¿Está `fragmento` literal en `texto`? Se acepta también con la notación…, La pregunta lista para guardar, con las opciones barajadas de forma…, Textos de las opciones para la verificación (en otro orden, sin roles) y la… (+7 more)

### Community 62 - "test_plan_windows.py"
Cohesion: 0.39
Nodes (11): _keys(), Qué ventanas procesa una corrida (spec §4): selección, reanudación y --limit., _seed(), test_gana_el_ultimo_estado_de_cada_ventana(), test_las_introducciones_quedan_fuera(), test_limit_cuenta_ventanas(), test_regenerate_ignora_el_historial(), test_se_saltan_las_ventanas_ok_y_se_reintentan_las_fallidas() (+3 more)

### Community 63 - "search.py"
Cohesion: 0.28
Nodes (8): init_fts(), BaseModel, query(), Full-text search over chunks using SQLite FTS5. We create a virtual table…, FTS5 has reserved chars; we wrap free-form input as a phrase if needed., Create FTS5 virtual table + triggers if missing, then backfill any chunks that…, _sanitize(), SearchHit

### Community 64 - "list_manuals"
Cohesion: 0.18
Nodes (10): get_extraction_cache(), get_manual(), list_manuals(), Reads `data/processed/<code>.<extractor>.json` for a manual. Returns the raw…, Full-text search across chunks via SQLite FTS5., Pruebas unitarias para la capa de acceso a datos del explorador…, Verifica la consulta de detalles de un manual específico., Verifica el listado de manuales y los KPIs globales del explorador. (+2 more)

### Community 65 - "test_geografia_moderna_mexico.py"
Cohesion: 0.48
Nodes (6): Perfil `geografia_moderna_mexico`: el temario de la imagen, como Capítulo ›…, test_cada_tema_cuelga_de_su_capitulo(), test_el_arbol_es_el_de_la_imagen(), test_lo_que_no_esta_en_la_imagen_queda_fuera(), test_los_subtitulos_y_los_capitulos_completos_quedan_como_texto(), _tree()

### Community 66 - "test_temario.py"
Cohesion: 0.48
Nodes (6): Perfil `taller_lectura_redaccion`: solo el temario pedido, como Bloque › Parte.…, test_cada_parte_cuelga_de_su_bloque(), test_cada_parte_lleva_solo_su_texto(), test_lo_que_no_esta_en_la_imagen_no_queda_en_ningun_nodo(), test_solo_quedan_los_bloques_y_partes_de_la_imagen(), _tree()

### Community 67 - "test_historia_universal.py"
Cohesion: 0.53
Nodes (5): Perfil `historia_universal`: el temario de la imagen, como Capítulo › Tema.…, test_cada_tema_cuelga_del_capitulo(), test_el_arbol_es_el_capitulo_y_sus_cuatro_temas(), test_los_subtitulos_quedan_en_el_cuerpo_de_su_tema(), _tree()

### Community 68 - "gemini/generate.py"
Cohesion: 0.24
Nodes (11): logging, _extract_usage(), generate_window(), _generate_with_retry(), Llamadas a Gemini en modo inmediato: una por ventana y la verificación de…, Resuelve un ejercicio nuevo a ciegas y compara su dificultad con la del libro…, Pull token counts from a google-genai response. Names vary by SDK version., Una llamada por ventana. Si la respuesta no se puede leer, se reintenta… (+3 more)

### Community 69 - "defaults.py"
Cohesion: 0.25
Nodes (6): Profile-default rules. Edit here to change defaults globally. Per-document…, Pruebas unitarias para las reglas y prompts de generación de preguntas de…, La instrucción por ventana lleva las reglas de Baldor y pide ejercicios., Verifica que el perfil 'algebra_baldor' está registrado en el catálogo de…, test_algebra_baldor_prompt_rendering(), test_algebra_baldor_rules_registered()

### Community 70 - "match_libro"
Cohesion: 0.50
Nodes (4): match_libro(), test_libro_with_trailing_title(), test_match_libro(), test_match_libro_with_accents()

### Community 71 - "Window"
Cohesion: 0.40
Nodes (5): build_window_message(), Mensaje de la llamada: el manual, la ruta del nodo, las páginas y el texto de…, Identidad estable de la ventana: `<node_id>:<ordinal_desde>-<ordinal_hasta>`., Window, test_el_mensaje_lleva_ruta_paginas_y_texto()

## Knowledge Gaps
- **47 isolated node(s):** `Workflow: graphify`, `graphify`, `graphify en Windows`, `1. Por qué existe`, `2. Forma del fichero` (+42 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 420 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `session_scope()` connect `session_scope` to `list_manuals`, `test_pipeline.py`, `_seed`, `Contrato: bundle de contenido v2`, `6_❓_Preguntas.py`, `etl/pipeline.py`, `export.py`, `data_access.py`, `session.py`, `init_db`, `etl/models/schema.py`, `importer.py`, `GenerationRun`, `test_plan_windows.py`, `search.py`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Why does `manuals()` connect `Contrato: bundle de contenido v2` to `etl/models/schema.py`, `session_scope`, `session.py`?**
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