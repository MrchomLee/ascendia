import json

with open("data/processed/Codigo de Justicia Militar.docling.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for i, el in enumerate(data["elements"][10:40]):
    idx = i + 10
    print(f"[{idx}] p.{el.get('page_number')} {el.get('kind')} | {repr(el.get('text'))[:150]}")
