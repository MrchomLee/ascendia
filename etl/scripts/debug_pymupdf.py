"""One-off debug script: inspect characters used as TOC leaders."""
from __future__ import annotations

import sys
import unicodedata
from collections import Counter
from pathlib import Path

import pymupdf

pdf = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\Users\jgome\Downloads\Manual de Operaciones MIlitares-1-20.pdf")

doc = pymupdf.open(pdf)
target_page = 2
for i in range(min(len(doc), 6)):
    t = doc[i].get_text("text")
    print(f"page idx {i}: {len(t)} chars, first 120: {t[:120]!r}")
print()
text = doc[target_page].get_text("text")

print(f"PAGE 2 length: {len(text)}")
print(f"sample line:")
sample = "Teoría de la Guerra"
idx = text.find(sample[:8])
if idx >= 0:
    end = text.find("\n", idx)
    line = text[idx:end if end > 0 else idx + 100]
    print(f"  raw: {line!r}")
    print(f"  codepoints in middle:")
    for c in line[20:60]:
        print(f"    {c!r:6} U+{ord(c):04X}  {unicodedata.name(c, '?')}")

print("\nMost common non-alphanumeric chars on the page:")
counter = Counter(c for c in text if not c.isalnum() and not c.isspace())
for ch, n in counter.most_common(15):
    print(f"  {ch!r:6} U+{ord(ch):04X}  {n} times")
