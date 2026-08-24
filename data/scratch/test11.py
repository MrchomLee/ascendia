from etl.pipeline import load_cached_extraction
from pathlib import Path
from etl.hierarchy.profile import get_profile
from etl.hierarchy.assembler import HierarchyAssembler

cache_path = Path("data/processed/Codigo de Justicia Militar.docling.json")
extraction = load_cached_extraction(cache_path)
profile_obj = get_profile("codigo_legal")

assembler = HierarchyAssembler(profile_obj, prefer_toc=False)
kept_elements, _ = assembler._filter_dropped(extraction.elements)

for i, el in enumerate(kept_elements[20:50]):
    idx = i + 20
    print(f"[{idx}] {el.kind} | {repr(el.text)[:100]}")
