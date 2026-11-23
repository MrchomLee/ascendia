## El proyecto

Convierte manuales y libros en PDF en preguntas de opción múltiple para la
plataforma Ruta al Ascenso. Pipeline: `etl/` (PDF → árbol de nodos y chunks),
`question_generator/` (preguntas), `explorer/` (revisor en Streamlit). Todo
persiste en `data/manuals.sqlite`. Lee el [README](README.md) antes de trabajar:
explica la instalación, cada comando y el flujo completo.

## Reglas para Claude en este repo

- **Responde en español**, también en los avances y en los mensajes de commit.
- **El repo es público.** Nunca subas a git PDFs, texto extraído de libros, la
  base `.sqlite`, bundles ni nada de `data/` (salvo los `.gitkeep`). Revisa
  `git status` antes de cada commit.
- **Las claves son personales.** La `GEMINI_API_KEY` la consigue y la escribe la
  persona en su `.env`; no la pidas por el chat ni la escribas en archivos
  versionados.
- **Haz commit, push o PR solo cuando te lo pidan.**
- **Comandos:** se corren desde la raíz con `py -3.14 -m uv run <comando>`
  (Windows) o `uv run <comando>` (macOS/Linux).
- **Pruebas por separado:** `pytest etl/tests` y `pytest question_generator/tests`.
  Juntas fallan por los `conftest.py`.
- **Respaldo antes de cargar:** antes de importar preguntas o correcciones a la
  base, copia `data/manuals.sqlite` a `data/scratch/`.
- **No entregues ni subas bundles a la webapp** sin permiso explícito.
- **No generes preguntas sin que te lo pidan:** con Gemini cuesta dinero, y sin
  API ocupa mucho trabajo.
- **Generar sin API:** `qgen-claude exportar <manual_id>` deja en
  `data/claude_code/<código>/` la instrucción y una ventana por archivo. Escribe
  cada respuesta en `respuestas/` siguiendo esa instrucción al pie de la letra y
  luego corre `qgen-claude importar <manual_id>`. La revisión
  (`exportar-revision`) y la corrección (`exportar-correccion`) funcionan igual.
- **Preguntas militares:** siguen las reglas de
  `question_generator/src/qgen/prompts/redaccion_militar.py`. Por ejemplo, el
  enunciado empieza «Conforme al …», nunca se pregunta por penas y los
  distractores salen de la misma norma. La clave no debe ser la opción más larga.
- **Árbol antes de preguntas:** si la jerarquía de un manual sale mal, se
  arregla en `etl/` antes de generar.

## graphify (opcional)

Si `graphify` está instalado (`uv tool install graphifyy`) y existe
`graphify-out/graph.json`:

- Para preguntas sobre el código, usa primero `graphify query "<pregunta>"`.
- Para relaciones, `graphify path "<A>" "<B>"`; para un concepto,
  `graphify explain "<concepto>"`.
- Lee `graphify-out/GRAPH_REPORT.md` solo para una revisión general de la
  arquitectura.
- Después de cambiar código, actualiza el grafo con `graphify update .`.

Si graphify no está instalado, busca en el código de la forma normal.

### graphify en Windows

- Desde PowerShell, `graphify update .` falla con `can't open file '...\.local\bin\graphify'`:
  el comando se relanza para fijar `PYTHONHASHSEED` y el lanzador pierde el `.exe`.
  Se evita definiendo la variable antes: `$env:PYTHONHASHSEED = "0"; graphify update .`
  (en Git Bash pasa lo mismo: `PYTHONHASHSEED=0 graphify update .`).
- Nunca `graphify update . --no-cluster` sobre el grafo versionado: reescribe `graph.json`
  sin comunidades.
