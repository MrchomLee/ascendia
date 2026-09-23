# Generación de preguntas por ventanas (qgen v2)

**Fecha:** 2026-09-23 · **Rama:** `feat/qgen-ventanas` · **Estado:** propuesta para revisión

## 1. Contexto

`qgen` genera preguntas **por nodo** en dos pasos: un "creador" propone 1–3 enunciados a
partir del texto completo del nodo, y después se hace una llamada por enunciado para las
4 opciones y la justificación. Una revisión en Python marca `needs_review` las preguntas
cuya respuesta correcta no es una cita literal.

Ese diseño se hizo para los manuales militares (cientos de nodos pequeños, texto
definicional). Con los libros de aspirantes falla:

| Problema | Evidencia |
|---|---|
| Muy pocas preguntas | Cálculo: 3 nodos / 112k caracteres → 3–9 preguntas; Álgebra y trigonometría: 4 nodos / 231k → 4–12 |
| La regla literal rompe los ejercicios | una derivada o un despeje nunca es cita literal → `needs_review` → la webapp no los sirve |
| Prompt militar para todos | rol "experto en Materias Militares", ejemplos de teoría de la guerra (la tabla `reference_questions` está vacía), "Conforme al calculo_una_variable, …" |
| Opciones pensadas para frases | "confusa = mitad de una frase + final de otra", "todas empiezan con palabras distintas" |
| Sin comprobar la clave | solo la coincidencia literal |
| Export bloqueado | el contrato v1 admite **una** pregunta por (corrida, nodo) |

## 2. Decisiones del usuario

1. Generar por **ventanas de texto** (A) con **una sola llamada por ventana** (B).
2. **Todas las preguntas posibles** por materia: sin cuota, cobertura total del texto.
3. **Dos familias:** `militar` y `civil`.
4. En `civil` hay preguntas de **teoría**, con respuesta **literal**, y de **ejercicios**
   **basados en el PDF**: por cada ejemplo o ejercicio resuelto del libro, el **ejemplo tal
   cual** (respuesta del libro) **más uno nuevo** del mismo tipo que **no supere la
   dificultad** del libro.
5. El usuario adapta la webapp a un **contrato v2** del bundle.
6. El usuario tiene preguntas de exámenes reales; se importarán después (fuera de alcance).

## 3. Alcance

**Dentro:** ventanas, llamada única por ventana, familias y tipos por perfil, validación
por tipo, verificación de ejercicios nuevos, reanudación, columnas nuevas en `questions`,
contrato v2 del bundle, explorador (mostrar tipo, cita y motivos), CLI y estimación.

**Fuera:** el ETL y los árboles de nodos (no se tocan); importar exámenes reales (el
comando `qgen-import-examples` ya existe); verificación con LLM de las preguntas de
teoría; el modo batch (sigue desactivado); cambios en la webapp (los hace el usuario, ver §11).

## 4. Ventanas

Una **ventana** es un grupo de chunks consecutivos **de un mismo nodo** (nunca mezcla
nodos), en orden de `Chunk.ordinal`.

**Texto de la ventana.** Los chunks de un nodo se solapan: el chunker repite al inicio de
cada chunk los últimos ~120 caracteres del anterior. Al unir chunks se quita ese
solapamiento: el sufijo más largo (hasta 200 caracteres) del chunk anterior que sea
prefijo del siguiente, más el separador `\n\n` que lo sigue.

**Algoritmo** (`build_windows(chunks) -> list[Window]`, puro y determinista):

- Se agregan chunks mientras el texto acumulado no pase de `OBJETIVO = 4000` caracteres.
- A partir de `MINIMO_CORTE = 3000`, si el siguiente chunk (ya sin solapamiento) empieza
  con un encabezado, la ventana se cierra **antes** de él. Encabezado = primera línea que
  empieza por `EJEMPLO <n>`, `<n>.<n> <Mayúscula>`, `Definición`, `DEFINICIÓN` o `Teorema`.
