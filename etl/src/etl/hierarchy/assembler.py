"""Build a manual's hierarchy tree from extracted elements + optional TOC.

Approach
--------
1. If the TOC was successfully parsed, use it as the **canonical skeleton**:
   create one node per TOC entry, in TOC order, using TOC depth.
2. Walk the body elements and attach narrative text to the nearest preceding
   node based on page numbers and proximity.
3. If no TOC, fall back to scanning body elements for headings using the
   active :class:`DocumentProfile`. Subsections that arrive without a parent
   Sección are tolerated and attached to whatever the previous heading was.
4. Anexos form a parallel branch under the Manual root.

The output is a flat list of HierarchyNode + parent-child links, easy to
persist as adjacency-list rows in SQLite.

The :class:`DocumentProfile` decides:
    - which heading kinds are detected (manual vs codigo_legal vs …)
    - what depth each kind sits at
    - which body elements are dropped as noise (headers/footers)
    - what metadata (e.g. DOF reform dates) to lift off the body
"""

from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import BaseModel, Field

from etl.extraction.toc_parser import TocResult
from etl.extraction.types import ElementKind, RawElement
from etl.hierarchy.patterns import HeadingMatch, KIND_LABELS
from etl.hierarchy.profile import DocumentProfile, PROFILES


class HierarchyNode(BaseModel):
    local_id: int
    parent_local_id: int | None = None
    level: int
    level_label: str
    ordinal: str
    title: str
    breadcrumb: str
    page_start: int
    page_end: int | None = None
    sort_key: str
    is_anexo: bool = False
    body_element_indices: list[int] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class HierarchyTree(BaseModel):
    nodes: list[HierarchyNode]
    root_ids: list[int]
    unattached_element_indices: list[int] = Field(default_factory=list)
    profile_name: str | None = None
    dropped_element_count: int = 0


@dataclass
class _Builder:
    nodes: list[HierarchyNode] = field(default_factory=list)
    stack: list[HierarchyNode] = field(default_factory=list)
    next_id: int = 0
    sort_counters: list[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])

    def add(
        self,
        match: HeadingMatch,
        title: str,
        page: int,
    ) -> HierarchyNode:
        level = match.level if not match.is_anexo else 0
        while self.stack and self.stack[-1].level >= level and not match.is_anexo:
            self.stack.pop()
        if match.is_anexo:
            self.stack.clear()

        parent = self.stack[-1] if self.stack else None
        while len(self.sort_counters) <= level:
            self.sort_counters.append(0)
        self.sort_counters[level] += 1
        for i in range(level + 1, len(self.sort_counters)):
            self.sort_counters[i] = 0
        sort_key = ".".join(f"{c:02d}" for c in self.sort_counters[: level + 1])

        breadcrumb_parts = [n.breadcrumb for n in self.stack[-1:]]
        prefix = breadcrumb_parts[0] + " › " if breadcrumb_parts else ""
        own_label = f"{match.level_label} {match.ordinal}".strip()
        full_label = own_label + (f" — {title}" if title else "")
        breadcrumb = prefix + full_label

        node = HierarchyNode(
            local_id=self.next_id,
            parent_local_id=parent.local_id if parent else None,
            level=level,
            level_label=match.level_label,
            ordinal=match.ordinal,
            title=title,
            breadcrumb=breadcrumb,
            page_start=page,
            sort_key=sort_key,
            is_anexo=match.is_anexo,
        )
        self.next_id += 1
        self.nodes.append(node)
        self.stack.append(node)
        return node


