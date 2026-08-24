import json

with open("data/processed/Codigo de Justicia Militar.docling.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for i, el in enumerate(data["elements"][40:60]):
    idx = i + 40
    print(f"[{idx}] p.{el.get('page_number')} {el.get('kind')} | {repr(el.get('text'))[:150]}")
