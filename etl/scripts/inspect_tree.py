"""Quick visual inspection of an in-memory hierarchy without persisting."""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

from etl.pipeline import run_pipeline


def main(pdf: Path, max_print: int = 50) -> None:
    summary, _, tree, chunks = run_pipeline(pdf, persist=False, use_cache=True)
    print(f"Profile: {summary.profile} (auto={summary.profile_auto_detected})")
    print(f"Pages: {summary.page_count}, nodes: {summary.node_count}, chunks: {summary.chunk_count}")
    print(f"Dropped elements: {summary.dropped_elements}")
    print(f"Unattached: {summary.unattached_elements}")
    print()

    levels = Counter(n.level_label for n in tree.nodes)
    print("Level distribution:")
    for lab, n in sorted(levels.items()):
        print(f"  {lab}: {n}")
    print()

    print(f"First {max_print} nodes (depth-first):")
    for n in sorted(tree.nodes, key=lambda x: x.sort_key)[:max_print]:
        indent = "  " * n.level
        print(f"{indent}d={n.level} [{n.level_label} {n.ordinal}] {n.title[:80]} (p.{n.page_start})")

    annotated = [n for n in tree.nodes if n.metadata.get("annotations")]
    print(f"\nNodes with metadata annotations (DOF reformas): {len(annotated)}")
    for n in annotated[:5]:
        print(f"  {n.level_label} {n.ordinal}: {n.metadata['annotations']}")


if __name__ == "__main__":
    main(Path(sys.argv[1]), max_print=int(sys.argv[2]) if len(sys.argv) > 2 else 50)