class HierarchyAssembler:
    """Assembles a tree from raw elements, optionally guided by a TOC.

    Parameters
    ----------
    profile
        Active document profile. Drives heading classification, drop
        filtering and metadata extraction. If ``None`` we use the
        ``"manual"`` profile by default (back-compat with older callers).
    prefer_toc
        When True, a successfully parsed TOC overrides body-driven detection.
    """

    def __init__(
        self,
        profile: DocumentProfile | None = None,
        *,
        prefer_toc: bool = True,
    ) -> None:
        self.profile = profile or PROFILES["manual"]
        self.prefer_toc = prefer_toc

    def assemble(
        self,
        elements: list[RawElement],
        toc: TocResult | None = None,
    ) -> HierarchyTree:
        kept_elements, kept_indices, dropped = self._filter_dropped(elements)

        if toc and toc.found and self.prefer_toc:
            tree = self._assemble_with_toc(kept_elements, kept_indices, toc)
        else:
            tree = self._assemble_from_body(kept_elements, kept_indices)

        tree.profile_name = self.profile.name
        tree.dropped_element_count = dropped
        return tree

    # ---- filtering ---------------------------------------------------------

    def _filter_dropped(
        self, elements: list[RawElement]
    ) -> tuple[list[RawElement], list[int], int]:
        kept: list[RawElement] = []
        indices: list[int] = []
        dropped = 0
        for i, el in enumerate(elements):
            if hasattr(self.profile, "clean_text"):
                el.text = self.profile.clean_text(el.text)
                
            if not el.text.strip():
                dropped += 1
                continue
                
            if self.profile.is_dropped_text(el.text):
                dropped += 1
                continue
            kept.append(el)
            indices.append(i)
        return kept, indices, dropped

    # ---- body-only assembly -----------------------------------------------

    def _assemble_from_body(self, elements: list[RawElement], indices: list[int]) -> HierarchyTree:
        builder = _Builder()
        unattached: list[int] = []

        for list_idx, el in enumerate(elements):
            orig_idx = indices[list_idx]
            if el.kind in (ElementKind.PAGE_HEADER, ElementKind.PAGE_FOOTER, ElementKind.PAGE_NUMBER):
                continue

            # Be permissive: legal-code articles often arrive as NarrativeText
            # because Docling does not visually treat "Artículo 1o.-" as a heading.
            match = self.profile.classify(el.text)

            if match:
                title = match.title_remainder
                if not title:
                    title = _peek_next_title(elements, list_idx, self.profile)
                builder.add(match, title, el.page_number)
                continue

            self._maybe_capture_metadata(el.text, builder)

            if builder.stack:
                builder.stack[-1].body_element_indices.append(orig_idx)
                builder.stack[-1].page_end = el.page_number
            else:
                unattached.append(orig_idx)

        roots = [n.local_id for n in builder.nodes if n.parent_local_id is None]
        return HierarchyTree(
            nodes=builder.nodes,
            root_ids=roots,
            unattached_element_indices=unattached,
        )

    def _assemble_with_toc(
        self,
        elements: list[RawElement],
        indices: list[int],
        toc: TocResult,
    ) -> HierarchyTree:
        builder = _Builder()

        for entry in toc.entries:
            match = self.profile.classify(entry.raw_title)
            if match is None:
                synth_level = min(entry.depth, 3)
                synth_label = _label_for_depth(self.profile, synth_level)
                match = HeadingMatch(
                    level=synth_level,
                    level_label=synth_label,
                    ordinal="",
                )
            title = match.title_remainder or _strip_known_prefix(entry.raw_title)
            builder.add(match, title, entry.page)

        offset = self._calculate_page_offset(elements, toc)
        unattached = self._attach_body_to_toc(elements, indices, builder.nodes, builder, offset)
        roots = [n.local_id for n in builder.nodes if n.parent_local_id is None]
        return HierarchyTree(
            nodes=builder.nodes,
            root_ids=roots,
            unattached_element_indices=unattached,
        )

    def _calculate_page_offset(
        self,
        elements: list[RawElement],
        toc: TocResult,
    ) -> int:
        if not toc.entries:
            return 0
            
        import string
        from collections import Counter
        def normalize(s: str) -> str:
            s = s.lower().translate(str.maketrans('', '', string.punctuation + '—·\t\n'))
            return " ".join(s.split())

        headings = [el for el in elements if el.kind == ElementKind.HEADING]
        
        offsets = []
        for entry in toc.entries[:50]:
            entry_norm = normalize(entry.raw_title)
            if not entry_norm:
                continue
            
            for h in headings:
                h_norm = normalize(h.text)
                if not h_norm:
                    continue
                if entry_norm == h_norm or entry_norm in h_norm:
                    offset = h.page_number - entry.page
                    if offset >= 0:
                        offsets.append(offset)
                        break
        if offsets:
            return Counter(offsets).most_common(1)[0][0]
        return 0

    def _attach_body_to_toc(
        self,
        elements: list[RawElement],
        indices: list[int],
        nodes: list[HierarchyNode],
        builder: _Builder,
        page_offset: int,
    ) -> list[int]:
        unattached: list[int] = []

        for list_idx, el in enumerate(elements):
            orig_idx = indices[list_idx]
            if el.kind in (ElementKind.PAGE_HEADER, ElementKind.PAGE_FOOTER, ElementKind.PAGE_NUMBER):
                continue
            
            # 1) Attempt to map by matching TOC heading
            match = self.profile.classify(el.text)
            if match:
                title = match.title_remainder
                if not title:
                    title = _peek_next_title(elements, list_idx, self.profile)
                
                # Check if this matches a TOC node
                found_node = builder.find_node_for_heading(match, title, el.page_number)
                if found_node:
                    builder.set_active(found_node)
                    continue

            # 2) Attach to active node, or fallback to page-based logic
            if builder.stack:
                builder.stack[-1].body_element_indices.append(orig_idx)
                builder.stack[-1].page_end = el.page_number
            else:
                self._maybe_capture_metadata(el.text, builder)
                
                # Fallback: find deepest node ending on/after this page
                adjusted_page = el.page_number - page_offset
                best_node = None
                for n in reversed(nodes):
                    if n.page_start <= adjusted_page:
                        if best_node is None or n.level > best_node.level:
                            best_node = n
                
                if best_node:
                    best_node.body_element_indices.append(orig_idx)
                    best_node.page_end = max(best_node.page_end or 0, el.page_number)
                else:
                    unattached.append(orig_idx)
        return unattached

    # ---- metadata ----------------------------------------------------------

    def _maybe_capture_metadata(
        self,
        text: str,
        builder: _Builder,
        target_override: HierarchyNode | None = None,
    ) -> None:
        if not self.profile.metadata_extractors:
            return
        captured = self.profile.extract_metadata(text)
        if not captured:
            return
        target = target_override or (builder.stack[-1] if builder.stack else None)
        if target is None:
            return
        bucket: list[dict[str, str]] = target.metadata.setdefault("annotations", [])
        bucket.append(captured)


def _label_for_depth(profile: DocumentProfile, depth: int) -> str:
    for kind, d in profile.kind_to_depth.items():
        if d == depth:
            return KIND_LABELS.get(kind, "Sección")
    return "Sección"


def _peek_next_title(
    elements: list[RawElement],
    idx: int,
    profile: DocumentProfile,
) -> str:
    """Look ahead up to 3 elements for something that acts as the heading title."""
    for j in range(idx + 1, min(idx + 4, len(elements))):
        candidate = elements[j].text.strip()
        if not candidate:
            continue
        # If we hit another heading of any kind, stop peeking
        if profile.classify(candidate):
            return ""
        # Don't grab long paragraphs or "Artículo..." as titles
        if len(candidate) > 200 or candidate.lower().startswith("artículo"):
            return ""
        return candidate
    return ""


def _strip_known_prefix(s: str) -> str:
    parts = s.split(maxsplit=2)
    if len(parts) >= 3 and parts[0].lower().rstrip("í") in {
        "capítulo", "capitulo", "sección", "seccion",
        "subsección", "subseccion", "anexo", "libro",
        "título", "titulo", "artículo", "articulo",
    }:
        return parts[2]
    return s
