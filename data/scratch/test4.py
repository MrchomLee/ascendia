import json

with open("data/processed/Codigo de Justicia Militar.docling.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for i, el in enumerate(data["elements"][:20]):
    print(f"[{i}] {el.get('kind')} | {repr(el.get('text'))[:100]}")
