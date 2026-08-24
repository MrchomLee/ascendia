# `explorer/` — revisor visual del pipeline

Herramienta local para inspeccionar y validar lo que producen las dos fases:
manuales ingeridos, jerarquía, chunks, TOC y elementos crudos del extractor
(fase 1), y las preguntas generadas con sus opciones (fase 2).

Es de **solo lectura con una excepción**: en la página de Preguntas se puede
marcar el `validation_status` de una pregunta. Es lo único que escribe, y
escribe solo esa columna: no borra preguntas, no dispara ingestas ni
generaciones, y no conoce la base de datos de la webapp.

## Cómo correr

Desde la raíz del workspace:

```powershell
py -3.14 -m uv run streamlit run explorer/src/explorer/Home.py
```

Abre `http://localhost:8501` automáticamente.

## Vistas

| Página | Qué muestra |
|---|---|
| **Home** | Lista de manuales ingeridos + KPIs globales |
| **📄 Manual** | Metadata + reporte de calidad + árbol jerárquico + chunks crudos |
| **🌳 Node** | Breadcrumb + chunks de un nodo + preview del PDF original |
| **📑 TOC** | Entradas del índice parseado + gaps contra los nodos creados |
| **🧱 Raw Elements** | Cache de extracción crudo con filtros por tipo y página |
| **🔍 Search** | Búsqueda full-text (FTS5) sobre el contenido de los chunks |
| **❓ Preguntas** | Preguntas con sus 6 opciones por rol, cobertura, corridas y revisión |

### El árbol y la cobertura

En **📄 Manual → Árbol**, cada nodo lleva un badge con las preguntas que
cuelgan de él: `❓3` si las tres se sirven, `❓1/3` si solo una llegaría a un
examen, y `⚠ sin pregunta` si el nodo tiene texto y nadie le generó nada. Es la
forma rápida de ver qué parte del manual está cubierta sin salir de la
jerarquía.

### La revisión

En **❓ Preguntas**, cada pregunta se muestra con su nodo de origen, las 6
opciones coloreadas por rol —correcta, confusa, dos distractores— y su
difíciles— y su justificación. Debajo hay un control para marcarla:

| Estado | ¿Se le sirve al alumno? |
|---|---|
| ⏳ `pending` — recién generada | **sí** |
| ✅ `valid` — revisada y aprobada | **sí** |
| 🔎 `needs_review` — dudosa | no |
| 🚫 `rejected` — mala | no |

Marcar no borra: una pregunta rechazada sigue en la base, viaja en el bundle y
queda constancia de que se revisó; simplemente la webapp no la mete en ningún
examen. Ese estado es el que después leen `qgen-export` y el importador.

Las otras dos pestañas son **Sin pregunta** (nodos con texto que se quedaron
fuera, o sea el trabajo pendiente del manual) y **Corridas** (cada invocación
de `qgen-generate` con su modelo, su costo y sus fallos).

## Navegación

Las páginas usan **query params** (`?manual_id=1&node_id=42`) en vez de session
state. Esto permite copiar/pegar URLs y compartir contextos exactos.
