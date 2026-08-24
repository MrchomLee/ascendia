"""Inspect a cached docling extraction to find LIBRO/TITULO lines and Latin-suffix articles."""
from __future__ import annotations

import json
from pathlib import Path

cache = Path("data/processed/cjm_codigo_justicia_militar.docling.json")
data = json.loads(cache.read_text(encoding="utf-8"))
els = data["elements"]
print(f"Total elements: {len(els)}\n")

print("Elements containing LIBRO/TITULO at start (truncated to text < 60 chars):")
for e in els:
    t = e["text"].strip()
    upper = t.upper()
    if (upper.startswith("LIBRO ") or upper.startswith("TITULO ") or upper.startswith("TÍTULO ")) and len(t) < 80:
        print(f'  p.{e["page_number"]} kind={e["kind"]} text={t!r}')
print()

print("Article lines with Latin suffixes (Sextus/Septimus/Quintus/Quáter/Sexies/etc.):")
suffixes = ["Sextus", "Septimus", "Quintus", "Quáter", "Quater", "Sexies", "Septies", "Octies", "Nonies", "Decies", "Octavus", "Nonus"]
for e in els[:5000]:
    t = e["text"]
    if "rticulo" in t[:15] and any(s in t[:50] for s in suffixes):
        print(f'  p.{e["page_number"]} text={t[:120]!r}')
