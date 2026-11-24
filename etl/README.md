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

## Libros escaneados (sin capa de texto)

`etl-ingest` no hace OCR por defecto: lee la capa de texto que trae el PDF. Un libro escaneado
se lee primero con `etl-escanear`, que deja un borrador en Markdown para revisar.

**Requisitos:**
- Windows y una tarjeta NVIDIA con CUDA. Se probó en una RTX 5070 Ti, a unos 0,6 s por recorte.
- El paquete de idioma español instalado en Windows, que trae el OCR de Windows (`es-MX`).
- El extra `escaneo` para el diccionario: `uv sync --extra escaneo`.
- La primera vez se descargan los modelos de Docling y de PaddleOCR-VL-1.5 (unos 2 GB).

```powershell
py -3.14 -m uv run etl-escanear todo data/raw_pdfs/libro.pdf --paginas 15-40
```

`todo` hace seis pasos; cada uno también se puede correr solo:

| Paso | Comando | Qué deja en `data/processed/escaneo/<libro>/` |
|---|---|---|
| 1 | `paginas` | `paginas/pNNNN.png`: la imagen del escaneo al doble (NNNN = página del PDF) |
| 2 | `maquetacion` | `maquetacion.json` (regiones de Docling) y `segmentos.json` (qué se lee y qué no) |
| 3–4 | `ocr` | `ocr_cache.json` (PaddleOCR-VL, por recorte) y `windows/pNNNN.json` (OCR de Windows) |
| 5–6 | `borrador` | `borrador.md` en orden de lectura y `dudas.txt` |

**Cómo se revisa:**
- **Las dudas.** `dudas.txt` lista las palabras que el OCR de Windows no leyó y que no están en el
  diccionario: ahí suelen estar los errores de PaddleOCR (palabras en inglés, guiones dentro de
  la palabra, letras cambiadas).
- **Mirarlas en la imagen.** `etl-escanear ver <pdf> palabra1 palabra2 …` junta en `ver.png` el
  renglón de la página donde aparece cada una.
- **Corregir la segmentación.** Si una región se leyó de más o de menos, se corrige en
  `ajustes.json`, por ejemplo `{"p0012": {"3": {"keep": false, "why": "fig"}}}`. Luego se corre
  otra vez `segmentar`, `ocr` y `borrador`; solo se leen los recortes que cambiaron.

**Lo que sigue siendo manual:** el ensamble del libro final. Incluye los folios impresos, los
niveles de título, los párrafos partidos entre páginas y las correcciones revisadas en la imagen.
Se hace sobre `borrador.md`, con ayuda de Claude. El texto final se convierte a PDF y se ingesta
con `etl-ingest --extractor pymupdf`.

Nada de `data/processed/` se sube a git: es el texto del libro.

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
