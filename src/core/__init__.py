"""
Core module initialization.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class DocumentProcessor(Protocol):
    """Protocol for document processors."""

    def process(self, document: dict) -> dict:
        """Process a document and return processed result."""
        ...


@runtime_checkable
class Chunker(Protocol):
    """Protocol for text chunkers."""

    def chunk(self, text: str, **kwargs) -> list:
        """Chunk text into segments."""
        ...


@runtime_checkable
class QualityScorer(Protocol):
    """Protocol for quality scorers."""

    def score(self, document: dict) -> float:
        """Score document quality."""
        ...


from src.core.schema_validator import (  # noqa: E402
    validate_document,
    validate_screenshot,
    validate_query,
    validate_chunk,
    load_domain_taxonomy,
    validate_batch,
)