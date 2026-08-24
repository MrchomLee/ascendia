from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from etl.extraction.types import ExtractionResult


class ExtractorBase(ABC):
    """Common interface for layout extractors.

    Adapters (Docling, Unstructured, etc.) implement this so the rest of the
    pipeline can swap engines without code changes — critical for the bake-off.
    """

    name: str

    @abstractmethod
    def extract(self, pdf_path: Path) -> ExtractionResult:
        """Run the extractor on a PDF and return normalized elements."""
        raise NotImplementedError
