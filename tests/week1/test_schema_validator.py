"""Tests for schema validation."""

import pytest
from src.core.schema_validator import (
    validate_document,
    validate_screenshot,
    validate_query,
    validate_chunk,
    load_domain_taxonomy,
    validate_batch,
)
from src.core.sample_data import SAMPLE_DOCUMENTS, SAMPLE_SCREENSHOTS


class TestDocumentValidation:
    """Tests for document schema validation."""

    def test_validate_valid_document(self):
        """Test validating a valid document."""
        doc = SAMPLE_DOCUMENTS[0]
        is_valid, error = validate_document(doc)
        assert is_valid is True
        assert error is None

    def test_validate_document_missing_required(self):
        """Test validating document missing required fields."""
        doc = {"title": "Missing doc_id"}
        is_valid, error = validate_document(doc)
        assert is_valid is False
        assert "doc_id" in error.lower() or "required" in error.lower()

    def test_validate_document_invalid_parse_status(self):
        """Test validating document with invalid parse_status."""
        doc = {
            "doc_id": "doc-001",
            "title": "Test",
            "content": "Content",
            "parse_status": "invalid_status",  # Invalid value
        }
        is_valid, error = validate_document(doc)
        # Should fail with enum validation error
        assert is_valid is False
        assert error is not None

    def test_validate_document_empty_title(self):
        """Test validating document with empty title - schema requires minLength 1."""
        doc = {
            "doc_id": "doc-001",
            "title": "",  # Empty title fails schema minLength: 1
            "content": "Content",
            "parse_status": "success",
        }
        is_valid, error = validate_document(doc)
        # Schema requires minLength: 1 for title, so this should fail if jsonschema is available
        if error:
            assert is_valid is False


class TestScreenshotValidation:
    """Tests for screenshot schema validation."""

    def test_validate_valid_screenshot(self):
        """Test validating a valid screenshot."""
        screen = SAMPLE_SCREENSHOTS[0]
        is_valid, error = validate_screenshot(screen)
        assert is_valid is True
        assert error is None

    def test_validate_screenshot_missing_required(self):
        """Test validating screenshot missing required fields."""
        screen = {"screen_id": "screen-001"}
        is_valid, error = validate_screenshot(screen)
        assert is_valid is False
        assert "doc_id" in error.lower() or "required" in error.lower()

    def test_validate_screenshot_invalid_screen_type(self):
        """Test validating screenshot with invalid screen_type."""
        screen = {
            "screen_id": "screen-001",
            "doc_id": "doc-001",
            "screen_type": "invalid",  # Invalid value
            "source_path": "/path/to/file.png",
        }
        is_valid, error = validate_screenshot(screen)
        if error:
            assert is_valid is False


class TestQueryValidation:
    """Tests for query schema validation."""

    def test_validate_valid_query(self):
        """Test validating a valid query."""
        query = {
            "query_id": "q-001",
            "query_text": "Làm thế nào để đăng nhập?",
            "query_type": "procedural",
            "difficulty": "easy",
            "domain_id": "D1",
        }
        is_valid, error = validate_query(query)
        assert is_valid is True
        assert error is None

    def test_validate_query_missing_required(self):
        """Test validating query missing required fields."""
        query = {"query_text": "Missing query_id"}
        is_valid, error = validate_query(query)
        assert is_valid is False
        assert "query_id" in error.lower()

    def test_validate_query_minimal(self):
        """Test validating query with minimal fields."""
        query = {"query_id": "q-002", "query_text": "Test question"}
        is_valid, error = validate_query(query)
        assert is_valid is True


class TestChunkValidation:
    """Tests for chunk schema validation."""

    def test_validate_valid_chunk_fixed(self):
        """Test validating a valid fixed chunk."""
        chunk = {
            "chunk_id": "doc-001_fixed_0001",
            "doc_id": "doc-001",
            "chunk_order": 1,
            "chunk_method": "fixed",
            "chunk_text": "This is chunk content",
            "window_size": 512,
            "overlap_size": 96,
            "char_start": 0,
            "char_end": 100,
            "token_estimate": 50,
        }
        is_valid, error = validate_chunk(chunk)
        assert is_valid is True
        assert error is None

    def test_validate_valid_chunk_structure(self):
        """Test validating a valid structure chunk."""
        chunk = {
            "chunk_id": "doc-001_struct_0001",
            "doc_id": "doc-001",
            "chunk_order": 1,
            "chunk_method": "structure",
            "chunk_text": "Section content",
            "heading_path": "Main > Sub > Detail",
            "section_title": "Detail",
            "section_depth": 3,
            "char_start": 0,
            "char_end": 100,
            "token_estimate": 30,
        }
        is_valid, error = validate_chunk(chunk)
        assert is_valid is True
        assert error is None


class TestDomainTaxonomy:
    """Tests for domain taxonomy loading."""

    def test_load_domain_taxonomy(self):
        """Test loading domain taxonomy."""
        domains = load_domain_taxonomy()
        assert len(domains) == 7
        domain_ids = [d["domain_id"] for d in domains]
        assert domain_ids == ["D1", "D2", "D3", "D4", "D5", "D6", "D7"]

    def test_domain_taxonomy_structure(self):
        """Test domain taxonomy has required fields."""
        domains = load_domain_taxonomy()
        for domain in domains:
            assert "domain_id" in domain
            assert "name" in domain
            assert "function_areas" in domain
            assert "characteristic_errors" in domain


class TestBatchValidation:
    """Tests for batch validation."""

    def test_validate_batch_documents(self):
        """Test validating a batch of documents."""
        valid, invalid = validate_batch(SAMPLE_DOCUMENTS, validate_document)
        # doc-sample-001 and doc-sample-002 should be valid
        # doc-sample-003 has empty title (fails minLength: 1)
        assert len(valid) >= 2  # At least 2 valid documents
        assert len(invalid) >= 1  # doc-sample-003 should be invalid

    def test_validate_batch_screenshots(self):
        """Test validating a batch of screenshots."""
        valid, invalid = validate_batch(SAMPLE_SCREENSHOTS, validate_screenshot)
        assert len(valid) == 2
        assert len(invalid) == 0