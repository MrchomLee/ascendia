import json
from etl.pipeline import load_cached_extraction
from pathlib import Path
from etl.hierarchy.profile import get_profile
from etl.hierarchy.assembler import HierarchyAssembler

cache_path = Path("data/processed/Codigo de Justicia Militar.docling.json")
extraction = load_cached_extraction(cache_path)
profile_obj = get_profile("codigo_legal")

assembler = HierarchyAssembler(profile_obj, prefer_toc=False)
tree = assembler.assemble(extraction.elements, None)

n2 = next((n for n in tree.nodes if n.local_id==2), None)
n3 = next((n for n in tree.nodes if n.local_id==3), None)

print(f"TITULO PRIMERO (ID 2): {n2.title}")
for idx in n2.body_element_indices:
    print(f"  [{idx}] {repr(extraction.elements[idx].text)[:100]}")

print(f"\nCAPITULO I (ID 3): {n3.title}")
for idx in n3.body_element_indices:
    print(f"  [{idx}] {repr(extraction.elements[idx].text)[:100]}")
