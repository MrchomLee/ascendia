# Niveles cognitivos en la generación de preguntas (qgen v3)

**Fecha:** 2026-09-25 · **Rama:** `feat/qgen-ventanas` · **Estado:** propuesta para revisión

## 1. Contexto

Hoy `qgen` genera, por ventana de texto, preguntas de tipo `teoria` (clave literal) y, en los
libros de matemáticas, `ejercicio_libro` y `ejercicio_nuevo`. Todas las de teoría son, en la
práctica, preguntas de **recordar un dato**.

El usuario quiere cuatro **niveles cognitivos**: conocimiento, comprensión, análisis y
aplicación. Entregó 16 ejemplos (`datapreguntashistoria.xlsx`, una hoja por nivel) basados
en *Geografía Moderna de México* (`Geografia_Moderna_de_Mexico_extraccion.pdf`). Al
contrastarlos con el PDF:

| Nivel | Ejemplos | ¿La correcta es literal? | Qué hace la pregunta |
|---|---|---|---|
| Conocimiento | 5 | Sí (4 exactas, 1 casi) | Pide un dato; las incorrectas suelen ser otros datos reales del texto |
| Comprensión | 4 | 2 de 4; las otras, paráfrasis | Explica un proceso (la costa avanza por los depósitos del Grijalva y el Usumacinta) |
| Análisis | 3 | No | Deduce cruzando datos ("cinco veces menor que Canadá…" → quinto lugar) |
| Aplicación | 4 | No | Caso inventado (topógrafos, comisión binacional) resuelto con un concepto del texto |

Consecuencia: la regla "la clave es copia literal" solo vale para conocimiento.

## 2. Decisiones del usuario

1. Cuatro niveles en **todos los libros**, también los militares.
2. **Proporción fija 55/15/15/15** (conocimiento / comprensión / análisis / aplicación).
3. **Validación:** cita literal obligatoria (comprobada en automático) + la revisión juzga
   que la clave se sostenga; sin llamadas extra.
4. La **webapp recibe el nivel** en el bundle (contrato v3); el usuario adapta la webapp.
5. **Enfoque 1:** un campo nuevo `nivel`, junto al `tipo` actual; una sola llamada por ventana.
6. **Enunciados directos:** sin "Según el texto…", aunque los ejemplos lo usen.
7. Las definiciones de cada nivel son las del usuario (§4).

## 3. Alcance

**Dentro:** campo `nivel` en la respuesta, la base y el bundle; definiciones de nivel en el
prompt; proporción y tope; ejemplos por nivel (importador xlsx); revisión automática por
nivel; nivel y reclasificación en la revisión con Claude; clasificación de las preguntas
existentes; explorador; CLI; contrato v3; prueba piloto con Geografía.

**Fuera:** adaptar la webapp a la v3 (la hace el usuario, §10); ejemplos propios de los
manuales militares (se importan después con el mismo comando); proveedor por API de pago;
verificación a ciegas de los niveles de razonamiento.

## 4. Los niveles (definiciones del usuario)

Estas definiciones viven en **un solo lugar** (`qgen/prompts/niveles.py`) y las usan el
prompt de generación (§6) y la rúbrica de revisión (§8). La "Clave (A)" es la opción
`correct`; el "Distractor (B)", la `confusa`.

**1. Conocimiento (Recordar)**
- Definición cognitiva: evocación directa de datos, hechos, fechas, clasificaciones o
  definiciones explícitas.
- Sintaxis: directa. "¿Qué?", "¿Quién?", "¿Cuándo?", "¿Cuál es la definición de…?"
- Clave: copia LITERAL y exacta del texto.
- Distractor B: la misma oración literal, cambiando un nombre propio, una cifra, un
  elemento de la lista o una unidad de medida.
- Filtro anti-falsos positivos: si la pregunta requiere que el alumno explique con sus
  palabras, deduzca o analice un caso, no es conocimiento. Aquí solo se escanea y recupera
  información textual.

**2. Comprensión (Entender / Explicar / Traducir)**
- Definición cognitiva: demostrar entendimiento del significado explícito de una idea o
  proceso. No pide un dato aislado: reformular, explicar o resumir un fenómeno con
  fidelidad conceptual.
- Sintaxis: "¿Cómo se describe el proceso de…?", "¿Qué significa la expresión…?", "En otras
  palabras, el concepto X se refiere a…"
- Clave: una PARÁFRASIS precisa; dice exactamente lo mismo que el texto, con otras palabras.
- Distractor B: alteración del núcleo explicativo: se invierte el verbo principal, el
  adjetivo descriptivo o la dirección del proceso ("aumenta" por "disminuye", "cóncavo" por
  "convexo"). Suena lógico pero es conceptualmente falso.