- Nunca se pasa de `MAXIMO = 6000`, salvo que un solo chunk ya lo supere: entonces ese
  chunk forma su propia ventana.
- Un nodo pequeño da una sola ventana.

**Identidad:** `window_key = "<node_id>:<ordinal_desde>-<ordinal_hasta>"`. Las páginas de
la ventana son `min(page_start)`–`max(page_end)` de sus chunks.

**Selección de nodos:** la misma que hoy (nodos con chunks, sin títulos "introducci…"),
salvo una diferencia: ya no se excluye un nodo entero por tener alguna pregunta; lo que
se salta son sus ventanas ya procesadas (ver "Reanudar").

**Reanudar.** Cada corrida nace con todas sus ventanas planeadas en `pendiente` dentro
de `metadata_json["ventanas"]` y las va marcando `ok` o `fallida`. Para cada ventana
**gana el estado de la corrida más reciente** que la tocó. Una corrida nueva **se salta**
las ventanas cuyo último estado es `ok` (aunque no dejaran preguntas, por ejemplo porque
todas se descartaron) y las que tienen preguntas guardadas (cubre una corrida que murió
sin cerrarse). `--regenerate` borra las preguntas de las ventanas que va a rehacer e
ignora el historial; si falla o se corta, sus ventanas quedan `fallida` o `pendiente` y
se retoman.

## 5. Familias y tipos

`DocumentRules` gana dos campos, con valor por perfil en `rules/defaults.py`:

- `familia: Literal["militar", "civil"]`
- `tipos: tuple[str, ...]`, subconjunto de `("teoria", "ejercicio")`

| Familia | Perfiles | Tipos |
|---|---|---|
| militar | `manual`, `codigo_legal`, `ley_organica` | teoria |
| civil | `historia_universal`, `geografia_moderna_mexico` | teoria |
| civil | `algebra_baldor`, `calculo_una_variable`, `algebra_trigonometria_geometria_analitica`, `taller_lectura_redaccion` | teoria, ejercicio |

`ejercicio` habilita los dos tipos de pregunta de ejercicio: `ejercicio_libro` y
`ejercicio_nuevo`. En el Taller, los ejercicios son aplicar las reglas de acentuación y
puntuación a palabras u oraciones. `RulesOverride` no cambia la familia ni los tipos.

## 6. La llamada por ventana

**Instrucción del sistema** = plantilla de la familia + reglas del perfil + ejemplos.

- **Plantilla `militar`:** el rol actual (evaluador de exámenes de promoción). Enunciado con
  el formato `Conforme al <título del manual>, <ruta del nodo>, ¿…?`, usando
  `Manual.title` (o `Manual.code` si no hay título), nunca el identificador del perfil.
- **Plantilla `civil`:** evaluador del examen de admisión, nivel bachillerato; enunciados
  directos, sin prefijo.
- **Ambas** piden **una pregunta por cada elemento evaluable** de la ventana
  (definiciones, propiedades, reglas, clasificaciones, hechos, actores, años,
  ubicaciones) y, si el perfil permite ejercicios, **por cada ejemplo o ejercicio
  resuelto**, un `ejercicio_libro` (el ejemplo del libro, con la respuesta del libro)
  y un `ejercicio_nuevo` (mismo tipo y procedimiento, datos nuevos, dificultad igual o
  menor). Un "ejemplo resuelto" es cualquier pasaje en que el libro aplica una regla o
  un procedimiento y muestra el resultado. Máximo 30 preguntas por ventana.
- **Reglas del perfil:** estilo, temas preferentes y prohibidos, instrucciones extra (como hoy).
- **Ejemplos:** `reference_questions` del perfil (hasta 5). Si no hay, la familia civil no
  lleva ejemplos; los ejemplos por defecto de teoría de la guerra solo se usan en `militar`.

**Mensaje de la llamada:** título del manual, ruta del nodo, páginas de la ventana y su
texto literal.

**Opciones:** siempre 1 `correct`, 1 `confusa`, 2 `distractor` (sin cambio para la webapp).

