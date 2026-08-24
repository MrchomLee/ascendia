from __future__ import annotations

import time
from pathlib import Path

from etl.extraction.base import ExtractorBase
from etl.extraction.types import (
    BoundingBox,
    ElementKind,
    ExtractionResult,
    RawElement,
)


_UNSTRUCTURED_LABEL_MAP: dict[str, ElementKind] = {
    "Title": ElementKind.TITLE,
    "Header": ElementKind.PAGE_HEADER,
    "NarrativeText": ElementKind.NARRATIVE,
    "ListItem": ElementKind.LIST_ITEM,
    "Table": ElementKind.TABLE,
    "Image": ElementKind.FIGURE,
    "Figure": ElementKind.FIGURE,
    "Footer": ElementKind.PAGE_FOOTER,
    "PageBreak": ElementKind.OTHER,
    "UncategorizedText": ElementKind.OTHER,
    "FigureCaption": ElementKind.NARRATIVE,
}


class UnstructuredAdapter(ExtractorBase):
    name = "unstructured"

    def __init__(self, strategy: str = "hi_res", languages: list[str] | None = None) -> None:
        self.strategy = strategy
        self.languages = languages or ["spa", "eng"]

    def extract(self, pdf_path: Path) -> ExtractionResult:
        from unstructured.partition.pdf import partition_pdf

        start = time.perf_counter()
        elements_raw = partition_pdf(
            filename=str(pdf_path),
            strategy=self.strategy,
            languages=self.languages,
            infer_table_structure=True,
        )

        elements: list[RawElement] = []
        max_page = 0
        for el in elements_raw:
            category = type(el).__name__
            kind = _UNSTRUCTURED_LABEL_MAP.get(category, ElementKind.OTHER)
            text = (str(el) or "").strip()
            if not text and kind not in (ElementKind.TABLE, ElementKind.FIGURE):
                continue

            metadata = getattr(el, "metadata", None)
            page_number = getattr(metadata, "page_number", None) if metadata else None
            page_number = int(page_number) if page_number else 0
            max_page = max(max_page, page_number)

            coords = getattr(metadata, "coordinates", None) if metadata else None
            bbox = _coords_to_bbox(coords)

            elements.append(
                RawElement(
                    page_number=page_number,
                    physical_page_index=max(page_number - 1, 0),
                    kind=kind,
                    text=text,
                    level=None,
                    bbox=bbox,
                    metadata={"unstructured_category": category},
                )
            )

        elapsed = time.perf_counter() - start
        return ExtractionResult(
            extractor_name=self.name,
            elements=elements,
            page_count=max_page,
            elapsed_seconds=elapsed,
            warnings=[],
        )


def _coords_to_bbox(coords: object | None) -> BoundingBox | None:
    if coords is None:
        return None
    points = getattr(coords, "points", None)
    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return BoundingBox(x0=min(xs), y0=min(ys), x1=max(xs), y1=max(ys))