- Filtro: si la pregunta se responde copiando literalmente una definición del texto, es de
  conocimiento. Para ser comprensión debe obligar a identificar la traducción o explicación
  del concepto, no su memorización.

**3. Aplicación (Usar reglas en casos nuevos)**
- Definición cognitiva: uso de un método, regla, fórmula o criterio explícito del texto para
  resolver una situación inédita.
- Sintaxis: plantea un CASO INVENTADO (un equipo hipotético, una comisión nueva, un
  comandante en una situación específica): "El Teniente X se encuentra en la situación Y.
  ¿Qué procedimiento debe aplicar?"
- Clave: la solución o el procedimiento exacto que dicta el texto, aplicado al caso.
- Distractor B: una solución que aplica la regla al revés, usa la herramienta equivocada o
  aplica la regla de una excepción en lugar de la regla general.
- Filtro: si la pregunta dice "¿Qué pasa cuando se aplica la regla X?", es de conocimiento o
  comprensión. Es OBLIGATORIO inventar un escenario que no está en el texto, cuya solución se
  extrae de las reglas del texto.

**4. Análisis (Deducir / Inferir / Relacionar)**
- Definición cognitiva: extraer conclusiones, comparar datos o inferir información que no
  está escrita explícitamente, pero que es lógicamente innegable al sumar los datos del texto.
- Sintaxis: "¿Qué se puede deducir sobre…?", "Al comparar X con Y, es correcto afirmar
  que…", "¿Qué conclusión subyacente establece el autor sobre…?"
- Clave: una CONCLUSIÓN INFERIDA (si el texto dice "A tiene 10 metros y B tiene 50", la
  clave dice "A es cinco veces menor que B").
- Distractor B: una deducción lógicamente inválida, una falsa correlación causa-efecto o la
  inversión de las variables ("B es cinco veces menor que A").
- Filtro: si la respuesta empieza con un "Porque…" que está literal en el texto, es de
  comprensión. La respuesta NO debe estar escrita textualmente: es una conclusión
  matemática, lógica o comparativa que el alumno construye cruzando datos del pasaje citado.

**Adaptaciones al integrarlas:**
- **Distractores C y D** (no los define el texto del usuario): en conocimiento, otros datos
  reales del mismo texto, como en los ejemplos; en los otros niveles, respuestas plausibles
  del mismo tema que fallan de otra manera que la confusa.
- **Sin "según el texto/manual"** en la familia civil (decisión 6). En la militar, el prefijo
  "Conforme al Manual …, <Ruta>, ¿…?" ya cumple esa función. Por lo mismo, la sintaxis de
  comprensión "¿Cómo describe el texto el proceso de…?" queda como "¿Cómo se describe el
  proceso de…?".
- **Orden en el prompt:** conocimiento, comprensión, aplicación, análisis (el del usuario).

## 5. Modelo de datos

**Respuesta de la generación.** `WindowQuestion` gana
`nivel: Literal["conocimiento", "comprension", "analisis", "aplicacion"]` (obligatorio).
Los valores van sin acentos; las etiquetas de pantalla los llevan. Un `ejercicio_libro` o
`ejercicio_nuevo` siempre es `aplicacion`: si llega con otro nivel se corrige en la
validación del esquema, sin descartarlo.

**Base de datos** (migración idempotente, como la de v2):
- `questions.cognitive_level` `String(16)`, nullable. `NULL` = sin clasificar (las
  preguntas anteriores a esta versión).
- `reference_questions.cognitive_level` `String(16)`, nullable, para elegir un ejemplo por
  nivel.

**Metadatos de la pregunta** (`metadata_json`):
- `revision.nivel`: el nivel que asignó la revisión con Claude.
- `nivel_generado`: el nivel que declaró la generación, cuando la revisión lo cambió.

## 6. Generación

**Prompt.** Nueva sección `NIVELES` con las cuatro definiciones de §4 y las adaptaciones;
las reglas de `CALIDAD` siguen valiendo para todos los niveles. `SYSTEM_VERSION` pasa a
`2026-09-25.v7`.

**Proporción.** Se generan **todas** las preguntas de conocimiento que el texto permita
(como hoy) y, sobre esa base `K`, las de los otros niveles: cada uno
`round(K × 15 / 55)`, con mínimo 1 si `K ≥ 3`. Con `K < 3`, los otros niveles son
opcionales ("si el texto lo permite"). Los ejercicios de matemáticas van **por fuera** de la
proporción (uno por ejemplo resuelto más uno nuevo, como hoy) y cuentan como aplicación.

**Tope.** `MAX_PREGUNTAS_POR_VENTANA` pasa de 30 a **45**: con 30, la proporción recortaría
las de conocimiento que hoy ya se sacan. El tope cuenta todas las preguntas de la
ventana, ejercicios incluidos. La estimación de costo ajusta
`CHARS_PER_QUESTION` de 350 a 190 (≈ 20/11 veces más preguntas por ventana).

