## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

## graphify en Windows

- Desde PowerShell, `graphify update .` falla con `can't open file '...\.local\bin\graphify'`:
  el comando se relanza para fijar `PYTHONHASHSEED` y el lanzador pierde el `.exe`.
  Se evita definiendo la variable antes: `$env:PYTHONHASHSEED = "0"; graphify update .`
  (en Git Bash pasa lo mismo: `PYTHONHASHSEED=0 graphify update .`).
- Nunca `graphify update . --no-cluster` sobre el grafo versionado: reescribe `graph.json`
  sin comunidades.
