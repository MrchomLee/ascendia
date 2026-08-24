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


_DOCLING_LABEL_MAP: dict[str, ElementKind] = {
    "title": ElementKind.TITLE,
    "section_header": ElementKind.HEADING,
    "section-header": ElementKind.HEADING,
    "text": ElementKind.NARRATIVE,
    "paragraph": ElementKind.NARRATIVE,
    "list_item": ElementKind.LIST_ITEM,
    "list-item": ElementKind.LIST_ITEM,
    "table": ElementKind.TABLE,
    "figure": ElementKind.FIGURE,
    "picture": ElementKind.FIGURE,
    "page_header": ElementKind.PAGE_HEADER,
    "page-header": ElementKind.PAGE_HEADER,
    "page_footer": ElementKind.PAGE_FOOTER,
    "page-footer": ElementKind.PAGE_FOOTER,
    "footnote": ElementKind.PAGE_FOOTER,
    "page_number": ElementKind.PAGE_NUMBER,
    "page-number": ElementKind.PAGE_NUMBER,
}


class DoclingAdapter(ExtractorBase):
    """Wraps Docling's DocumentConverter with conservative memory settings.

    Defaults are tuned for **PDFs with native extractable text** (the common
    case for born-digital manuals): OCR is OFF, the PDF's text layer is used
    directly, and internal queue/batch sizes are clipped so memory stays
    bounded. For scanned manuals, pass `do_ocr=True`.

    Why these defaults exist
    ------------------------
    Docling's default pipeline runs RapidOCR + layout model + table model on
    every page and queues up to 100 rendered page bitmaps in RAM. On long
    documents (~450 pages) that piles up several GB and triggers
    `std::bad_alloc` mid-run. Disabling OCR for digitally-extractable PDFs
    eliminates the dominant memory consumer with zero quality loss (we then
    rely on the PDF's text layer, which we already verified is clean).
    """

    name = "docling"

    def __init__(
        self,
        *,
        do_ocr: bool = False,
        do_table_structure: bool = True,
        table_mode_fast: bool = True,
        queue_max_size: int = 8,
        layout_batch_size: int = 2,
        table_batch_size: int = 2,
        ocr_batch_size: int = 2,
        ocr_languages: list[str] | None = None,
    ) -> None:
        self.do_ocr = do_ocr
        self.do_table_structure = do_table_structure
        self.table_mode_fast = table_mode_fast
        self.queue_max_size = queue_max_size
        self.layout_batch_size = layout_batch_size
        self.table_batch_size = table_batch_size
        self.ocr_batch_size = ocr_batch_size
        self.ocr_languages = ocr_languages or ["es"]

    def _build_converter(self):
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import (
            PdfPipelineOptions,
            TableFormerMode,
        )
        from docling.document_converter import DocumentConverter, PdfFormatOption

        opts = PdfPipelineOptions()
        opts.do_ocr = self.do_ocr
        opts.do_table_structure = self.do_table_structure
        if self.do_table_structure and self.table_mode_fast:
            opts.table_structure_options.mode = TableFormerMode.FAST

        opts.generate_page_images = False
        opts.generate_picture_images = False
        opts.generate_table_images = False
        opts.images_scale = 1.0

        if hasattr(opts, "force_backend_text"):
            opts.force_backend_text = not self.do_ocr

        if hasattr(opts, "queue_max_size"):
            opts.queue_max_size = self.queue_max_size
        if hasattr(opts, "layout_batch_size"):
            opts.layout_batch_size = self.layout_batch_size
        if hasattr(opts, "table_batch_size"):
            opts.table_batch_size = self.table_batch_size
        if hasattr(opts, "ocr_batch_size"):
            opts.ocr_batch_size = self.ocr_batch_size

        if self.do_ocr and hasattr(opts, "ocr_options"):
            opts.ocr_options.lang = self.ocr_languages

        return DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
        )

    def extract(self, pdf_path: Path) -> ExtractionResult:
        start = time.perf_counter()
        converter = self._build_converter()
        result = converter.convert(str(pdf_path))
        doc = result.document

        elements: list[RawElement] = []
        warnings: list[str] = []

        for item, _level in doc.iterate_items():
            label = getattr(item, "label", None)
            label_str = str(label).lower() if label else "other"
            kind = _DOCLING_LABEL_MAP.get(label_str, ElementKind.OTHER)

            text = (getattr(item, "text", "") or "").strip()
            
            # If the item has a marker, prepend it
            marker = getattr(item, "marker", None)
            if marker:
                marker_text = (getattr(marker, "text", str(marker)) or "").strip()
                if marker_text and not text.startswith(marker_text):
                    text = f"{marker_text} {text}".strip()

            if not text and kind not in (ElementKind.TABLE, ElementKind.FIGURE):
                continue

            page_no = _first_page(item)
            bbox = _first_bbox(item)

            elements.append(
                RawElement(
                    page_number=page_no or 0,
                    physical_page_index=(page_no - 1) if page_no else 0,
                    kind=kind,
                    text=text,
                    level=getattr(item, "level", None),
                    bbox=bbox,
                    metadata={
                        "docling_label": label_str,
                        "self_ref": getattr(item, "self_ref", None),
                    },
                )
            )

        elapsed = time.perf_counter() - start
        page_count = len(getattr(doc, "pages", {})) or 0

        return ExtractionResult(
            extractor_name=self.name,
            elements=elements,
            page_count=page_count,
            elapsed_seconds=elapsed,
            warnings=warnings,
        )


def _first_page(item: object) -> int | None:
    prov = getattr(item, "prov", None)
    if not prov:
        return None
    first = prov[0] if hasattr(prov, "__getitem__") else next(iter(prov), None)
    if first is None:
        return None
    return getattr(first, "page_no", None)


def _first_bbox(item: object) -> BoundingBox | None:
    prov = getattr(item, "prov", None)
    if not prov:
        return None
    first = prov[0] if hasattr(prov, "__getitem__") else next(iter(prov), None)
    if first is None:
        return None
    bbox = getattr(first, "bbox", None)
    if bbox is None:
        return None
    return BoundingBox(
        x0=getattr(bbox, "l", 0.0),
        y0=getattr(bbox, "t", 0.0),
        x1=getattr(bbox, "r", 0.0),
        y1=getattr(bbox, "b", 0.0),
    )