**Desvíos.** No se descarta nada por proporción. La corrida guarda en `metadata_json` el
conteo por nivel de cada ventana y el total (`niveles`), y el resumen del CLI muestra la
proporción real contra la meta y las ventanas con `K ≥ 3` a las que les faltó algún nivel.

**Ejemplos por nivel.** El prompt incluye **un ejemplo por nivel**, marcado como *modelo de
forma, no de contenido* y con la instrucción de no copiarlo. Se eligen, por nivel, del
mismo manual; si no hay, del perfil; si no, globales (el de menor id, para que el prompt sea
determinista). Si no hay ninguna referencia, la familia militar conserva sus ejemplos de
siempre.

**Importador xlsx.** `qgen-import-examples` acepta `.xlsx`: una hoja por nivel (el nombre de
la hoja da el nivel: "Conocimiento", "Comprension", "Analisis", "Aplicacion", con o sin
acento), fila de encabezado con "Pregunta", y columnas *Respuesta correcta* → `correct`,
*Respuesta similar* → `confusa`, *Respuesta incorrecta* ×2 → `distractor`. Limpieza al
importar: se quitan las marcas `[cite: …]`; los inicios "De acuerdo con la información del
texto,", "Según el texto,", "A partir del texto," (y variantes finales ", según el texto")
y se recapitaliza la primera letra tras "¿". Los 16 ejemplos entran con `--profile global`.

**Por familia.** Militar: los cuatro niveles con el prefijo "Conforme al …"; los casos de
aplicación en contexto militar. Civil: enunciados directos.

## 7. Revisión automática por nivel

`review()` (en `validation/checks.py`) pasa a depender del nivel en las preguntas de teoría.
En los cuatro niveles, la **cita** debe ser literal ("cita no encontrada" si no).

| Nivel | Comprobación | Motivo |
|---|---|---|
| Conocimiento | La clave debe ser literal | "respuesta parafraseada" (como hoy) |
| Comprensión, análisis, aplicación | La clave **no** debe ser literal, si tiene 6 palabras o más | "la clave es literal: por su forma es conocimiento" |
| Aplicación | Más de la mitad del enunciado no debe estar copiada del texto | "el caso no es inventado" |

- "Literal" es la misma función de hoy (`norm_text` o `norm_math`). El umbral de 6 palabras
  evita falsos positivos con frases cortas que aparecen por coincidencia.
- "Copiado": el bloque literal más largo compartido entre el enunciado y el texto de la
  ventana (ambos normalizados) supera la mitad del enunciado.
- Los ejercicios de matemáticas no cambian de revisión.
- Cualquier motivo deja la pregunta en `needs_review`, como hoy.

## 8. Revisión con Claude y clasificación

**Rúbrica.** Incluye las definiciones de §4 y pide clasificar cada pregunta. Criterios de
rechazo nuevos, además de los cinco actuales:
- comprensión con paráfrasis infiel al texto;
- análisis con una conclusión que no es lógicamente innegable;
- aplicación con un caso que no se resuelve con la regla citada.

**Veredicto.** Gana `nivel` (obligatorio en la revisión completa). Si difiere del
declarado, la pregunta **se reclasifica, no se rechaza**: `cognitive_level` toma el nivel
de la revisión y `metadata_json["nivel_generado"]` guarda el declarado.

**Qué exporta `exportar-revision`:**
- preguntas sin decidir (`pending`, `needs_review`) sin revisión previa → **revisión
  completa** (veredicto, calificación, nivel);
- cualquier pregunta con `cognitive_level` nulo, aunque esté decidida (p. ej. las 245 del
  Taller) → **solo clasificar**, marcada así en el lote.

El lote muestra el nivel declarado y los motivos de la revisión automática.

**Qué aplica `importar-revision`:**
- Pregunta sin decidir: exige `veredicto`, `calificacion` y `nivel`; si falta el veredicto se
  omite con el motivo "falta el veredicto".
- Pregunta decidida: solo pone el nivel si estaba nulo; **nunca cambia su estado** (si trae
  veredicto, se ignora y se reporta "ya decidida: solo se clasificó").
- El resumen cuenta aceptadas, rechazadas, dudosas, **reclasificadas** y **solo
  clasificadas**.

## 9. Contrato v3 del bundle

- `BUNDLE_VERSION = 3`; `SUPPORTED_VERSIONS = {1, 2, 3}`; v1 y v2 se siguen validando.
- En v3 cada pregunta lleva `cognitive_level` (la clave es obligatoria): uno de
  `conocimiento`, `comprension`, `analisis`, `aplicacion`, o `null` solo para las
  generadas antes de los niveles y aún sin clasificar.
