"""Tests for document parser."""

import json
import tempfile
from pathlib import Path

import pytest

from src.week1.document_parser import (
    MarkdownParser,
    PDFParser,
    DOCXParser,
    parse_file,
    parse_directory,
    write_jsonl,
    read_jsonl,
    get_parser,
    _generate_doc_id,
    _extract_headings_from_markdown,
    _extract_sections_from_markdown,
)


@pytest.fixture
def tmp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def sample_md(tmp_dir):
    """Create a sample markdown file."""
    content = """# Hướng dẫn đăng nhập

## Giới thiệu
Tài liệu hướng dẫn đăng nhập hệ thống.

## Yêu cầu
- Tài khoản hợp lệ
- Mật khẩu đúng

### Chi tiết
Nội dung chi tiết về yêu cầu.
"""
    path = tmp_dir / "login_guide.md"
    path.write_text(content, encoding="utf-8")
    return str(path)


class TestMarkdownParser:
    """Tests for MarkdownParser."""

    def test_parse_valid_markdown(self, sample_md):
        """Test parsing a valid markdown file."""
        parser = MarkdownParser()
        doc = parser.parse(sample_md)

        assert doc["parse_status"] == "success"
        assert doc["source_type"] == "md"
        assert doc["title"] == "Hướng dẫn đăng nhập"
        assert len(doc["headings"]) == 4
        assert doc["headings"][0] == {"level": 1, "text": "Hướng dẫn đăng nhập"}
        assert doc["headings"][1] == {"level": 2, "text": "Giới thiệu"}

    def test_parse_markdown_sections(self, sample_md):
        """Test that sections are extracted correctly."""
        parser = MarkdownParser()
        doc = parser.parse(sample_md)

        assert len(doc["sections"]) > 0
        assert "heading_path" in doc["sections"][0]
        assert doc["sections"][0]["level"] == 2

    def test_parse_markdown_content(self, sample_md):
        """Test that content is preserved."""
        parser = MarkdownParser()
        doc = parser.parse(sample_md)

        assert "đăng nhập" in doc["content"].lower()
        assert len(doc["content"]) > 50

    def test_parse_markdown_with_kwargs(self, sample_md):
        """Test parsing with additional metadata."""
        parser = MarkdownParser()
        doc = parser.parse(
            sample_md, domain_id="D1", function_area="login", language="vi"
        )

        assert doc["domain_id"] == "D1"
        assert doc["function_area"] == "login"
        assert doc["language"] == "vi"

    def test_parse_nonexistent_file(self):
        """Test parsing a file that doesn't exist."""
        parser = MarkdownParser()
        doc = parser.parse("/nonexistent/path.md")

        assert doc["parse_status"] == "failed"
        assert doc["source_type"] == "md"

    def test_parse_empty_markdown(self, tmp_dir):
        """Test parsing an empty markdown file."""
        path = tmp_dir / "empty.md"
        path.write_text("", encoding="utf-8")
        parser = MarkdownParser()
        doc = parser.parse(str(path))

        assert doc["parse_status"] == "success"
        assert doc["title"] == "empty"  # Uses filename as title
        assert doc["headings"] == []


class TestPDFParser:
    """Tests for PDFParser."""

    def test_parse_nonexistent_pdf(self):
        """Test parsing a PDF that doesn't exist."""
        parser = PDFParser()
        doc = parser.parse("/nonexistent/doc.pdf")

        assert doc["parse_status"] == "failed"
        assert doc["source_type"] == "pdf"


class TestDOCXParser:
    """Tests for DOCXParser."""

    def test_parse_nonexistent_docx(self):
        """Test parsing a DOCX that doesn't exist."""
        parser = DOCXParser()
        doc = parser.parse("/nonexistent/doc.docx")

        assert doc["parse_status"] == "failed"
        assert doc["source_type"] == "docx"


class TestHelpers:
    """Tests for helper functions."""

    def test_generate_doc_id(self):
        """Test doc_id generation from path."""
        doc_id = _generate_doc_id("path/to/login_guide.md")
        # Underscores are kept, only non-alphanumeric chars (except _) are replaced
        assert doc_id == "doc-login_guide"

    def test_generate_doc_id_special_chars(self):
        """Test doc_id generation with special characters."""
        doc_id = _generate_doc_id("path/to/Hướng dẫn.md")
        assert doc_id.startswith("doc-")
        assert len(doc_id) > 4

    def test_extract_headings(self):
        """Test heading extraction from markdown text."""
        text = "# Title\n## Subtitle\n### Sub-subtitle\nContent"
        headings = _extract_headings_from_markdown(text)
        assert len(headings) == 3
        assert headings[0]["level"] == 1
        assert headings[0]["text"] == "Title"

    def test_extract_sections(self):
        """Test section extraction from markdown text."""
        text = "# Title\n\nSection 1 content\n\n## Sub\n\nSub content"
        sections = _extract_sections_from_markdown(text)
        assert len(sections) >= 1
        assert "Title" in sections[0]["heading_path"]

    def test_extract_sections_empty(self):
        """Test section extraction from text without headings."""
        text = "Just some text\nwithout any headings"
        sections = _extract_sections_from_markdown(text)
        assert sections == []


class TestParseFunctions:
    """Tests for parse_file, parse_directory, JSONL I/O."""

    def test_parse_file_markdown(self, sample_md):
        """Test parse_file with a markdown file."""
        doc = parse_file(sample_md)
        assert doc["parse_status"] == "success"

    def test_parse_file_unsupported(self, tmp_dir):
        """Test parse_file with unsupported file type."""
        path = tmp_dir / "file.xyz"
        path.write_text("content", encoding="utf-8")
        doc = parse_file(str(path))
        assert doc["parse_status"] == "failed"

    def test_parse_directory(self, tmp_dir):
        """Test parsing all files in a directory."""
        (tmp_dir / "doc1.md").write_text("# Doc 1\nContent 1", encoding="utf-8")
        (tmp_dir / "doc2.md").write_text("# Doc 2\nContent 2", encoding="utf-8")
        (tmp_dir / "ignored.txt").write_text("ignored", encoding="utf-8")

        docs = parse_directory(str(tmp_dir))
        assert len(docs) == 2
        assert all(d["parse_status"] == "success" for d in docs)

    def test_parse_directory_nonexistent(self):
        """Test parsing a nonexistent directory."""
        docs = parse_directory("/nonexistent/dir")
        assert docs == []

    def test_get_parser(self):
        """Test getting parser by extension."""
        assert isinstance(get_parser("test.md"), MarkdownParser)
        assert isinstance(get_parser("test.pdf"), PDFParser)
        assert isinstance(get_parser("test.docx"), DOCXParser)
        assert get_parser("test.xyz") is None

    def test_write_and_read_jsonl(self, tmp_dir, sample_md):
        """Test JSONL write and read round-trip."""
        docs = [parse_file(sample_md)]
        output_path = str(tmp_dir / "output.jsonl")

        write_jsonl(docs, output_path)
        assert Path(output_path).exists()

        loaded = read_jsonl(output_path)
        assert len(loaded) == 1
        assert loaded[0]["doc_id"] == docs[0]["doc_id"]
        assert loaded[0]["title"] == docs[0]["title"]

    def test_write_jsonl_creates_dirs(self, tmp_dir):
        """Test that write_jsonl creates parent directories."""
        output_path = str(tmp_dir / "sub" / "dir" / "docs.jsonl")
        write_jsonl([{"test": "data"}], output_path)
        assert Path(output_path).exists()
