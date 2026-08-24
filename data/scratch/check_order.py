import json

# Revisar el orden de los elementos extraídos alrededor del Artículo 4
with open("data/processed/Codigo de Justicia Militar.docling.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("=== Elementos alrededor de Art 4 y 5 (buscando II y V desplazados) ===\n")
for i, el in enumerate(data["elements"]):
    text = el.get("text", "")
    if any(k in text for k in ["Artículo 3o", "Artículo 4o", "Artículo 5o", 
                                 "II.Ser mayor", "V.Ser de notoria",
                                 "II.- Ser mayor", "V.- Ser de notoria",
                                 "I.Ser mexicano", "III.Ser abogado", "IV.Acreditar"]):
        print(f"[{i}] p.{el.get('page_number')} {el.get('kind')} | {repr(text)[:120]}")