- La identidad de las preguntas no cambia respecto a v2.
- `qgen-export` avisa cuántas preguntas van sin clasificar.
- `CONTRATO-BUNDLE.md` documenta la v3 en su historial.

## 10. Trabajo en la webapp (lo hace el usuario)

Aceptar bundles v3, agregar la columna del nivel (nullable) y, si quiere, filtrar o armar
exámenes por nivel. Copiar el `spec.py` actualizado, como con la v2.

## 11. Explorador y CLI

**Explorador:**
- Cada pregunta muestra su nivel junto al tipo ("📘 Teoría · Análisis"); si la revisión lo
  cambió: "Análisis (generada como comprensión)".
- Filtro por nivel, con "sin clasificar".
- Indicadores: cantidad por nivel y porcentaje real contra la meta 55/15/15/15.

**CLI:**
- `qgen-generate` y `qgen-claude importar`: tabla de proporción real por nivel contra la
  meta y ventanas sin algún nivel.
- `qgen-claude importar-revision`: cuenta reclasificadas y solo clasificadas.
- `qgen-import-examples`: soporte xlsx (§6).
- `qgen-export`: bundle v3 y aviso de sin clasificar.

## 12. Organización del código

| Módulo | Cambio |
|---|---|
| `qgen/prompts/niveles.py` (nuevo) | niveles, etiquetas, definiciones (§4) y proporción |
| `qgen/prompts/schemas.py` | `WindowQuestion.nivel`; ejercicios → aplicación; tope 45 |
| `qgen/prompts/families.py` | sección NIVELES, proporción, ejemplos por nivel, `SYSTEM_VERSION` |
| `qgen/validation/checks.py` | `review()` por nivel (§7) |
| `qgen/models/schema.py`, `models/reference_schema.py`, `db/migration.py` | columnas `cognitive_level` |
| `qgen/db/persistence.py`, `pipeline.py` | guardar el nivel; conteo por nivel en la corrida |
| `qgen/reference/importer.py`, `reference/repository.py` | xlsx y limpieza; ejemplos por nivel |
| `qgen/claude_review.py` | rúbrica con niveles, veredicto con nivel, solo clasificar |
| `qgen/cost.py` | `CHARS_PER_QUESTION` |
| `qgen/bundle/spec.py`, `bundle/build.py`, `CONTRATO-BUNDLE.md` | contrato v3 |
| `qgen/cli/*` | resúmenes por nivel |
| `explorer/…/questions_access.py`, página de Preguntas | nivel, filtro e indicadores |

## 13. Pruebas (TDD)

- Esquema: `nivel` obligatorio; ejercicios corregidos a aplicación.
- Prompt: definiciones en ambas familias, proporción y tope; un ejemplo por nivel con la
  prioridad manual → perfil → global; ejemplos militares solo sin referencias.
- `review()`: clave literal exigida en conocimiento y señalada en los otros niveles (con el
  umbral de 6 palabras); caso copiado en aplicación; ejercicios sin cambio.
- Importador: el xlsx de 4 hojas da 16 referencias con su nivel; limpieza de `[cite]` y de
  "según el texto".
- Pipeline e importación de Claude Code: el nivel se guarda; conteo por nivel en la corrida;
  aviso de ventanas sin algún nivel.
- Revisión con Claude: nivel obligatorio; reclasificación con `nivel_generado`; "solo
  clasificar" no toca el estado; falta de veredicto en una sin decidir.
- Bundle: v3 valida `cognitive_level` (incluido `null`); v2 sigue válido.
- Migración idempotente; explorador muestra el nivel y filtra.

## 14. Prueba piloto

1. Importar los 16 ejemplos del xlsx (`--profile global`).
2. Generar con Claude Code **5 ventanas de Geografía (manual 11)** de las secciones que
   cubren los ejemplos (coordenadas y límites, Sierra Madre Occidental, costas, islas); se
   eligen al planear.
3. Revisión con Claude y medición: proporción real, reclasificadas y rechazadas por nivel.
4. Si sale bien: clasificar las 245 preguntas del Taller y seguir con el resto de Geografía.

## 15. Riesgos

| Riesgo | Mitigación |
|---|---|
| El modelo copia los ejemplos (en el piloto, del mismo libro) | "modelo de forma, no de contenido; no lo copies"; la revisión rechaza copias |
| La proporción no se respeta | se mide y reporta por ventana; se ajusta el prompt con los datos del piloto |
| Falsos positivos de "clave literal" | umbral de 6 palabras; el motivo deja la pregunta a revisar, no la descarta |
| Clasificar las mías con mis propias reglas (sesgo) | la reclasificación guarda ambos niveles; el usuario revisa al azar |
| Más preguntas por ventana → más salida por llamada | tope 45; con Gemini, ~16k tokens de salida por ventana, dentro del límite |
