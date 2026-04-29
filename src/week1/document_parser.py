"""
Document parser for ingesting MD/PDF/DOCX files into the RAG pipeline.

Supports Markdown, PDF, and DOCX formats. Outputs documents conforming
to the document_metadata_schema.json.
"""

import json
import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _generate_doc_id(source_path: str) -> str:
    """Generate a doc_id from source file path."""
    stem = Path(source_path).stem
    clean = re.sub(r"[^a-zA-Z0-9_-]", "-", stem)
    return f"doc-{clean}"


def _extract_headings_from_markdown(text: str) -> list[dict]:
    """Extract headings from markdown text with levels."""
    headings = []
    for line in text.split("\n"):
        match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
        if match:
            level = len(match.group(1))
            text_val = match.group(2).strip()
            headings.append({"level": level, "text": text_val})
    return headings


def _extract_sections_from_markdown(text: str) -> list[dict]:
    """Extract sections from markdown text with heading paths."""
    sections = []
    current_path = []
    current_level = 0
    current_text_lines = []

    def _flush_section():
        if current_path and current_text_lines:
            section_text = "\n".join(current_text_lines).strip()
            if section_text:
                sections.append(
                    {
                        "heading_path": " > ".join(current_path),
                        "text": section_text,
                        "level": current_level,
                    }
                )

    for line in text.split("\n"):
        match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
        if match:
            _flush_section()
            level = len(match.group(1))
            heading_text = match.group(2).strip()
            current_path = current_path[: level - 1]
            current_path.append(heading_text)
            current_level = level
            current_text_lines = []
        else:
            current_text_lines.append(line)

    _flush_section()
    return sections


class BaseParser(ABC):
    """Abstract base class for document parsers."""

    @abstractmethod
    def parse(self, source_path: str, **kwargs) -> dict:
        """Parse a document and return document metadata dict."""
        ...

    def _build_document(
        self,
        doc_id: str,
        title: str,
        content: str,
        source_type: str,
        source_path: str,
        headings: list[dict] | None = None,
        sections: list[dict] | None = None,
        parse_status: str = "success",
        **extra_fields,
    ) -> dict:
        """Build a document metadata dict conforming to schema."""
        now = datetime.now(timezone.utc).isoformat()
        doc = {
            "doc_id": doc_id,
            "title": title,
            "source_type": source_type,
            "source_path": source_path,
            "parse_status": parse_status,
            "content": content,
            "headings": headings or [],
            "sections": sections or [],
            "created_at": now,
            "updated_at": now,
        }
        doc.update(extra_fields)
        return doc


class MarkdownParser(BaseParser):
    """Parser for Markdown (.md) files."""

    def parse(self, source_path: str, **kwargs) -> dict:
        """Parse a Markdown file into document metadata."""
        path = Path(source_path)
        doc_id = kwargs.get("doc_id") or _generate_doc_id(source_path)

        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read markdown file {source_path}: {e}")
            return self._build_document(
                doc_id=doc_id,
                title="",
                content="",
                source_type="md",
                source_path=source_path,
                parse_status="failed",
            )

        headings = _extract_headings_from_markdown(content)
        sections = _extract_sections_from_markdown(content)

        title = headings[0]["text"] if headings else path.stem

        # Strip heading lines from content for clean text
        clean_content = re.sub(r"^(#{1,6})\s+.+$", "", content, flags=re.MULTILINE)
        clean_content = re.sub(r"\n{3,}", "\n\n", clean_content).strip()

        return self._build_document(
            doc_id=doc_id,
            title=title,
            content=content,
            source_type="md",
            source_path=source_path,
            headings=headings,
            sections=sections,
            language=kwargs.get("language", "vi"),
            domain_id=kwargs.get("domain_id"),
            function_area=kwargs.get("function_area"),
        )


class PDFParser(BaseParser):
    """Parser for PDF files using PyPDF2 or pypdf."""

    def parse(self, source_path: str, **kwargs) -> dict:
        """Parse a PDF file into document metadata."""
        path = Path(source_path)
        doc_id = kwargs.get("doc_id") or _generate_doc_id(source_path)

        try:
            from pypdf import PdfReader

            reader = PdfReader(str(path))
            pages = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)

            content = "\n\n".join(pages)

            if not content.strip():
                logger.warning(f"PDF {source_path} yielded no text content")
                parse_status = "partial"
            else:
                parse_status = "success"

            headings = _extract_headings_from_markdown(content)
            sections = _extract_sections_from_markdown(content)
            title = headings[0]["text"] if headings else path.stem

            return self._build_document(
                doc_id=doc_id,
                title=title,
                content=content,
                source_type="pdf",
                source_path=source_path,
                headings=headings,
                sections=sections,
                parse_status=parse_status,
                language=kwargs.get("language", "vi"),
                domain_id=kwargs.get("domain_id"),
                function_area=kwargs.get("function_area"),
            )

        except ImportError:
            logger.error("pypdf not available. Install with: pip install pypdf")
            return self._build_document(
                doc_id=doc_id,
                title="",
                content="",
                source_type="pdf",
                source_path=source_path,
                parse_status="failed",
            )
        except Exception as e:
            logger.error(f"Failed to parse PDF {source_path}: {e}")
            return self._build_document(
                doc_id=doc_id,
                title="",
                content="",
                source_type="pdf",
                source_path=source_path,
                parse_status="failed",
            )


