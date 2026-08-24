import json

# Mostrar todos los elementos de página 2 en orden, para ver el contexto completo
with open("data/processed/Codigo de Justicia Militar.docling.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("=== Todos los elementos entre índice 46 y 65 ===\n")
for i in range(46, 66):
    el = data["elements"][i]
    print(f"[{i}] p.{el.get('page_number')} {el.get('kind'):12s} | {repr(el.get('text',''))[:130]}")
