# `question_generator/` — Fase 2: generación de preguntas con Gemini

Genera preguntas de examen sobre los nodos-hoja con contenido de cada manual
ingestado por la ETL. Cada pregunta incluye 6 opciones con roles diferenciados
(1 correcta + 1 confusa + 2 distractores)
y una justificación, todo en una sola llamada por nodo.

## Modos de ejecución

- **immediate** (default): cada llamada a Gemini espera respuesta y persiste.
- **batch** (`--batch`): submit de un job único, polling separado para parsear
  resultados. ~50% más barato, hasta 24h de espera.

Ambos comparten el mismo cache explícito por documento (PDF + system instruction
+ reglas) — Gemini solo paga input completo en la primera llamada del documento.

## Comandos

```powershell
# Estimar costo antes de correr
py -3.14 -m uv run qgen-generate <manual_id> --dry-run

# Generar todas las preguntas faltantes (immediate)
py -3.14 -m uv run qgen-generate <manual_id>

# Solo las primeras 5 (dev)
py -3.14 -m uv run qgen-generate <manual_id> --limit 5

# Un nodo específico
py -3.14 -m uv run qgen-generate <manual_id> --node-id <id>

# Pro model + batch
py -3.14 -m uv run qgen-generate <manual_id> --model pro --batch

# Re-generar todas (sobreescribe)
py -3.14 -m uv run qgen-generate <manual_id> --regenerate

# Estado de batches en curso / específico
py -3.14 -m uv run qgen-batch-status
py -3.14 -m uv run qgen-batch-status <run_id>

# Inspeccionar resultado
py -3.14 -m uv run qgen-inspect <question_id>
py -3.14 -m uv run qgen-stats <manual_id>
```

## Entregar un manual

`qgen-export` empaqueta un manual en un bundle JSON autocontenido: es lo que se
entrega a quien opera la webapp, en vez de pasarle `data/manuals.sqlite`.

```powershell
# Valida contra el contrato sin escribir nada
py -3.14 -m uv run qgen-export <manual_id> --check

# Escribe data/bundles/{codigo}--{fecha}--v{n}.json + su .sha256
py -3.14 -m uv run qgen-export <manual_id>

# Una sola corrida (repetible), o con la respuesta cruda de Gemini
py -3.14 -m uv run qgen-export <manual_id> --run <run_id>
py -3.14 -m uv run qgen-export <manual_id> --include-raw
```

El formato está especificado en
[`CONTRATO-BUNDLE.md`](../CONTRATO-BUNDLE.md)
e implementado en `src/qgen/bundle/spec.py`, el mismo módulo que usa el
importador del otro lado. El exportador valida **antes** de escribir y aborta si
algo no cuadra: es mejor no entregar que entregar roto.

## Configuración

Necesita `GEMINI_API_KEY` en `.env` (raíz del workspace).

## Tests

```powershell
py -3.14 -m uv run pytest question_generator/tests
```