class DOCXParser(BaseParser):
    """Parser for DOCX files using python-docx."""

    def parse(self, source_path: str, **kwargs) -> dict:
        """Parse a DOCX file into document metadata."""
        path = Path(source_path)
        doc_id = kwargs.get("doc_id") or _generate_doc_id(source_path)

        try:
            import docx

            doc = docx.Document(str(path))

            # Extract paragraphs
            paragraphs = []
            headings = []
            for para in doc.paragraphs:
                text = para.text.strip()
                if not text:
                    continue

                # Check if paragraph is a heading
                if para.style and para.style.name and para.style.name.startswith("Heading"):
                    try:
                        level = int(para.style.name.replace("Heading ", "").replace("Heading", "1"))
                    except ValueError:
                        level = 1
                    headings.append({"level": level, "text": text})

                paragraphs.append(text)

            content = "\n\n".join(paragraphs)
            sections = _extract_sections_from_text(paragraphs, headings)
            title = headings[0]["text"] if headings else path.stem

            if not content.strip():
                logger.warning(f"DOCX {source_path} yielded no text content")
                parse_status = "partial"
            else:
                parse_status = "success"

            return self._build_document(
                doc_id=doc_id,
                title=title,
                content=content,
                source_type="docx",
                source_path=source_path,
                headings=headings,
                sections=sections,
                parse_status=parse_status,
                language=kwargs.get("language", "vi"),
                domain_id=kwargs.get("domain_id"),
                function_area=kwargs.get("function_area"),
            )

        except ImportError:
            logger.error("python-docx not available. Install with: pip install python-docx")
            return self._build_document(
                doc_id=doc_id,
                title="",
                content="",
                source_type="docx",
                source_path=source_path,
                parse_status="failed",
            )
        except Exception as e:
            logger.error(f"Failed to parse DOCX {source_path}: {e}")
            return self._build_document(
                doc_id=doc_id,
                title="",
                content="",
                source_type="docx",
                source_path=source_path,
                parse_status="failed",
            )


def _extract_sections_from_text(
    paragraphs: list[str], headings: list[dict]
) -> list[dict]:
    """Extract sections from paragraphs using heading boundaries."""
    if not headings:
        return []

    sections = []
    heading_texts = {h["text"] for h in headings}
    current_path = []
    current_level = 0
    current_text_lines = []

    def _flush():
        if current_path and current_text_lines:
            text = "\n".join(current_text_lines).strip()
            if text:
                sections.append(
                    {
                        "heading_path": " > ".join(current_path),
                        "text": text,
                        "level": current_level,
                    }
                )

    heading_map = {h["text"]: h["level"] for h in headings}

    for para in paragraphs:
        if para in heading_map:
            _flush()
            level = heading_map[para]
            current_path = current_path[: level - 1]
            current_path.append(para)
            current_level = level
            current_text_lines = []
        else:
            current_text_lines.append(para)

    _flush()
    return sections


# Parser registry
PARSERS = {
    ".md": MarkdownParser,
    ".markdown": MarkdownParser,
    ".pdf": PDFParser,
    ".docx": DOCXParser,
}


def get_parser(file_path: str) -> Optional[BaseParser]:
    """Get the appropriate parser for a file based on extension."""
    ext = Path(file_path).suffix.lower()
    parser_class = PARSERS.get(ext)
    if parser_class:
        return parser_class()
    logger.warning(f"No parser available for extension: {ext}")
    return None


def parse_file(source_path: str, **kwargs) -> dict:
    """Parse a single file and return document metadata."""
    parser = get_parser(source_path)
    if parser:
        return parser.parse(source_path, **kwargs)
    return {
        "doc_id": _generate_doc_id(source_path),
        "title": "",
        "source_type": Path(source_path).suffix.lstrip("."),
        "source_path": source_path,
        "parse_status": "failed",
        "content": "",
        "headings": [],
        "sections": [],
    }


def parse_directory(directory: str, pattern: str = "**/*") -> list[dict]:
    """Parse all supported files in a directory.

    Returns list of document metadata dicts.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        logger.error(f"Directory not found: {directory}")
        return []

    documents = []
    for file_path in dir_path.glob(pattern):
        if file_path.suffix.lower() in PARSERS:
            logger.info(f"Parsing: {file_path}")
            doc = parse_file(str(file_path))
            documents.append(doc)

    logger.info(f"Parsed {len(documents)} documents from {directory}")
    return documents


def write_jsonl(documents: list[dict], output_path: str) -> str:
    """Write documents to JSONL file. Returns output path."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        for doc in documents:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    logger.info(f"Wrote {len(documents)} documents to {output_path}")
    return str(output)


def read_jsonl(file_path: str) -> list[dict]:
    """Read documents from JSONL file."""
    documents = []
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                documents.append(json.loads(line))
    return documents


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Parse documents into JSONL")
    parser.add_argument("--input", required=True, help="Input file or directory")
    parser.add_argument("--output", default="data/documents/processed/docs.jsonl", help="Output JSONL path")
    parser.add_argument("--pattern", default="**/*", help="Glob pattern for directory mode")
    args = parser.parse_args()

    input_path = Path(args.input)
    if input_path.is_file():
        docs = [parse_file(str(input_path))]
    elif input_path.is_dir():
        docs = parse_directory(str(input_path), args.pattern)
    else:
        logger.error(f"Input not found: {args.input}")
        exit(1)

    write_jsonl(docs, args.output)
    print(f"Parsed {len(docs)} documents → {args.output}")