| Tipo | `correct` | `confusa` | `distractor` |
|---|---|---|---|
| teoria | fragmento **literal** de la ventana | concepto parecido con un detalle crítico cambiado | otros conceptos reales del texto |
| ejercicio_* | el resultado | el resultado del error más típico | otros errores típicos |

Se eliminan las instrucciones "mezcla la primera mitad de la correcta con el final de
otro concepto" y, para ejercicios, "todas las opciones deben empezar con palabras distintas".

**Salida estructurada** (`WindowResponse`):

```json
{"preguntas": [{
  "tipo": "teoria | ejercicio_libro | ejercicio_nuevo",
  "pregunta": "…",
  "opciones": [{"rol": "correct | confusa | distractor", "texto": "…"}],
  "cita": "fragmento literal de la ventana en que se apoya",
  "justificacion": "teoría: por qué es la correcta · ejercicio: resolución paso a paso"
}]}
```

Límites: `pregunta` ≤ 1000, `texto` de opción ≤ 500, `cita` ≤ 2000, `justificacion` ≤ 2000
caracteres. En `ejercicio_libro` la cita es el ejemplo del libro con su resultado; en
`ejercicio_nuevo`, el ejemplo del libro en que se basa.

**Parámetros:** modelo por defecto `gemini-3.6-flash` (como hoy), temperatura 0.3. La
caché del PDF sigue como hoy: se usa si la cuenta lo permite; si falla, se trabaja sin
ella (2 hilos en lugar de 15).

## 7. Validación y verificación

La respuesta se interpreta como JSON y **cada pregunta se valida por separado**: una
pregunta inválida no invalida la ventana.

**Resultados posibles:** `pending` (pasa todo; la webapp la sirve), `needs_review` (se
guarda con `metadata.motivos`), **descartada** (no se guarda; el motivo va a
`run.metadata_json["descartes"]`).

**Se descarta si:**
- no cumple la estructura (4 opciones, roles 1/1/2, textos distintos, cita no vacía,
  límites de longitud);
- pasa de las 30 primeras preguntas de la ventana;
- su tipo no está permitido por el perfil;
- es duplicada de otra pregunta **del mismo nodo** (de esta corrida o anteriores): en
  `teoria`, si el núcleo del enunciado (desde el primer «¿», sin el prefijo «Conforme
  al …, <ruta>,» que comparten todas las militares de un nodo) tiene similitud ≥ 0.90
  en ambos sentidos (`difflib.SequenceMatcher`) **y** la respuesta correcta es la misma;
  en ejercicios, solo si el enunciado normalizado es **idéntico** (dos ejercicios del
  mismo tipo difieren en los datos y se parecen mucho a propósito).

**Revisiones por tipo:**

| Tipo | Comprobación | Motivo si falla |
|---|---|---|
| teoria | `cita` ⊂ ventana y `correct` ⊂ ventana (normalización de texto) | "cita no encontrada" / "respuesta parafraseada" |
| ejercicio_libro | `cita` ⊂ ventana; `correct` ⊂ `cita` (normalización matemática) | "cita no encontrada" / "el resultado no aparece en el ejemplo citado" |
| ejercicio_nuevo | `cita` ⊂ ventana + **verificación** | "sin ejemplo de referencia" / motivo de la verificación |

**Normalización de texto:** Unicode NFC, espacios colapsados, comillas y guiones
unificados (`“”«»` → `"`, `–—` → `-`), sin distinguir mayúsculas.
**Normalización matemática**: la de texto + NFKC (𝑥 → x, ² → 2), sin espacios, sin `^`,
`·`, `*` ni `×`, y `−` → `-`, `′` → `'`. Así `x^2 − 4` y el aplanado `x2 - 4` coinciden.
Los ejercicios se comparan con ella; en `teoria` basta con que coincida la normalización
de texto **o** la matemática (la teoría de los libros de matemáticas también trae fórmulas).

