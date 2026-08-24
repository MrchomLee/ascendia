from etl.pipeline import load_cached_extraction
from pathlib import Path
from etl.hierarchy.profile import get_profile
from etl.hierarchy.assembler import HierarchyAssembler

cache_path = Path("data/processed/Codigo de Justicia Militar.docling.json")
extraction = load_cached_extraction(cache_path)
profile_obj = get_profile("codigo_legal")

assembler = HierarchyAssembler(profile_obj, prefer_toc=False)
tree = assembler.assemble(extraction.elements, None)

for n in tree.nodes[:5]:
    print(f"NODE {n.local_id}: {n.level_label} {n.title}")
    print(f"  Body indices: {n.body_element_indices}")
