from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ElementKind(StrEnum):
    TITLE = "title"
    HEADING = "heading"
    NARRATIVE = "narrative"
    LIST_ITEM = "list_item"
    TABLE = "table"
    FIGURE = "figure"
    PAGE_HEADER = "page_header"
    PAGE_FOOTER = "page_footer"
    PAGE_NUMBER = "page_number"
    OTHER = "other"


class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0


class RawElement(BaseModel):
    """One layout element extracted from a PDF page.

    Both Docling and Unstructured adapters normalize their output to this shape
    so the rest of the pipeline (hierarchy assembler, chunker) does not depend
    on which extractor was used.
    """

    page_number: int
    physical_page_index: int = Field(
        description="0-based index in the PDF (sequential), independent of "
        "printed page numbers (which may use roman numerals in prefaces)."
    )
    kind: ElementKind
    text: str
    level: int | None = Field(
        default=None,
        description="Heading depth as detected by the extractor (None if N/A).",
    )
    bbox: BoundingBox | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExtractionResult(BaseModel):
    extractor_name: str
    elements: list[RawElement]
    page_count: int
    elapsed_seconds: float
    warnings: list[str] = Field(default_factory=list)