**Verificación de `ejercicio_nuevo`:** una llamada aparte, temperatura 0, que recibe el
enunciado, las 4 opciones **barajadas y sin roles** (A–D) y la cita (el ejemplo del
libro). Salida `{razonamiento, opcion: A|B|C|D|ninguna|varias, dificultad: menor|igual|mayor}`.
Pasa a `needs_review` si la opción no es la `correct`, si responde `ninguna` o `varias`,
o si la dificultad es `mayor`. El resultado se guarda en `metadata.verificacion` y sus
tokens cuentan en el costo de la corrida.

**Orden de las opciones:** se baraja al guardar, con una semilla derivada del enunciado
(reproducible), para que la correcta no quede siempre en la misma posición.

## 8. Persistencia

**Columnas nuevas en `questions`:**

| Columna | Tipo | Contenido |
|---|---|---|
| `question_type` | `String(32)`, no nula, por defecto `teoria` | `teoria`, `ejercicio_libro` o `ejercicio_nuevo` |
| `source_quote` | `Text`, no nula, por defecto `""` | la cita |
| `window_key` | `String(64)`, indexada | la ventana que la produjo |

`metadata_json` de la pregunta: `paginas`, `motivos`, `verificacion`, tokens y latencia.

**Migración:** `init_question_tables` añade con `ALTER TABLE … ADD COLUMN` las columnas
que falten (idempotente). La tabla está vacía hoy. Se mantiene la restricción única
(`run_id`, `node_id`, `generation_order`); `generation_order` es único dentro de la corrida.

**Corrida (`GenerationRun`):** `nodes_total`, `nodes_completed` y `nodes_failed` cuentan
**nodos** (hoy cuentan preguntas por error): completado = todas sus ventanas `ok`.
`metadata_json` añade `ventanas` (estado por `window_key`), conteos de preguntas por tipo
y estado, y `descartes`.

## 9. CLI, estimación y explorador

- `qgen-generate` conserva sus opciones: `--limit` limita **ventanas**; `--node` genera
  solo las ventanas de ese nodo; `--regenerate` y `--dry-run` como hoy.
- `--dry-run` estima con el número de ventanas: por ventana, entrada = instrucción
  (~1 500 tokens) + texto de la ventana (caracteres / 4); salida = 1 pregunta por cada
  350 caracteres de ventana × 350 tokens; más una verificación (~1 000 de entrada, ~800
  de salida) por cada `ejercicio_nuevo` estimado (1 por cada 1 500 caracteres en perfiles
  con ejercicios). Son valores iniciales: se calibran con la primera corrida real.
- **Explorador**, pestaña de preguntas: cada pregunta muestra su **tipo**, su **cita** y
  sus **motivos** si está en `needs_review`. La cobertura por nodo no cambia.

## 10. Contrato v2 del bundle

`bundle/spec.py` es la única implementación del contrato, compartida por el exportador y
el importador de la webapp.

| | v1 | v2 |
|---|---|---|
| `bundle_version` | 1 | 2 |
| Identidad de la pregunta | única por (`run_ref`, `node_ref`) | única por (`run_ref`, `generation_order`) |
| `question_type` | — | obligatorio: `teoria`, `ejercicio_libro`, `ejercicio_nuevo` |
| `source_quote` | — | obligatorio, texto de 1 a 2000 caracteres |
| Opciones | 1 correct, 1 confusa, 2 distractor | igual |

- El exportador escribe **v2**. `SUPPORTED_VERSIONS = {1, 2}`: el validador aplica las
  reglas de v1 a los bundles v1 y las de v2 a los v2.
- Páginas, motivos y verificación viajan en `metadata` (campo libre, ya existente).
- Se actualiza `CONTRATO-BUNDLE.md` con los cambios de la v2.

## 11. Trabajo en la webapp (lo hace el usuario)

1. Copiar el `bundle/spec.py` nuevo.
2. Postgres: cambiar el índice único de preguntas de (corrida, nodo) a (corrida,
   `generation_order`) y añadir las columnas `question_type` y `source_quote`.
3. Actualizar `docs/06-contrato-bundle-de-contenido.md`.

