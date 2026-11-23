"""High-level pipeline orchestration.

Glues extraction → TOC → hierarchy → chunking → persistence into one entry
point. The CLI commands are thin wrappers around `run_pipeline`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from etl.chunking.consolidator import ChunkConsolidator, ConsolidatedChunk
from etl.db.persistence import persist_manual
from etl.db.session import session_scope
from etl.extraction.base import ExtractorBase
from etl.extraction.toc_parser import TocResult, parse_toc
from etl.extraction.types import ExtractionResult
from etl.hierarchy.assembler import HierarchyAssembler, HierarchyTree
from etl.hierarchy.profile import (
    DocumentProfile,
    auto_detect_profile,
    get_profile,
)


ExtractorName = Literal["docling", "unstructured"]


class PipelineResult(BaseModel):
    extractor: str
    page_count: int
    elapsed_seconds: float
    toc_found: bool
    toc_entries: int
    node_count: int
    chunk_count: int
    unattached_elements: int
    profile: str
    profile_auto_detected: bool
    dropped_elements: int = 0
    manual_id: int | None = None


def get_extractor(name: ExtractorName, *, do_ocr: bool = False) -> ExtractorBase:
    if name == "docling":
        from etl.extraction.docling_adapter import DoclingAdapter

        return DoclingAdapter(do_ocr=do_ocr)
    if name == "unstructured":
        from etl.extraction.unstructured_adapter import UnstructuredAdapter

        return UnstructuredAdapter()
    raise ValueError(f"Unknown extractor: {name}")


def cache_extraction(result: ExtractionResult, cache_path: Path) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    payload = result.model_dump(mode="json")
    cache_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def load_cached_extraction(cache_path: Path) -> ExtractionResult | None:
    if not cache_path.exists():
        return None
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        return ExtractionResult.model_validate(data)
    except Exception:
        return None


def run_pipeline(
    pdf_path: Path,
    *,
    extractor_name: ExtractorName = "docling",
    code: str | None = None,
    title: str | None = None,
    edition: str | None = None,
    branch: str | None = None,
    persist: bool = True,
    use_cache: bool = True,
    processed_dir: Path | None = None,
    do_ocr: bool = False,
    profile: str | None = None,
) -> tuple[PipelineResult, ExtractionResult, HierarchyTree, list[ConsolidatedChunk]]:
    """Run the full pipeline on a single PDF.

    Returns the summary plus the intermediate artifacts (extraction result,
    hierarchy tree, chunks) so callers like the bake-off can compare without
    re-running the heavy extraction.

    Parameters
    ----------
    profile
        DocumentProfile name ("manual", "codigo_legal", "ley_organica", …).
        If ``None``, the profile is auto-detected from the first elements.
    """
    processed_dir = processed_dir or Path("data/processed")
    cache_path = processed_dir / f"{pdf_path.stem}.{extractor_name}.json"

    extraction: ExtractionResult | None = (
        load_cached_extraction(cache_path) if use_cache else None
    )
    if extraction is None:
        extractor = get_extractor(extractor_name, do_ocr=do_ocr)
        extraction = extractor.extract(pdf_path)
        if use_cache:
            cache_extraction(extraction, cache_path)

    profile_obj: DocumentProfile
    profile_auto = False
    if profile:
        profile_obj = get_profile(profile)
    else:
        detected = auto_detect_profile(extraction.elements)
        profile_obj = get_profile(detected)
        profile_auto = True

    toc: TocResult = parse_toc(pdf_path)
    tree: HierarchyTree = HierarchyAssembler(profile_obj, prefer_toc=False).assemble(
        extraction.elements, toc
    )
    chunks = ChunkConsolidator(
        max_chars=2500,
        soft_target=2100,
        overlap=200,
        merge_under_chars=0 if profile_obj.name in ("codigo_legal", "ley_organica", "algebra_baldor") else 500
    ).consolidate(tree, extraction.elements)

    summary = PipelineResult(
        extractor=extraction.extractor_name,
        page_count=extraction.page_count,
        elapsed_seconds=extraction.elapsed_seconds,
        toc_found=toc.found,
        toc_entries=len(toc.entries),
        node_count=len(tree.nodes),
        chunk_count=len(chunks),
        unattached_elements=len(tree.unattached_element_indices),
        profile=profile_obj.name,
        profile_auto_detected=profile_auto,
        dropped_elements=tree.dropped_element_count,
    )

    if persist:
        manual_code = code or _guess_code(pdf_path)
        manual_title = title or _guess_title(pdf_path)
        with session_scope() as session:
            manual = persist_manual(
                session,
                code=manual_code,
                title=manual_title,
                edition=edition,
                branch=branch,
                source_path=pdf_path,
                page_count=extraction.page_count,
                extractor_used=extraction.extractor_name,
                tree=tree,
                chunks=chunks,
                extra_metadata={
                    "toc_confidence": toc.confidence,
                    "toc_entries": len(toc.entries),
                    "profile": profile_obj.name,
                    "profile_auto_detected": profile_auto,
                    "dropped_elements": tree.dropped_element_count,
                },
            )
            session.flush()
            summary = summary.model_copy(update={"manual_id": manual.id})

    return summary, extraction, tree, chunks


_CODE_RE = re.compile(r"\b(DN\s*M\s*\d{3,5}|D[A-Z]{1,3}\s*\d{3,5})\b", re.IGNORECASE)


def _guess_code(pdf_path: Path) -> str:
    if m := _CODE_RE.search(pdf_path.stem):
        return re.sub(r"\s+", " ", m.group(1).upper())
    return pdf_path.stem


def _guess_title(pdf_path: Path) -> str:
    return pdf_path.stem.replace("_", " ").replace("-", " ").strip()
