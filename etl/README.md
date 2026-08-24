# `etl/` — Fase 1: extracción estructurada de manuales PDF

Procesa manuales militares en PDF y los persiste en SQLite con su jerarquía
(`PARTE → Capítulo → Sección → Subsección`) preservada para poder generar
preguntas en fases posteriores.

## Pipeline

```
PDF
 │
 ├─► [1] Registro del manual
 ├─► [2] Detector + parser de TOC       (extraction/toc_parser.py)
 ├─► [3] Extractor de layout            (extraction/{docling,unstructured}_adapter.py)
 ├─► [4] Ensamblador de jerarquía       (hierarchy/assembler.py)
 ├─► [5] Consolidador de chunks         (chunking/consolidator.py)
 └─► [6] Persistencia                   (db/ + models/schema.py)
```

## Comandos

Desde la raíz del workspace:

```powershell
# Bake-off Docling vs Unstructured sobre un PDF
py -3.14 -m uv run etl-bakeoff data/raw_pdfs/dn_m_1455.pdf

# Ingestión completa con el motor por defecto (Docling)
py -3.14 -m uv run etl-ingest data/raw_pdfs/dn_m_1455.pdf

# Inspección de la BD
py -3.14 -m uv run etl-inspect manuals
py -3.14 -m uv run etl-inspect tree <manual_id>
py -3.14 -m uv run etl-inspect node <node_id>
```

## Qué pasa después

El contenido ingestado no viaja solo: la fase 2 (`question_generator/`) genera
las preguntas sobre estos nodos, y `qgen-export` empaqueta manual + jerarquía +
preguntas en un bundle JSON que es lo que se entrega. Ver el
[README de la raíz](../README.md) y [CONTRATO-BUNDLE.md](../CONTRATO-BUNDLE.md).

## Tests

```powershell
py -3.14 -m uv run pytest etl/tests
```

## Notas sobre Unstructured y Python 3.14

Unstructured aún no declara soporte oficial para Python 3.14. Si la instalación
falla, se puede instalar como extra opcional aparte:

```powershell
py -3.14 -m uv pip install "unstructured[pdf]"
```

O correr solo el adaptador de Unstructured en un sub-entorno 3.12:

```powershell
py -3.12 -m uv run --with "unstructured[pdf]" python -m etl.cli.bakeoff ...
```