## 12. Organización del código

| Unidad | Responsabilidad |
|---|---|
| `qgen/windows.py` (nuevo) | `build_windows`: chunks de un nodo → ventanas (puro) |
| `qgen/prompts/families.py` (nuevo) | plantillas militar/civil, instrucción del sistema y mensaje por ventana |
| `qgen/prompts/schemas.py` | `WindowQuestion`, `WindowResponse`, `VerificationResult` |
| `qgen/gemini/generate.py` | `generate_window` y `verify_exercise` (llamadas y tokens) |
| `qgen/validation/checks.py` (nuevo) | normalizaciones, revisiones por tipo, duplicados |
| `qgen/pipeline.py` | orquestación: nodos → ventanas → llamada → validación → verificación → guardado |
| `qgen/rules/` | `familia` y `tipos` por perfil |
| `qgen/db/migration.py`, `models/schema.py` | columnas nuevas |
| `qgen/bundle/` | contrato v2 |
| `explorer/` | tipo, cita y motivos |

**Se elimina:** `prompts/creator.py`, `generate_draft_questions`/`DraftOutcome`,
`QuestionDraftList`, la plantilla de opciones de `prompts/system.py` y
`prompts/render.py` (los reemplaza `prompts/families.py`), el recorte de incisos con regex
y la revisión literal que hoy vive en `pipeline.py` (pasa a `validation/checks.py`).

## 13. Errores

- **429/503:** reintentos con espera exponencial, como hoy.
- **Respuesta de ventana ilegible o cortada:** un reintento; si vuelve a fallar, la
  ventana queda `fallida` con su motivo y la siguiente corrida la retoma.
- **Falla la verificación:** la pregunta queda `needs_review` con motivo "verificación fallida".
- **Corte de la corrida (Ctrl-C u otra excepción):** como hoy, lo ya guardado se conserva y
  la corrida se cierra `cancelled` o `failed`; las ventanas no terminadas se retoman.

## 14. Pruebas (TDD)

- **Ventanas:** deterministas; nunca mezclan nodos; respetan 4000/6000; cortan antes de
  "EJEMPLO n" y de "x.y" pasados 3000; quitan el solapamiento; chunk gigante = ventana propia.
- **Prompt:** el militar usa el título real del manual; el civil no lleva ejemplos
  militares; los tipos del perfil se reflejan en la instrucción.
- **Validación:** literal de teoría con normalización; normalización matemática
  (`x^2 − 4` = `x2 - 4`); duplicados (teoría ≥ 0.90, ejercicios idénticos); descartes y
  motivos.
- **Verificación:** otra opción, `ninguna`, `varias` o dificultad `mayor` → `needs_review`.
- **Reanudar:** se saltan ventanas `ok`; las `fallida` se reintentan; `--regenerate` ignora el historial.
- **Migración:** idempotente sobre una base con la tabla antigua.
- **Contrato:** v2 acepta varias preguntas por nodo, rechaza `generation_order` repetido en
  una corrida y exige `question_type` y `source_quote`; v1 sigue validando igual.
- **Flujo completo** con un Gemini falso: ventana → llamada → validación → guardado →
  bundle v2 válido.
- **Prueba real:** `--limit` pequeño sobre Cálculo y sobre un manual militar, revisión
  en el explorador y calibración de la estimación.

## 15. Riesgos

- **Fórmulas aplanadas** en los PDF de Word: pueden generar claves erróneas; lo mitiga la
  normalización matemática y la verificación de ejercicios nuevos.
- **"Todas las posibles"** producirá también preguntas triviales; es lo pedido. Los
  ejemplos de exámenes reales (fuera de alcance) serán la palanca de calidad.
- **Respuestas largas:** con 30 preguntas por ventana la salida ronda 10 000 tokens; si
  una ventana se corta, el reintento y la reanudación la recuperan.
- **Límites del plan gratuito:** sin caché hay 2 hilos y reintentos por 429; una corrida
  completa puede tardar horas, pero se puede reanudar.
